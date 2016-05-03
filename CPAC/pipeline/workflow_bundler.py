# CPAC/pipeline/workflow_bundler.py
#

'''
Module containing the prototype workflow bundler for a C-PAC pipeline
'''

class WorkflowBundler(object):
    '''
    Class that contains a list of workflows and available resources to
    manage and schedule each and all of the workflow executions
    '''

    def __init__(self, wflows=[], num_threads=None, memory_gb=None):
        '''
        Method to instantiate a new WorkflowBundler object

        Parameters
        ----------
        self : WorkflowBundler
            self-inheritence
        wflows : list (optional); default=[]
            a list of workflows to monitor, schedule, and execute
        num_threads : int (optional); default=system CPUs
            specify the number of threads the bundler can use on the
            system; if not specified, the total number of CPUs on the
            system will be assumed
        memory_gb : float (optional); default=90% of system
            specify the amount of RAM (GB) the bundler can use on the
            system; if not specified, 90% of system memory will be used
        '''

        # Import packages
        import multiprocessing
        from nipype.pipeline.plugins.multiproc import get_system_total_memory_gb

        # Default args
        if num_threads is None:
            num_threads = multiprocessing.cpu_count()
        else:
            num_threads = int(num_threads)
        if memory_gb is None:
            memory_gb = 0.9*get_system_total_memory_gb()
        else:
            memory_gb = float(memory_gb)

        # Init variables
        self.wflows = wflows
        self.num_threads = num_threads
        self.memory_gb = memory_gb

    def _check_run_args(self):
        '''
        Check the arguments provided in the __init__ method
        '''

        # Import packages
        import nipype.pipeline.engine as pe
        from nipype.pipeline.plugins.multiproc import get_system_total_memory_gb
        import multiprocessing

        # Init variables
        wflows = self.wflows
        plugin = self.plugin
        plugin_args = self.plugin_args

        # wflows
        if not isinstance(wflows, list):
            err_msg = 'wflows parameter must be a list, but is of type: %s' \
                       % type(wflows)
            raise TypeError(err_msg)
        else:
            for wflow in wflows:
                if not isinstance(wflow, pe.Workflow):
                    err_msg = 'All elements in list must be workflow objects, '\
                              'but a type: %s was found!' % type(wflow)
                    raise TypeError(err_msg)

        # plugin
        if plugin is not None and not isinstance(plugin, str):
            err_msg = 'plugin parameter must be a string, but is of type: %s' \
                       % type(plugin)
            raise TypeError(err_msg)

        # plugin_args
        if not isinstance(plugin_args, dict):
            err_msg = 'plugin_args parameter must be a dict, but is of type: %s' \
                       % type(plugin_args)
            raise TypeError(err_msg)

        # Ensure workflow plugin arguments are less than bundler
        n_procs = plugin_args.get('n_procs', multiprocessing.cpu_count())
        if n_procs > self.num_threads:
            err_msg = 'Workflow threads: %d is greater than bundler '\
                      'threads: %d - fix and try again!' \
                      % (n_procs, self.num_threads)
            raise ValueError(err_msg)
        memory_gb = plugin_args.get('memory_gb', get_system_total_memory_gb())
        if memory_gb > self.memory_gb:
            err_msg = 'Workflow memory: %.3f GB is greater than bundler '\
                      'memory: %%.3f GB - fix and try again!' \
                      % (memory_gb, self.memory_gb)
            raise ValueError(err_msg)

        # Populate workflow plugin args
        self.plugin_args['n_procs'] = n_procs
        self.plugin_args['memory_gb'] = memory_gb

    def run(self, plugin=None, plugin_args=None):
        '''
        Run the workflows
        '''

        # Import packages
        from multiprocessing import Process

        # Error checking
        self.plugin = plugin
        self.plugin_args = plugin_args
        self._check_run_args()

        # Form process list
        kwargs = {'plugin' : self.plugin,
                  'plugin_args' : self.plugin_args}
        proc_list = [Process(target=wflow.run, args=(), kwargs=(kwargs)) \
                     for wflow in self.wflows]

        # Init variables
        num_wflows = len(self.wflows)
        running_wflow = 0
        job_queue = []
        available_memory = self.memory_gb
        available_threads = self.num_threads
        wflow_memory = self.plugin_args['memory_gb']
        wflow_threads = self.plugin_args['n_procs']

        # Launch and monitor jobs while they are available
        while running_wflow < num_wflows:
            if available_memory > self.plugin_args['memory_gb'] and \
               available_threads > self.plugin_args['n_procs']:
                available_memory -= wflow_memory
                available_threads -= wflow_threads
                # Start process
                proc_list[running_wflow].start()
                running_wflow += 1
