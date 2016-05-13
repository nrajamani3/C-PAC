# CPAC/pipeline/workflow_bundler.py
#

'''
Module containing the prototype workflow bundler for a C-PAC pipeline
'''

# Import packages
from multiprocessing import Process, Pool, cpu_count, pool
from traceback import format_exception
import os
import sys

import numpy as np
from copy import deepcopy
from nipype.pipeline.engine import MapNode
from nipype.utils.misc import str2bool
from nipype import logging
from nipype.pipeline.plugins import semaphore_singleton
from nipype.pipeline.plugins.base import (DistributedPluginBase, report_crash)
from nipype.pipeline.plugins.multiproc \
    import get_system_total_memory_gb, NonDaemonPool, run_node, release_lock

# Init logger
logger = logging.getLogger('workflow')
from nipype import config
config.enable_debug_mode()
logging.update_logging(config)


def create_cpac_arg_list(sublist_filepath, config_filepath):
    '''
    Function to create a list of arguments to feed to prep_workflow
    '''

    # Import packages
    import yaml
    from CPAC.utils.configuration import Configuration

    # Init variables
    args_list = []
    sublist = yaml.load(open(sublist_filepath, 'r'))
    with open(config_filepath, 'r') as cfg:
        pipeline_config = yaml.load(cfg)
        config = Configuration(pipeline_config)

    # Create args list
    for sub_dict in sublist:
        args = ((sub_dict, config), {})
        args_list.append(args)

    # Return args list
    return args_list


