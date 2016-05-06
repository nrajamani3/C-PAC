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
        args = ((sub_dict, config),)
        args_list.append(args)

    # Return args list
    return args_list


class BundlerMetaPlugin(DistributedPluginBase):
    """Execute workflow with multiprocessing, not sending more jobs at once
    than the system can support.

    The plugin_args input to run can be used to control the multiprocessing
    execution and defining the maximum amount of memory and threads that 
    should be used. When those parameters are not specified,
    the number of threads and memory of the system is used.

    System consuming nodes should be tagged:
    memory_consuming_node.interface.estimated_memory_gb = 8
    thread_consuming_node.interface.num_threads = 16

    The default number of threads and memory for a node is 1. 

    Currently supported options are:

    - non_daemon : boolean flag to execute as non-daemon processes
    - n_procs: maximum number of threads to be executed in parallel
    - memory_gb: maximum memory (in GB) that can be used at once.

    """

    def __init__(self, plugin_args=None):
        '''
        Init method
        '''

        # Init variables and instance attributes
        super(BundlerMetaPlugin, self).__init__(plugin_args=plugin_args)
        self._taskresult = {}
        self._taskid = 0
        non_daemon = True
        self.plugin_args = plugin_args
        total_cores = cpu_count()
        total_memory_gb = get_system_total_memory_gb()
        self.processors = total_cores
        self.memory_gb = total_memory_gb*0.9 # 90% of system memory

        # Check plugin args
        if not self.plugin_args or not (plugin_args.has_key('function_handle') \
                                        and plugin_args.has_key('args_list')):
            err_msg = 'The "function_handle" and "args_list" keys in the '\
                      'plugin_args must be provided for bundler to execute!'
            raise Exception(err_msg)

        # Get plugin arguments
        self.function_handle = plugin_args['function_handle']
        self.pending_wfs = plugin_args['args_list']
        if 'non_daemon' in self.plugin_args:
            non_daemon = plugin_args['non_daemon']
        if 'n_procs' in self.plugin_args:
            if self.plugin_args['n_procs'] <= cpu_count():
                self.processors = self.plugin_args['n_procs']
            else:
                msg = 'plugin_args["n_procs"]: %d is greater than the '\
                      'available system cores: %d\nSetting processors '\
                      'limit to: %d' % (self.plugin_args['n_procs'],
                                        total_cores, total_cores)
                logger.info(msg)
        if 'memory_gb' in self.plugin_args:
            if self.plugin_args['memory_gb'] <= total_memory_gb:
                self.memory_gb = self.plugin_args['memory_gb']
            else:
                msg = 'plugin_args["memory_gb"]: %.3f is greater than the '\
                      'available system memory: %.3f\nSetting memory '\
                      'limit to: %.3f' % (self.plugin_args['memory_gb'],
                                         total_memory_gb, total_memory_gb)
                logger.info(msg)

        # Instantiate different thread pools for non-daemon processes
        if non_daemon:
            # run the execution using the non-daemon pool subclass
            self.pool = NonDaemonPool(processes=self.processors)
        else:
            self.pool = Pool(processes=self.processors)

    def run(self):
        '''
        Run workflows
        '''

        # Import packages
        import copy
        import time
        import numpy as np

        # Init workflow queue
        self.running_wfs = []
        self.available_procs = self.processors
        self.available_memory_gb = self.memory_gb

        # While there are workflows running or pending
        while not (self.running_wfs.is_empty() or self.pending_wfs.is_empty()):

            # First clean out runners that are finished
            for runner in self.running_wfs:
                if np.alltrue(runner.proc_done):
                    self.running_wfs.remove(runner)

            # If there is available resources and pending workflows
            # add workflow to running queue
            if self.available_memory_gb > 0 and self.available_procs > 0 and \
               not self.pending_wfs.is_empty():
                args, kwargs = self.args_list.pop()
                wflow = self.function_handle(*args, **kwargs)
                runner, execgraph = wflow._prep()
                runner._config = wflow.config
                runner._generate_dependency_list(execgraph)
                self.running_wfs.append(runner)

            # Build a list of (runner, id) tuples of available nodes from
            # running_wf queue
            available_nodes = []
            for runner in self.running_wfs:
                # Check to see if a job is available
                jobids = np.flatnonzero((runner.proc_done == False) & \
                                        (runner.depidx.sum(axis=0) == 0).__array__())
                id_tuples = [(runner, jid) for jid in jobids]
                available_nodes.extend(id_tuples)
    
            # Sort jobs ready to run first by memory and then by number of threads
            # The most resource consuming jobs run first (x[0] - runner, x[1] - jobid)
            available_nodes.sort(key=lambda x: \
                                 (x[0].procs[x[1]]._interface.estimated_memory_gb,
                                  x[0].procs[x[1]]._interface.num_threads),
                                 reverse=True)

            for runner, jobid in available_nodes:
                # If there are available resources
                node = runner.procs[jobid]
                node_threads_est = node._interface.num_threads
                node_mem_gb_est = node._interface.estimated_memory_gb
                # Check to make sure node estimated resources aren't greater
                # than what we have
                if node_threads_est > self.processors or \
                   node_mem_gb_est > self.estimated_memory_gb:
                    err_msg = 'Estimated node resources:\nnum_threads: %d, '\
                              'estimated_memory_gb: %.3f are greater than '\
                              'available:\nnum_threads: %d, estimated_memory_gb: %.3f' \
                              % (node_threads_est, node_mem_gb_est,
                                 self.processors, self.memory_gb)
                    raise Exception(err_msg)
                if node_threads_est <= self.available_procs and \
                   node_mem_gb_est <= self.available_memory_gb:
                    logger.info('Executing: %s ID: %d' %(node._id, jobid))
                    if isinstance(node, MapNode):
                        try:
                            num_subnodes = node.num_subnodes()
                        except Exception:
                            etype, eval, etr = sys.exc_info()
                            traceback = format_exception(etype, eval, etr)
                            report_crash(self.procs[jobid], traceback=traceback)
                            runner._clean_queue(jobid, graph)
                            runner.proc_pending[jobid] = False
                            continue
                        if num_subnodes > 1:
                            submit = runner._submit_mapnode(jobid)
                            if not submit:
                                continue
                    # change job status in appropriate queues
                    self.proc_done[jobid] = True
                    self.proc_pending[jobid] = True
                    self.available_procs -= node_threads_est
                    self.available_memory_gb -= node_mem_gb_est

                    # Send job to task manager and add to pending tasks
                    if self._status_callback:
                        self._status_callback(node, 'start')
                    if str2bool(node.config['execution']['local_hash_check']):
                        logger.debug('checking hash locally')
                        try:
                            hash_exists, _, _, _ = node.hash_exists()
                            logger.debug('Hash exists %s' % str(hash_exists))
                            if (hash_exists and (node.overwrite == False or \
                                                 (node.overwrite == None and \
                                                  not node._interface.always_run))):
                                self._task_finished_cb(jobid) # TODO: gotta look into this
                                runner._remove_node_dirs()
                                continue
                        except Exception:
                            etype, eval, etr = sys.exc_info()
                            traceback = format_exception(etype, eval, etr)
                            report_crash(self.procs[jobid], traceback=traceback)
                            runner._clean_queue(jobid, graph)
                            runner.proc_pending[jobid] = False
                            continue
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
                        self._task_finished_cb(jobid) # TODO: gotta look into this
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


    def _wait(self):
        if len(self.pending_tasks) > 0:
            semaphore_singleton.semaphore.acquire()
        semaphore_singleton.semaphore.release()

    def _get_result(self, taskid):
        if taskid not in self._taskresult:
            raise RuntimeError('Multiproc task %d not found' % taskid)
        if not self._taskresult[taskid].ready():
            return None
        return self._taskresult[taskid].get()

    def _report_crash(self, node, result=None):
        if result and result['traceback']:
            node._result = result['result']
            node._traceback = result['traceback']
            return report_crash(node,
                                traceback=result['traceback'])
        else:
            return report_crash(node)

    def _clear_task(self, taskid):
        del self._taskresult[taskid]

    def _submit_job(self, node, updatehash=False):
        self._taskid += 1
        if hasattr(node.inputs, 'terminal_output'):
            if node.inputs.terminal_output == 'stream':
                node.inputs.terminal_output = 'allatonce'

        self._taskresult[self._taskid] = \
            self.pool.apply_async(run_node,
                                  (node, updatehash),
                                  callback=release_lock)
        return self._taskid

    def _send_procs_to_workers(self, updatehash=False, graph=None):
        """ Sends jobs to workers when system resources are available.
            Check memory (gb) and cores usage before running jobs.
        """
        executing_now = []

        # Check to see if a job is available
        jobids = np.flatnonzero((self.proc_pending == True) & \
                                (self.depidx.sum(axis=0) == 0).__array__())

        # Check available system resources by summing all threads and memory used
        busy_memory_gb = 0
        busy_processors = 0
        for jobid in jobids:
            busy_memory_gb += self.procs[jobid]._interface.estimated_memory_gb
            busy_processors += self.procs[jobid]._interface.num_threads

        free_memory_gb = self.memory_gb - busy_memory_gb
        free_processors = self.processors - busy_processors

        # Check all jobs without dependency not run
        jobids = np.flatnonzero((self.proc_done == False) & \
                                (self.depidx.sum(axis=0) == 0).__array__())

        # Sort jobs ready to run first by memory and then by number of threads
        # The most resource consuming jobs run first
        jobids = sorted(jobids,
                        key=lambda item: (self.procs[item]._interface.estimated_memory_gb,
                                          self.procs[item]._interface.num_threads))

        logger.debug('Free memory (GB): %d, Free processors: %d',
                     free_memory_gb, free_processors)

        # While have enough memory and processors for first job
        # Submit first job on the list
        for jobid in jobids:
            logger.debug('Next Job: %d, memory (GB): %d, threads: %d' \
                         % (jobid, self.procs[jobid]._interface.estimated_memory_gb,
                            self.procs[jobid]._interface.num_threads))

            if self.procs[jobid]._interface.estimated_memory_gb <= free_memory_gb and \
               self.procs[jobid]._interface.num_threads <= free_processors:
                logger.info('Executing: %s ID: %d' %(self.procs[jobid]._id, jobid))
                executing_now.append(self.procs[jobid])

                if isinstance(self.procs[jobid], MapNode):
                    try:
                        num_subnodes = self.procs[jobid].num_subnodes()
                    except Exception:
                        etype, eval, etr = sys.exc_info()
                        traceback = format_exception(etype, eval, etr)
                        report_crash(self.procs[jobid], traceback=traceback)
                        self._clean_queue(jobid, graph)
                        self.proc_pending[jobid] = False
                        continue
                    if num_subnodes > 1:
                        submit = self._submit_mapnode(jobid)
                        if not submit:
                            continue

                # change job status in appropriate queues
                self.proc_done[jobid] = True
                self.proc_pending[jobid] = True

                free_memory_gb -= self.procs[jobid]._interface.estimated_memory_gb
                free_processors -= self.procs[jobid]._interface.num_threads

                # Send job to task manager and add to pending tasks
                if self._status_callback:
                    self._status_callback(self.procs[jobid], 'start')
                if str2bool(self.procs[jobid].config['execution']['local_hash_check']):
                    logger.debug('checking hash locally')
                    try:
                        hash_exists, _, _, _ = self.procs[
                            jobid].hash_exists()
                        logger.debug('Hash exists %s' % str(hash_exists))
                        if (hash_exists and (self.procs[jobid].overwrite == False or \
                                             (self.procs[jobid].overwrite == None and \
                                              not self.procs[jobid]._interface.always_run))):
                            self._task_finished_cb(jobid)
                            self._remove_node_dirs()
                            continue
                    except Exception:
                        etype, eval, etr = sys.exc_info()
                        traceback = format_exception(etype, eval, etr)
                        report_crash(self.procs[jobid], traceback=traceback)
                        self._clean_queue(jobid, graph)
                        self.proc_pending[jobid] = False
                        continue
                logger.debug('Finished checking hash')

                if self.procs[jobid].run_without_submitting:
                    logger.debug('Running node %s on master thread' \
                                 % self.procs[jobid])
                    try:
                        self.procs[jobid].run()
                    except Exception:
                        etype, eval, etr = sys.exc_info()
                        traceback = format_exception(etype, eval, etr)
                        report_crash(self.procs[jobid], traceback=traceback)
                    self._task_finished_cb(jobid)
                    self._remove_node_dirs()

                else:
                    logger.debug('submitting %s' % str(jobid))
                    tid = self._submit_job(deepcopy(self.procs[jobid]),
                                           updatehash=updatehash)
                    if tid is None:
                        self.proc_done[jobid] = False
                        self.proc_pending[jobid] = False
                    else:
                        self.pending_tasks.insert(0, (tid, jobid))
            else:
                break

        logger.debug('No jobs waiting to execute')
