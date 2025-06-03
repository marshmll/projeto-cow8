from flask import Blueprint, render_template

_other = Blueprint('_other', __name__)

@_other.route("/about")
def about():
    return render_template('about.html', data=[])
