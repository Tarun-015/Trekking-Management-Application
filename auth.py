from functools import wraps
from flask import session, redirect


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "admin":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "staff":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "user":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function