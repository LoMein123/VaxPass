import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def display_error(message, code=400):
    """Redirct to error page"""

    return render_template("error.html", top=code, bottom=message), code


def login_required(f):
    """Make sure user logs in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function