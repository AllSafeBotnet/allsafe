#!/usr/bin/python3

"""
This is the script handling the worker of the botnet seen as a single thread. 
The botnet will be made of multiple agents, independent each other, each one
using thread-based parallelism according to the features of their own running machines 
to handle multiple connection to the specified url.

Created:    24 October 2016
Modified:   24 October 2016
"""

import threading


class AllSafeWorker(threading.Thread):
    def __init__(self, tid, name, config):
        """
        This class extends the implementation of threading.Thread to handle a HTTP GET request.
        On init we set the thread identifier and we call the super class method.

        @param: tid, integer - the thread unique identifier 
        @param: name, alphanumeric string - the thread unique name
        @param: config, dictionary - the configuration parameter for this thread
        """
        # calling superclass init method
        threading.Thread.__init__(self)
        # setting up threading attributes
        self._tid     = tid
        self._name    = name
        # setting up connection parameters from dictionary
        # configuration - connection
        self._url     = config['url']
        self._agent   = config['agent']
        # configuration - periodicity
        self._period   = config['period']
        self._maxcount = config['maxcount']        


    def run(self):
        # dummy (for now...)
        print("I am: " + self._name)



if __name__ == "__main__":
    # dummy
