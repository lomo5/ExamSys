from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, ChangePasswordForm


# # auth 蓝本中的 before_app_request 处 理程序会在每次请求前运行
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.ping()  # 每次收到用户的请求时都要调用 User对象的ping() 方法更新用户的"上次访问时间"


@auth.route('/login')
def login():
    form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(staff_number=form.staff_number.data).first()
    #     if user is not None and user.verify_password(form.password.data):
    #         login_user(user, form.remember_me.data)
    #         next_page = request.args.get('next')
    #         if next_page is None or not next_page.startswith('/'):
    #             next_page = url_for('home.index')
    #         return redirect(next_page)
    #     flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('home.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)