import time

from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify

from webapp.catalog.models import Catalog
from webapp.db import db
from webapp.purchase.forms import AddVoucherForm
from webapp.utils import benchmark

blueprint = Blueprint('main', __name__)


@blueprint.route('/')
def index():
    return render_template('main/index.html')
