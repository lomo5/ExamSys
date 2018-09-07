from datetime import datetime, timedelta

import tablib
from flask import render_template, redirect, url_for, make_response, send_file, flash
from flask_login import login_required, current_user

from . import admin
from .forms import AdminReport, AddUserForm, ChangePwdForm, ModifyUserForm, DeleteUserForm
from .. import db
from ..models import User, Department, Exercise, Subject


# 虽热此处路由只写了'/'，但是由于蓝图admin注册时添加了'/admin'前缀，因此实际以下路由为'/admin/'
# @admin.route('/')
# @login_required
# def index():
#     form = UserManageForm()
#     return render_template('admin/report.html', form=form)
#
#
# @admin.route('/question_manage')
# @login_required
# def question_manage():
#     form = UserManageForm()
#     return render_template('admin/report.html', form=form)
#
#
# @admin.route('/paper_manage')
# @login_required
# def paper_manage():
#     form = UserManageForm()
#     return render_template('admin/report.html', form=form)


@admin.route('/user_manage', methods=['GET', 'POST'])
@login_required
def user_manage():
    form_newuser = AddUserForm()
    form_pwd = ChangePwdForm()
    form_mod = ModifyUserForm()
    form_del = DeleteUserForm()

    # 用户提交了"创建新用户"表单
    if form_newuser.validate_on_submit() and form_newuser.submit_add.data is True:
        print('new user passed')
        new_user = User()
        try:
            new_user.staff_number = form_newuser.staff_number_add.data
            new_user.username = form_newuser.username_add.data
            new_user.department_id = int(form_newuser.department_add.data)
            new_user.role_id = int(form_newuser.role_add.data)
            new_user.add_time = datetime.utcnow()
            new_user.password = form_newuser.password_add.data
            new_user.info = ''
            sub_list = Subject.query.all()  # 为用户添加所有科目
            new_user.subjects = sub_list
        except:
            flash('创建新用户失败！')
            return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd,
                                   form_del=form_del,
                                   form_mod=form_mod, act_tab='newuser')
        db.session.add(new_user)
        db.session.commit()
        flash('新用户创建成功！')
        return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd, form_del=form_del,
                               form_mod=form_mod, act_tab='newuser')

    # 用户提交了"密码更改"表单
    if form_pwd.validate_on_submit() and form_pwd.submit_change.data is True:
        print('password passed')
        try:
            pwd_user = User.query.filter(User.staff_number == int(form_pwd.staff_number_change.data)).first()
            pwd_user.password = form_pwd.password_change.data
        except:
            flash('密码修改失败！')
            return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd,
                                   form_del=form_del,
                                   form_mod=form_mod, act_tab='password')

        # db.session.add(pwd_user)
        db.session.commit()
        flash('密码已更改！')
        return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd, form_del=form_del,
                               form_mod=form_mod, act_tab='password')

    # 用户提交了"删除用户"表单
    if form_del.validate_on_submit() and form_del.submit_delete.data is True:
        print('delete passed')
        try:
            del_user = User.query.filter(User.staff_number == int(form_del.staff_number_delete.data)).first()
            db.session.delete(del_user)
            db.session.commit()
        except:
            flash('删除用户失败！')
            return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd,
                                   form_del=form_del,
                                   form_mod=form_mod, act_tab='delete')

        flash('用户已删除！')
        return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd, form_del=form_del,
                               form_mod=form_mod, act_tab='delete')

    # 用户提交了"信息修改"表单
    if form_mod.validate_on_submit() and form_mod.submit_modify.data is True:
        print('modify passed')
        try:
            mod_user = User.query.filter(User.staff_number==int(form_mod.staff_number_modify.data)).first()
            mod_user.email = form_mod.email_modify.data
            mod_user.department_id = int(form_mod.department_modify.data)
            mod_user.role_id = int(form_mod.role_modify.data)
        except:
            flash('用户信息修改失败！')
            return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd,
                                   form_del=form_del,
                                   form_mod=form_mod, act_tab='modify')
        db.session.commit()
        flash('用户信息已修改！')
        return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd, form_del=form_del,
                               form_mod=form_mod, act_tab='modify')

    # 如果不是post，或者validate失败，则根据用户点击的submit按钮来确定接下来渲染的页面的默认tab是哪个；如果是get则返回default。
    if form_mod.submit_modify.data is True:
        act_tab = 'modify'
    elif form_del.submit_delete.data is True:
        act_tab = 'delete'
    elif form_pwd.submit_change.data is True:
        act_tab = 'password'
    elif form_newuser.submit_add.data is True:
        act_tab = 'newuser'
    else:
        act_tab = 'default'

    return render_template('admin/usermanage.html', form_newuser=form_newuser, form_pwd=form_pwd, form_del=form_del,
                           form_mod=form_mod, act_tab=act_tab)


