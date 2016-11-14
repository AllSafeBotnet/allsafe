"""
This is the script handling the worker of the botnet seen as a single thread. 
The botnet will be made of multiple agents, independent each other, each one
using thread-based parallelism according to the features of their own running machines 
to handle multiple connection to the specified url.

Created:    24 October 2016
Modified:   13 November 2016
"""

import threading
from allsafe.utils.config import validateConfigFile
from allsafe.utils.log import log

class AllSafeWorker(threading.Thread):
    def __init__(self, wid, name, config):
        """
        This class extends the implementation of threading.Thread to handle a HTTP GET request.
        On init we set the thread identifier and we call the super class method.

        @param: wid, integer - the worker unique identifier 
        @param: name, alphanumeric string - the thread unique name
        @param: config, dictionary - the configuration parameter for this thread
        """
        # calling superclass init method
        threading.Thread._init__(self)
        # setting up threading attributes
        self._wid     = wid
        self._name    = name
        # setting up connection parameters from dictionary
        # configuration - connection
        self._url     = config['url']
        self._agent   = config['agent']
        # configuration - periodicity
        self._period   = int(config['period'])
        self._maxcount = int(config['maxcount'])


    def getWorkerTarget(self):
        """
        This method prints out a human readable representation of this worker purpose
        """
        workerTarget  = self.getName()
        workerTarget += " - TARGET: "  + self._url
        workerTarget += " - AGENT: "   + self._agent

    def run(self):
        # dummy (for now...)
        print("I am: " + self._name)


class AllSafeWorkerMaster():
    def __init__(self, config_file):
        """
        This class represents the botnet master as the thread who is in command to launch every 
        thread execution in order to fulfill botnet requiremets. It accepts a configuration file
        as main 

        @param: config_file, filename - path for the configuration file 
        """
        # parsing the configuration file to return a configuration dictionary
        self._configuration = validateConfigFile(config_file)
        if self._configuration == None:
            raise Exception("Configuration file is not properly formatted!")

        # configuring the master
        self._modified = long(self._configuration["last_modified"])
        self._agent    = self._configuration["user_agent_b"]
        self._remote   = self._configuration["cc_server"]
        self._log      = self._configuration["log_file"]

        # initializing workers array
        self._workers = []
        
    
    def initializeWorkers(self):
        """
        This method allow the botnet master to create every thread with correct parameters in order
        to correctly execute them.
        """
        
        # logging the initialization routine - start
        log(self._log, "------------------- <SETUP> -------------------")

        for i in range(0, len(self._configuration["targets"])):
            # iterating over the target list we initialize every worker
            worker = AllSafeWorker(i, "worker-" + str(i), self._configuration["targets"][i])
            # logging worker reference
            log(self._log, worker.getWorkerTarget())

        # logging the initialization routine - end
        log(self._log, "------------------- </SETUP> -------------------")


    def executeBotnet(self): 
        """
        This method handle the execution of the entire botnet, starting each worker one after one and
        handling the final join operation.
        """
        
        # iterating over workers to start them up
        for worker in self._workers:
            # logging the startup routine
            log(self._log, "starting up " + worker.getName() + " ...")
            worker.start()

        # iterating over worker to join them
        for worker_to_join in self._workers:
            worker_to_join.join()
        
        log(self._log, "... finally exiting bot master!")


if __name__ == "__main__":
    # dummy
    