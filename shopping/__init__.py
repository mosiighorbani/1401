from flask import Blueprint


shopping = Blueprint('shopping', __name__ , url_prefix='/shopping/')


from . import views
