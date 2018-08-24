import random

from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

from . import home  # 导入blueprint
from .forms import ExerciseBeginForm, ExercisesForm, ExerciseSingleForm
from ..models import Question


# 主页
@home.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return render_template('home/index.html', username=current_user.username)
    return render_template('home/index.html')


# 个人信息
@home.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    return render_template('home/index.html', username=current_user.username)


# 刷题开始页
@home.route('/exercise', methods=['GET', 'POST'])
@login_required
def exercise():
    form = ExerciseBeginForm()
    # 1、选科目；2、如果已经选择了科目并点击"开始"，如果验证通过，则转到答题页面，同时将subject存入session
    if form.validate_on_submit():
        session['subject_id'] = form.subject.data  # 保存科目，通过session变量传给题目显示页
        session['q_ids'] = ''  # 清空已答题id列表；q_ids为以逗号分隔的question_id组成的字串，记录所有已经做过的问题
        session['current_q'] = 0  # 当前页面显示第几题（即当前题在q_ids中排第几个，用于前后翻页的情况）；0表示没有开始
        return redirect(url_for('home.exercises'))
    return render_template('home/exercise.html', form=form, username=current_user.username)


# 题目显示页
@home.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    form = ExercisesForm()
    if form.validate_on_submit():  # 判断request带POST数据，且数据符合表单定义要求
        # 点击了"提交"按钮。todo：接下来判断答案对错，如果答错，则显示正确答案
        pass

    # 如果不是点击"提交"（即前一题答对或现在是第一题），则生成试题并显示
    # alphabet = ['A', 'B', 'C', 'D', 'E', 'F']
    q_id_list = session.get('q_ids').split(',')  # 已经练过的问题的id的列表
    q_over = []  # 已经练过的问题的列表
    for qid in q_id_list:  # 从session中提取已经练过的问题的id列表
        q_over.append(Question.query.filter_by(id=qid).first())
    # 提取一道没有做过的随机题目
    q = random_question(q_over, session.get('subject_id'))
    if q is None:  # 返回的试题为空，则返回选择科目页面
        flash('恭喜！本专业下所有题目均已练习完毕！')
        return redirect(url_for('home.exercise'))
    else:  # 返回了一道题，接下来判断题型
        q_context = q.question  # 题干
        if q.question_type.type_name == 'SINGLE':
            optn_list = q.options.split('||')
            ans = q.answer
            form = ExerciseSingleForm(option_list)
    # todo: 判断上一题对错并回显；已回显的则显示下一题；所有题目答完的判断；如果session中题目列表为空，则生成所有题目的随机顺序id列表
    return render_template('home/exercises.html', form=form, question_context=q_context,
                           question_type=q.question_type.type_name, username=current_user.username)


# 试卷考试
@home.route('/examine', methods=['GET', 'POST'])
@login_required
def exam():
    return render_template('home/examine.html', username=current_user.username)


# 生成随机题目
def random_question(q_over, s_id):
    """生成随机题目。参数：(q_over：已经联系过的题目的id的列表, s_id：科目（subject）的id),"""
    all_question = Question.query.filter_by(subject_id=s_id).all()
    for q in q_over:  # 把已经联系过的题目去掉
        all_question.pop(q)
    if len(all_question) > 0:  # 如果未考题目列表中还有题目，则随即返回一道题目
        return random.choice(all_question)
    return None  # 否则（已练完所有题）返回None
