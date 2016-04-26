"""
 __init__.py
"""

from flask import Flask

UPLOAD_FOLDER = "/home/student/Campy/CampyDatabase/WebApp/app/uploads"
ALLOWED_EXTENSIONS = set(["csv"])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config.from_object('config')

from app import views
