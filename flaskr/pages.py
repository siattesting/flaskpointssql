from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint("pages", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template('home.html')

@bp.route("/about", methods=["GET"])
def about():
    return render_template('about.html')