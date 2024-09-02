from flask import Blueprint, render_template

from board.auth import login_required

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")

@bp.route("/about")
def about():
    return render_template("pages/about.html")

@bp.route("/admin")
@login_required  # Add this line to restrict access to admin pages.
def admin():
    return render_template("pages/admin.html")