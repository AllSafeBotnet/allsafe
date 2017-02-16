"""
This is a very module to retrieve system statistics.

Created:    16 January  2017
Modified:   16 January  2017
"""

import os
import platform

class SysStatistics:
    def __init__(self):
        """
        This class represents a simple interface to access
        a summary of the system statistics about the enviroment
        into which the botnet client is currently running.
        """
        self._osname   = os.name                    # 'posix', 'nt', 'java'
        self._environ  = os.environ                 # environment 
        self._platform = platform.platform()        # human readable platform summary
        self._node     = platform.node()            # name of the node as in the local network


    def getPlatformSummary(self):
        """
        This method just return platform summary.
        @return: string, summary of the platform available info
        """
        summary = ""
        summary += str(self._osname) + " >> "
        summary += str(self._platform) + " >> "
        summary += str(self._node)

        return summary


    def getEnvironmentSummary(self):
        """
        This method scan environ to get info about execution environment
        @return: string, summary of the exec environment
        """
        summary = ""
        try:
            summary += "LANG : " + str(self._environ['LANG']) + " - "
            summary += "HOME : " + str(self._environ['HOME']) + " - "
            summary += "PWD : " + str(self._environ['PWD']) + " - "
        except Exception:
            summary = "CANNOT RETRIEVE ENVIRON INFORMATION"

        return summary