@admin.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    """统计报表
    """
    if current_user.role.id != 1:
        redirect(url_for('home.index'))

    form = AdminReport()

    if form.validate_on_submit():
        period = form.period.data  # 统计周期
        unit = form.unit.data  # 统计单位

        period_name = [('D', '今天'), ('W', '本周'), ('M', '本月')]
        unit_name = [('department', '部门'), ('individual', '个人')]
        filename = ''
        header_str = ''  # 标题中的"XX时段"名称
        day_before = (datetime.utcnow() + timedelta(days=-1))  # 注 意：系统中时间均采用UTC时间！！！
        week_before = (datetime.utcnow() + timedelta(days=-7))
        month_before = (datetime.utcnow() + timedelta(days=-30))  # .strftime('%Y-%m-%d %H:%M')
        before = datetime.utcnow()
        if period == 'D':
            before = day_before
            filename += '24小时统计'
            header_str = '今日做题人数'
        elif period == 'W':
            before = week_before
            filename += '本周统计'
            header_str = '本周做题人数'
        elif period == 'M':
            before = month_before
            filename += '本月统计'
            header_str = '本月做题人数'

        if unit == 'department':
            headers = (u"部门", u"部门人数", header_str, u"做题数量", u"正确率")
            filename += '_部门.xls'
        elif unit == 'individual':
            headers = (u"部门", u"姓名", u"做题数量", u"正确率")
            filename += '_个人.xls'
        data = tablib.Dataset(headers=headers)

        if unit == 'department':
            for dept in Department.query.all():
                d_name = dept.department_name
                # 计数器清零
                count_q = 0  # 做题数量
                count_t = 0  # 正确数
                dept_user_count = len(User.query.filter(User.department_id == dept.id).all())  # 部门人数
                count_exe_user = 0  # 统计时段内做题的人数
                for d_user in dept.users:
                    has_exercised = False
                    for exe in Exercise.query.filter(Exercise.user_id == d_user.id).all():
                        if exe.begin_time > before:
                            count_q += len(exe.result_list)
                            count_t += exe.result_list.count('T')
                            has_exercised = True
                    if has_exercised:
                        count_exe_user += 1
                if count_q != 0 and count_t != 0:
                    percent = round((count_t / count_q) * 100, 2)  # 保留两位小数，注意：这里乘了100
                else:
                    percent = 0
                data.append([d_name, dept_user_count, count_exe_user, count_q, str(percent) + "%"])
        elif unit == 'individual':
            for d_user in User.query.all():
                count_q = 0
                count_t = 0
                for exe in Exercise.query.filter(Exercise.user_id == d_user.id).all():
                    if exe.begin_time > before:
                        count_q += len(exe.result_list)
                        count_t += exe.result_list.count('T')
                if count_q != 0 and count_t != 0:
                    percent = round((count_t / count_q) * 100, 2)  # 正确率，保留两位小数
                else:
                    percent = 0
                data.append([d_user.department.department_name, d_user.username, count_q, str(percent) + "%"])

        open(filename, 'wb').write(data.xls)

        # 问题：本地调试的时候，由于没有uwsgi做代理，当前目录即为项目根目录。写文件会写到项目根目录下。上传腾讯云后，写目录变成了/home/www/examsys，此时再用send_file("../" + filename)就会提示文件不存在（uwsgi的log中）
        # 这是由于：上传到腾讯云后，uwsgi配置文件没有指定项目根目录，默认将是uwsgi的启动目录。这就使运行时，默认当前目录变成了/home/www/examsys,而不是/home/www/examsys/ExamSys
        # 解决办法：需要在uwsgi的配置文件中添加chdir变量，将当前目录指定为：/home/www/examsys/ExamSys
        response = make_response(send_file("../" + filename))
        # 文件名中文支持：通过将filename编码转为latin-1（server.py里边会严格按照latin-1编码来解析filename），将utf8编码的中文文件名默认转为latin-1编码文件名。
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        # UnicodeEncodeError: 'latin-1' codec can't encode characters in position 42-46: ordinal not in range(256)
        # 参考：https://stackoverflow.com/questions/47575665/flask-raises-unicodeencodeerror-latin-1-when-send-attachment-with-utf-8-charac

        return response

    # 获取页面下方表格参数
    table = []  # 页面表格内容
    before = (datetime.utcnow() + timedelta(days=-1))  # 注 意：系统中时间均采用UTC时间！！！
    for dept in Department.query.all():
        d_name = dept.department_name
        # 计数器清零
        count_q = 0  # 做题数量
        count_t = 0  # 正确数
        dept_user_count = len(User.query.filter(User.department_id == dept.id).all())  # 部门人数
        cout_exe_u = 0  # 做题人数
        for d_user in dept.users:
            has_exercised = False
            for exe in Exercise.query.filter(Exercise.user_id == d_user.id).all():
                if exe.begin_time > before:
                    count_q += len(exe.result_list)
                    count_t += exe.result_list.count('T')
                    has_exercised = True
            if has_exercised:
                cout_exe_u += 1

        if count_q != 0 and count_t != 0:
            percent = round(count_t / count_q, 4) * 100  # 正确率。注意：这里乘了100
        else:
            percent = 0
        table.append([d_name, dept_user_count, cout_exe_u, count_q, str(percent) + "%"])  # todo:为什么总有超长的百分数？？？导出的excel是正确的！

    return render_template('admin/report.html', form=form, table=table)
