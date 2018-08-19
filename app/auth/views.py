from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm


# # auth 蓝本中的 before_app_request 处 理程序会在每次请求前运行
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.ping()  # 每次收到用户的请求时都要调用 User对象的ping() 方法更新用户的"上次访问时间"


@auth.route('/login')
def login():
    form = LoginForm()  # 创建loginform对象
    if form.validate_on_submit():  # 如果验证通过，并点击了提交
        user = User.query.filter_by(staff_number=form.staff_number.data).first()
        if user is not None and user.verify_password(form.password.data):
            # login_user(user, remember=False, duration=None, force=False, fresh=True)
            # 调用login_user函数将user对象保存在会话上下文中
            login_user(user, form.remember_me.data)
            # next：用户访问未授权的URL时会转到登录表单，Flask-Login把原地址保存在查询字符串的next参数中。
            next_page = request.args.get('next')  # 从request.args字典中读取next参数
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('home.index')
            return redirect(next_page)
        flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已注销！')
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
            flash('您的密码已修改。')
            return redirect(url_for('home.index'))
        else:
            flash('无效的密码！')
    return render_template("auth/change_password.html", form=form)