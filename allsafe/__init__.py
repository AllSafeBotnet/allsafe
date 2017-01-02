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


def show_login_form():
    # The render template method will render an HTML page using Jinja2 template if any.
    return render_template("loginpage.html")


def login(username, password):
    print("Hello " + username)
    if (validate(username, password)):
        return render_template("controlpage.html")
    else:
        return abort(401)


def validate(username, password):
    if (username == "fsociety" and password == "steelmountain"):
        # TODO Can we do it in a more effective way?
        return True;

if __name__ == "__main__":
    print("-------------------------------------------------------------")
    print("            ALLSAFE BOTNET - Academic purpose only           ")
    print("                          v. 0.1.0                           ")
    print("\nDeveloped with no harmful intentions and love by:          ")
    print("  - Alessio 'Tyrell' Moretti                                 ")
    print("  - Federico 'Elliot' Vagnoni                                ")
    print("-------------------------------------------------------------")
    app.run()
