from flask import render_template, redirect, url_for, make_response, send_file
from datetime import datetime, timedelta

import tablib
from flask import render_template, redirect, url_for, make_response, send_file
from flask_login import login_required, current_user

from . import admin
from .forms import RegistrationForm, AdminReport
from ..models import User, Department, Exercise
import os



# 虽热此处路由只写了'/'，但是由于蓝图admin注册时添加了'/admin'前缀，因此实际以下路由为'/admin/'
@admin.route('/')
@login_required
def index():
    form = RegistrationForm()
    return render_template('admin/report.html', form)


@admin.route('/question_manage')
@login_required
def question_manage():
    form = RegistrationForm()
    return render_template('admin/report.html', form)


@admin.route('/paper_manage')
@login_required
def paper_manage():
    form = RegistrationForm()
    return render_template('admin/report.html', form)


@admin.route('/user_manage')
@login_required
def user_manage():
    form = RegistrationForm()
    return render_template('admin/report.html', form)


@admin.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if current_user.role.id != 1:
        redirect(url_for('home.index'))

    form = AdminReport()

    if form.validate_on_submit():
        period = form.period.data  # 统计周期
        unit = form.unit.data  # 统计单位

        period_name = [('D', '今天'), ('W', '本周'), ('M', '本月')]
        unit_name = [('department', '部门'), ('individual', '个人')]
        filename=''
        header_str = ''  # 标题中的"XX时段"名称
        day_before = (datetime.utcnow() + timedelta(days=-1))  #注 意：系统中时间均采用UTC时间！！！
        week_before = (datetime.utcnow() + timedelta(days=-7))
        month_before = (datetime.utcnow() + timedelta(days=-30))  # .strftime('%Y-%m-%d %H:%M')
        before = datetime.utcnow()
        if period == 'D':
            before = day_before
            filename += 'day_report'
            header_str = '今日做题人数'
        elif period == 'W':
            before = week_before
            filename += 'week_report'
            header_str = '本周做题人数'
        elif period == 'M':
            before = month_before
            filename += 'month_report'
            header_str = '本月做题人数'

        if unit == 'department':
            headers = (u"部门",u"部门人数", header_str, u"做题数量", u"正确率")
            filename = '_department.xls'
        elif unit == 'individual':
            headers = (u"部门", u"姓名", u"做题数量", u"正确率")
            filename='_individual.xls'
        data = tablib.Dataset(headers=headers)


        d_name = ''  # 部门名称
        count_q = 0  # 做题数量
        count_t = 0  # 正确数
        percent = 0  # 正确率
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
                            has_exercised=True
                    if has_exercised:
                        count_exe_user += 1
                if count_q !=0 and count_t !=0:
                    percent = round(count_t / count_q, 4) * 100  # todo:注意这里乘了100
                else:
                    percent = 0
                data.append([d_name, dept_user_count,count_exe_user, count_q, str(percent) + "%"])
        elif unit == 'individual':
            for d_user in User.query.all():
                for exe in Exercise.query.filter(Exercise.user_id == d_user.id).all():
                    if exe.begin_time > before:
                        count_q += len(exe.result_list)
                        count_t += exe.result_list.count('T')
                if count_q !=0 and count_t !=0:
                    percent = round(count_t / count_q, 4) * 100  # todo:注意这里乘了100
                else:
                    percent = 0
                data.append([d_user.department.department_name, d_user.username, count_q, str(percent) + "%"])

        open(filename, 'wb').write(data.xls)

        response = make_response(send_file("../" + filename))
        response.headers["Content-Disposition"] = "attachment; filename=" + filename
        # todo：文件名是中文会出编码错误告警：
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
            has_exercised =False
            for exe in Exercise.query.filter(Exercise.user_id == d_user.id).all():
                if exe.begin_time > before:
                    count_q += len(exe.result_list)
                    count_t += exe.result_list.count('T')
                    has_exercised = True
            if has_exercised:
                cout_exe_u += 1

        if count_q != 0 and count_t != 0:
            percent = round(count_t / count_q, 4) * 100  # 正确率。todo:注意这里乘了100
        else:
            percent = 0
        table.append([d_name, dept_user_count, cout_exe_u, count_q, str(percent) + "%"])

    return render_template('admin/report.html', form=form, table=table)
