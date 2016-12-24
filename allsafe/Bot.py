from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
 
'''
This is a simple implementation of a micro WebServer using Flask

This server will receive HTTP request in both GET and POST method on the root page.

If the method is POST, a login request is assumed and the login process will be performed;
if the process fails an error message will be returned; if it will succed the amdin page will be returned.

If the method is GET, the login form will be shown.
'''
@app.route("/",  methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        return login(request.form['u'], request.form['p'])
    else:
        return show_login_form()
    

def show_login_form():
    #The render template method will render an HTML page using Jinja2 template if any.
    return render_template("loginpage.html")

def login(username, password):
    print("Hello " + username)
    validate(username, password)                #TODO
    return render_template("adminpanel.html")   #TODO



if __name__ == "__main__":
    app.run()