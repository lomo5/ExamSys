from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User


# auth 蓝本中的 before_app_request 处 理程序会在每次请求前运行
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()  # 每次收到用户的请求时都要调用 ping() 方法更新用户的"上次访问时间"
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))