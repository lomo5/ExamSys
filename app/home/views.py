from flask import render_template, redirect, request, url_for, flash
from . import home  # 导入blueprint


@home.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home/index.html')
