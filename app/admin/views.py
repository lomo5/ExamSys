from . import admin  # 导入blueprint
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import User
from .forms import LoginForm


# 虽热此处路由只写了'/'，但是由于蓝图admin注册时添加了'/admin'前缀，因此实际以下路由为'/admin/'
@admin.route('/')
def index():
    form = LoginForm()
    return render_template('admin/test.html', form)
