"""
 views.py
"""

from flask import request, session, redirect, render_template, flash
from app import app
from .sparql import data_queries as dq
from .forms import AddForm, SummaryForm
from .formToTriple import form_to_triple as ft

####################################################################################################
# index
#
# The homepage I guess. Just renders the index html where the buttons are displayed.
####################################################################################################
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

####################################################################################################
# add
#
# For getting the AddForm when requested, and going back to the home page when the form is submitted
# successfully. Calls init_session_vars and creates an AddForm when called.
####################################################################################################
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

####################################################################################################
# names
#
# Calls the query getIsoNames to retrieve, you guessed it, all the names of the isolates in the
# database. Renders the names html which just shows all the names we retrieved. Probably not useful
# and won't be included in the final app, but good for testing and seeing how everything works
# together.
####################################################################################################
@app.route("/names")
def names():

    isos = dq.getIsoNames()
    return render_template("names.html", title="Isolate Names", isos=isos)

####################################################################################################
# getSummary
#
# Renders the summaryForm when there's a GET request, displays a summary page for an isolate on a
# successful POST request. Retrieves most of the data for an isolate and displays it to the user.
####################################################################################################
@app.route("/getSummary", methods=["GET", "POST"])
def getSummary():

    form = SummaryForm()

    if form.validate_on_submit():

        iso_title = form.iso_title.data
        iso_name = dq.getPropVal(iso_title, "hasIsolateName")

        epi_vals, lims_vals, bio_vals = [], [], []

        epi_vals.append(dq.getPropVal(iso_title, "hasSourceName"))
        epi_vals.append(dq.getLocation(iso_title))

        lims_vals.append(dq.getPropVal(iso_title, "partOfProject"))
        lims_vals.append(dq.getPropVal(iso_title, "partOfSubProject"))
        lims_vals.append(dq.getPropVal(iso_title, "hasCollectionID"))
        lims_vals.append(dq.getPropVal(iso_title, "hasLDMSid"))
        lims_vals.append(dq.getPropVal(iso_title, "hasNMLid"))

        bio_vals.append(dq.getSpecies(iso_title))

        epi_keys = ("Source", "Location")
        bio_keys = ("Species",)
        lims_keys = ("Project", "Subproject", "Collection ID", "LDMS ID", "NML ID")

        epi_data = dict(zip(epi_keys, epi_vals))
        bio_data = dict(zip(bio_keys, bio_vals))
        lims_data = dict(zip(lims_keys, lims_vals))

        data = {"EPI Data":epi_data, "Biological Data":bio_data, "LIMS Data":lims_data}

        title = "Isolate {} Summary".format(iso_name)

        return render_template("summary.html",
                               title=title,
                               data=data)

    return render_template("get_summary.html", title="Isolate Summary", form=form)

####################################################################################################
# init_session_vars
#
# Just initializes some variables that we need in the session. Used in the AddFom validators mostly.
####################################################################################################
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



