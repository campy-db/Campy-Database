from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from app import app
from sparql import queries as q
from forms import AddForm
from formToTriple import formToTriple as ft

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/add", methods = ["GET","POST"])
def add():

    form = AddForm()

    if form.validate_on_submit():
        triple = ft.formToTriple(form)
        #q.writeToBG(triple)
        flash("Isolate added")
        return redirect("/index")

    return render_template("addIso.html", title = "Add Isolate", form = form)


@app.route("/names")
def names():

    isos = q.getIsoNames()
    return render_template("names.html",title = "Isolate Names",isos = isos)

"""
@app.route("/login", methods = ["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error  =  "Invalid username"
        elif request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("show_entries"))
    return render_template("login.html", error = error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("show_entries"))
"""