class BundlerMetaPlugin(object):
    '''
    '''

    def __init__(self, plugin_args, plugin='MultiProc'):
        '''
        Init method
        '''

        # Init variables and instance attributes
        #super(BundlerMetaPlugin, self).__init__(plugin_args=plugin_args)

        # Get and init to system resources
        total_cores = cpu_count()
        total_memory_gb = get_system_total_memory_gb()

        # Check for mandatory arguments in plugin args
        if not plugin_args or not (plugin_args.has_key('function_handle') \
                                   and plugin_args.has_key('args_list')):
            err_msg = 'The "function_handle" and "args_list" keys in the '\
                      'plugin_args must be provided for bundler to execute!'
            raise Exception(err_msg)

        # Get mandatory plugin arguments
        self.function_handle = plugin_args['function_handle']
        self.pending_wfs = plugin_args['args_list']
        self.plugin = plugin

        # Optional plugin arguments
        # Daemon job submissions
        if plugin_args.has_key('non_daemon'):
            self.non_daemon = plugin_args['non_daemon']
        else:
            self.non_daemon = True
        # Thread limits
        if plugin_args.has_key('n_procs'):
            if plugin_args['n_procs'] <= cpu_count():
                self.processors = plugin_args['n_procs']
            else:
                msg = 'plugin_args["n_procs"]: %d is greater than the '\
                      'available system cores: %d\nSetting processors '\
                      'limit to: %d' % (plugin_args['n_procs'],
                                        total_cores, total_cores)
                logger.info(msg)
        else:
            self.processors = total_cores # Use all cores
        # Memory limits
        if plugin_args.has_key('memory_gb'):
            if plugin_args['memory_gb'] <= total_memory_gb:
                self.memory_gb = plugin_args['memory_gb']
            else:
                msg = 'plugin_args["memory_gb"]: %.3f is greater than the '\
                      'available system memory: %.3f\nSetting memory '\
                      'limit to: %.3f' % (plugin_args['memory_gb'],
                                          total_memory_gb, total_memory_gb)
                logger.info(msg)
        else:
            self.memory_gb = get_system_total_memory_gb()*0.9 # 90% of system memory
        # Status callback
        if plugin_args.has_key('status_callback'):
            self.status_callback = plugin_args['status_callback']
        else:
            self.status_callback = None
        # Max workflows in parallel
        if plugin_args.has_key('max_parallel'):
            self.max_parallel = plugin_args['max_parallel']
        else:
            self.max_parallel = self.processors//2

    def _update_queues_and_resources(self):
        '''
        Function to update the pending and running queues as well as to
        calculate and return available resources and nodes to run 
        '''

        # Init variables
        self.free_memory_gb = self.memory_gb
        self.free_procs = self.processors
        self.available_nodes = []

        # First clean out runners that are finished
        for runner in self.running_wfs:
            all_procs_submitted = (runner.proc_done == True).all()
            no_procs_pending = (runner.proc_pending == False).all()
            if all_procs_submitted and no_procs_pending:
                logger.debug('Removing runner %s from running queue...' % str(runner))
                self.running_wfs.remove(runner)
                # Workflow level clean-up
                wflow, execgraph = self.runner_graph_dict[runner]
                wflow._post_run(execgraph)
                # Runner level clean-up
                runner._remove_node_dirs()
            else:
                busy_jids = np.flatnonzero((runner.proc_pending == True) & \
                            (runner.depidx.sum(axis=0) == 0).__array__())
                logger.debug('Runner %s is still busy with %d running jobs' % (str(runner), len(busy_jids)))
                for jid in busy_jids:
                    node = runner.procs[jid]
                    logger.debug('node: %s, %d is running...' % (node.name, node._id))
                    self.free_memory_gb -= node._interface.estimated_memory_gb
                    self.free_procs -= node._interface.num_threads
                    logger.debug('free memory: %.3f, free procs: %d' % (self.free_memory_gb, self.free_procs))

        # If there is available resources and pending workflows
        # add workflow to running queue
        if self.free_memory_gb > 0 and self.free_procs > 0 and \
           len(self.pending_wfs) > 0 and len(self.running_wfs) < self.max_parallel:
            logger.debug('Pop a new workflow from stack and init!')
            args, kwargs = self.pending_wfs.pop()
            wflow = self.function_handle(*args, **kwargs)
            runner, execgraph = wflow._prep(self.plugin)
            self.runner_graph_dict[runner] = (wflow, execgraph)
            # Configure runner plugin
            if self.non_daemon:
                runner.pool = NonDaemonPool(processes=self.processors)
            else:
                runner.pool = Pool(processes=self.processors)
            runner._status_callback = self.status_callback
            runner._taskresult = {}
            runner._taskid = 0
            runner._config = wflow.config
            runner._generate_dependency_list(execgraph)
            # runner.run() base inits
            runner.pending_tasks = []
            runner.readytorun = []
            runner.mapnodes = []
            runner.mapnodesubids = {}
            self.running_wfs.append(runner)

        # Build a list of (runner, id) tuples of available nodes from
        # running_wf queue
        for runner in self.running_wfs:
            logger.debug('Now %d runners in running queue' % len(self.running_wfs))
            # Check to see if a job is available
            jobids = np.flatnonzero((runner.proc_done == False) & \
                                    (runner.depidx.sum(axis=0) == 0).__array__())
            id_tuples = [(runner, jid) for jid in jobids]
            self.available_nodes.extend(id_tuples)

        # Sort jobs ready to run first by memory and then by number of threads
        # The most resource consuming jobs run first (x[0] - runner, x[1] - jobid)
        self.available_nodes.sort(key=lambda x: \
                             (x[0].procs[x[1]]._interface.estimated_memory_gb,
                              x[0].procs[x[1]]._interface.num_threads),
                             reverse=True)
        logger.debug('Now %d available nodes for execution' % len(self.available_nodes))

        # Return available resources
        #return available_nodes

    def _send_procs_to_workers(self, runner, jobid, updatehash=False):
        '''
        '''

        # Init node variables for clarity
        node = runner.procs[jobid]
        node_threads_est = node._interface.num_threads
        node_mem_gb_est = node._interface.estimated_memory_gb

        # Check to make sure node estimated resources aren't greater
        # than what we have
        if node_threads_est > self.processors or node_mem_gb_est > self.memory_gb:
            err_msg = 'Estimated node resources:\nnum_threads: %d, '\
                      'estimated_memory_gb: %.3f are greater than '\
                      'available:\nnum_threads: %d, estimated_memory_gb: %.3f' \
                      % (node_threads_est, node_mem_gb_est,
                         self.processors, self.memory_gb)
            raise Exception(err_msg)

        # If node estimated resources are less than what is free,
        # try and submit the node for run
        logger.debug('free memory: %.3f, free procs: %d' % (self.free_memory_gb, self.free_procs))
        if node_threads_est <= self.free_procs and \
           node_mem_gb_est <= self.free_memory_gb:
            logger.info('Executing: %s ID: %d' %(node._id, jobid))

            # Submit MapNode
            if isinstance(node, MapNode):
                try:
                    num_subnodes = node.num_subnodes()
                except Exception:
                    # Get the workflow graph
                    graph = self.runner_graph_dict[runner][1]
                    etype, eval, etr = sys.exc_info()
                    traceback = format_exception(etype, eval, etr)
                    report_crash(self.procs[jobid], traceback=traceback)
                    runner._clean_queue(jobid, graph)
                    runner.proc_pending[jobid] = False
                    return
                if num_subnodes > 1:
                    submit = runner._submit_mapnode(jobid)
                    if not submit:
                        return

            # Change job status in appropriate queues
            runner.proc_done[jobid] = True
            runner.proc_pending[jobid] = True
            self.free_procs -= node_threads_est
            self.free_memory_gb -= node_mem_gb_est

            # Send job to task manager and add to pending tasks
            if runner._status_callback:
                runner._status_callback(node, 'start')
            if str2bool(node.config['execution']['local_hash_check']):
                logger.debug('checking hash locally')
                try:
                    hash_exists, _, _, _ = node.hash_exists()
                    logger.debug('Hash exists %s' % str(hash_exists))
                    if (hash_exists and (node.overwrite == False or \
                                         (node.overwrite == None and \
                                          not node._interface.always_run))):
                        runner._task_finished_cb(jobid)
                        runner._remove_node_dirs()
                        return
                except Exception:
                    # Get the workflow graph
                    graph = self.runner_graph_dict[runner][1]
                    etype, eval, etr = sys.exc_info()
                    traceback = format_exception(etype, eval, etr)
                    report_crash(runner.procs[jobid], traceback=traceback)
                    runner._clean_queue(jobid, graph)
                    runner.proc_pending[jobid] = False
                    return

            logger.debug('Finished checking hash')

            if node.run_without_submitting:
                logger.debug('Running node %s on master thread' \
                             % node.name)
                try:
                    node.run()
                except Exception:
                    etype, eval, etr = sys.exc_info()
                    traceback = format_exception(etype, eval, etr)
                    report_crash(node, traceback=traceback)
                runner._task_finished_cb(jobid)
                runner._remove_node_dirs()
            else:
                logger.debug('submitting %s' % str(jobid))
                tid = runner._submit_job(deepcopy(node), updatehash=updatehash)
                if tid is None:
                    runner.proc_done[jobid] = False
                    runner.proc_pending[jobid] = False
                else:
                    runner.pending_tasks.insert(0, (tid, jobid))

    logger.debug('No jobs waiting to execute')

    def run(self, updatehash=False):
        '''
        Run workflows
        '''

        # Import packages
        import copy
        import time
        import traceback
        import numpy as np
        from nipype.pipeline.plugins.base import report_nodes_not_run

        # Init workflow queue
        self.running_wfs = []
        self.runner_graph_dict = {}
        notrun = []

        # While there are workflows running or pending
        while len(self.running_wfs) > 0 or len(self.pending_wfs) > 0:
            logger.debug('before update: running wfs: %d, pending wfs: %d' % (len(self.running_wfs), len(self.pending_wfs)))
            # Update queues and get available resources
            self._update_queues_and_resources()
            logger.debug('after update: running wfs: %d, pending wfs: %d' % (len(self.running_wfs), len(self.pending_wfs)))

            # Iterate through the available nodes and submit jobs
            for runner, jobid in self.available_nodes:
                num_jobs = len(runner.pending_tasks)
                logger.debug('Number of pending tasks: %d' % num_jobs)
                if num_jobs < runner.max_jobs:
                    self._send_procs_to_workers(runner, jobid, updatehash)
                else:
                    logger.debug('Not submitting')

            for runner in self.running_wfs:
                
                toappend = []
                # Get the workflow graph
                graph = self.runner_graph_dict[runner][1]
                logger.debug('checking pending tasks for %s, pending: %d' % (str(runner), len(runner.pending_tasks)))
                # trigger callbacks for any pending results
                while runner.pending_tasks:
                    taskid, jobid = runner.pending_tasks.pop()
                    logger.debug('pending task: %d, %d for runner: %s' % (taskid, jobid, str(runner)))
                    try:
                        result = runner._get_result(taskid)
                        if result:
                            if result['traceback']:
                                notrun.append(runner._clean_queue(jobid, graph,
                                                                result=result))
                            else:
                                runner._task_finished_cb(jobid)
                                runner._remove_node_dirs()
                            runner._clear_task(taskid)
                        else:
                            toappend.insert(0, (taskid, jobid))
                    except Exception:
                        result = {'result': None,
                                  'traceback': traceback.format_exc()}
                        notrun.append(runner._clean_queue(jobid, graph,
                                                          result=result))

                if toappend:
                    runner.pending_tasks.extend(toappend)
                runner._wait()

        report_nodes_not_run(notrun)
