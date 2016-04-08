"""
 views.py
"""

from flask import request, session, redirect, render_template, flash
from app import app
from .sparql import queries as q
from .sparql import data_queries as dq
from .forms import AddForm, SummaryForm
from .formToTriple import form_to_triple as ft

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "GET":
        init_session_vars()

    form = AddForm(session)

    if form.validate_on_submit():
        triple = ft.formToTriple(form)
        #q.writeToBG(triple)
        print triple
        flash("Isolate added")
        return redirect("/index")
    else:
        session["form_error"] = False

    return render_template("addIso.html", title="Add Isolate", form=form)


@app.route("/names")
def names():

    isos = q.getIsoNames()
    return render_template("names.html", title="Isolate Names", isos=isos)

@app.route("/isolate_summary")
def summary():

    form = SummaryForm()

    if form.validate_on_submit():
        pass
    return render_template("isolate_summary.html", title="Isolate Summary", form=form)




def init_session_vars():

    session["last_animal"] = None
    session["last_sample_type"] = None
    session["form_error"] = False

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



