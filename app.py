import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp

# configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Ensure responses are not cached
@app.after_request
def after_request(response):
    response.headers["Cach-Control"] = "no-cach, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Configure session to use filesystem (instead of cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
