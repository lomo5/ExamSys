import random
from datetime import datetime

from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user

from . import home  # 导入blueprint
from .forms import ExerciseBeginForm, ExerciseSingleForm, ExerciseTrueFalseForm, ExerciseMultiChoiceForm, \
    ExerciseFillForm, ExerciseAnswerForm, ExerciseNextQuestionForm
from .. import db
from ..models import Question, Exercise, QuestionType, Mistake

QUESTIONTYPES = [('填空题', 'hoem')]


# [(qt.id, qt.type_name) for qt in QuestionType.query.order_by(QuestionType.id).all()]

# 主页
@home.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return render_template('home/index.html')
    return render_template('home/index.html')


# 刷题开始页
@home.route('/beginexerc', methods=['GET', 'POST'])
@login_required
def beginexerc():
    form = ExerciseBeginForm()
    # 1、选科目；2、如果已经选择了科目并点击"开始"，如果验证通过，则转到答题页面，同时将subject存入session
    if form.validate_on_submit():
        # 写入Exercise表：时间、两个字串
        exerc_id = new_exercise()
        # 将科目id和刚生成的练习id加入session以备在接下来的练习题目页面显示
        session['subject_id'] = form.subject.data  # 保存科目，通过session变量传给题目显示页
        session['exercise_id'] = exerc_id  # commit之后exerc才有了id
        q_type_id = int(form.question_type.data)
        session['question_type'] = q_type_id  # 保存题型，0表示所有题型
        session.pop('before_id', None)
        session.pop('u_answer', None)
        # session['current_q'] = 0  # 当前页面显示第几题（即当前题在q_ids中排第几个，用于前后翻页的情况）；0表示没有开始

        # q_type_name = QuestionType.query.filter(QuestionType.id == q_type_id).first().type_name
        # if q_type_name == "单选题":
        #     return redirect(url_for('home.single'))
        # elif q_type_name == "多选题":
        #     return redirect(url_for('home.multi'))
        # elif q_type_name == "填空题":
        #     return redirect(url_for('home.filling'))
        # elif q_type_name == "判断题":
        #     return redirect(url_for('home.truefalse'))
        # elif q_type_name == "简答题":
        #     return redirect(url_for('home.jianda'))

        return redirect(url_for('home.exercises'))
    return render_template('home/beginexerc.html', form=form)


# # 单选题
# @home.route('/single', methods=['GET', 'POST'])
# @login_required
# def single():
#     if 'subject_id' not in session or 'question_type' not in session:  # 如果session中没有subject_id，则返回选择科目页面
#         flash('请先选择科目和题型！')
#         return redirect(url_for('home.exercise'))
#     if 'exercise_id' not in session:
#         exerc_id = new_exercise()
#         session['exercise_id'] = exerc_id
#     # 取得当前的Exercise对象
#     exerc = Exercise.query.filter(Exercise.id == session['exercise_id']).first()
#     sub_id = session['subject_id']  # 取得当前科目id
#     qtype = session['question_type']  # 取得当前问题类型
#     if sub_id == '' or qtype == '':
#         flash('请先选择科目和题型！')
#         return redirect(url_for('home.exercise'))
#
#     # str_result = exerc.result_list  # 已经练过的问题的结果字串
#     # result_list = list(str_result)  # 已经练过的问题的结果列表
#
#     q_next = random_question(exerc, sub_id, int(qtype))  # 生成一道随机题目
#     if q_next is None:  # 如果是最后一道题,则清空session变量，返回科目选择页面
#         flash('恭喜！本专业下此类题型所有题目均已练习完毕！')
#         session.pop('exercise_id', None)
#         session.pop('subject_id', None)
#         session.pop('before_id', None)
#         return redirect(url_for('home.exercise'))
#     form = ExerciseSingleForm(question=q_next)
#     a = form.validate_on_submit()
#     b = form.is_submitted()
#     if form.validate_on_submit() and "before_id" in session:
#         q_id_before = int(session['before_id'])
#
#     session['before_id'] = str(q_next.id)
#     return render_template('home/single.html')


# # 多选题
# @home.route('/multi', methods=['GET', 'POST'])
# @login_required
# def multi():
#     return render_template('home/multi.html')
#
#
# # 填空题
# @home.route('/filling', methods=['GET', 'POST'])
# @login_required
# def filling():
#     return render_template('home/filling.html')
#
#
# # 判断题
# @home.route('/truefalse', methods=['GET', 'POST'])
# @login_required
# def truefalse():
#     return render_template('home/trueflase.html')
#
#
# # 简答题
# @home.route('/jianda', methods=['GET', 'POST'])
# @login_required
# def jianda():
#     return render_template('home/jianda.html')


# 题目显示页
@home.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    if 'subject_id' not in session or 'question_type' not in session:  # 如果session中没有subject_id，则返回选择科目页面
        flash('请先选择科目和题型！')
        return redirect(url_for('home.beginexerc'))
    if 'exercise_id' not in session:
        exerc_id = new_exercise()
        session['exercise_id'] = exerc_id
    # 取得当前的Exercise对象
    exerc = Exercise.query.filter(Exercise.id == session['exercise_id']).first()
    sub_id = session['subject_id']  # 取得当前科目id
    qtype = session['question_type']  # 取得当前问题类型。todo：用于指定特地题型的情况
    if sub_id == '' or qtype == '':
        flash('请先选择科目和题型！')
        return redirect(url_for('home.beginexerc'))

    if 'before_id' in session:
        before_id = session['before_id']  # 上一题id。  新打开浏览器直接取会出错（不存在），应该先判断是否存在！！
        before_qtype_id = Question.query.filter(Question.id == before_id).first().qtype_id
        before_qtype_name = QuestionType.query.filter(QuestionType.id == before_qtype_id).first().type_name
    else:
        before_id = ''  # todo: 上一题为空
        before_qtype_id = ''
        before_qtype_name = ''

    # str_result = exerc.result_list  # 已经练过的问题的结果字串
    if int(qtype) != 0:
        qtypename = QuestionType.query.filter(QuestionType.id == int(qtype)).first().type_name
    else:
        qtypename = '单选题'  # 随便挑一个

    if qtypename == '单选题':
        form = ExerciseSingleForm()  # (question=Question.query.filter(Question.id == before_id).first())
    elif qtypename == '多选题':
        form = ExerciseMultiChoiceForm()  # (question=Question.query.filter(Question.id == before_id).first())
    elif qtypename == '判断题':
        form = ExerciseTrueFalseForm()
    elif qtypename == '填空题':
        form = ExerciseFillForm()
    elif qtypename == '简答题':
        form = ExerciseAnswerForm()

    # try:
    req_form = request.form
    #     subm = req_form['submit']
    le = len(req_form)
    #     # sub_data = req_form.submit.data
    #     #
    #     # d_le = len(req_form.submit.data)
    #     # r=request
    #     # a = req_form.form['submit']
    #     submited = le > 2  # (not req_form['submit'] is None) and req_form.submit.data == True
    #
    # except:
    #     submited = False

    if form.is_submitted() and before_id != '':  # 判断request带POST数据，且数据符合表单定义要求
        # 点击了"提交"按钮。todo：接下来判断答案对错，如果答错，则显示正确答案
        # todo：点了提交则：判断对错；更新mistake、exercise表；跳转显示answer页
        before_q = Question.query.filter_by(id=before_id).first()  # 上一题对象
        correct = None
        u_answer = ''  # 用户答案
        # before_q_contxt = ''  #
        # before_q_type = ''
        # before_q_options = ''
        try:
            # 判断对错
            if before_qtype_name == '单选题':
                if 'answers' in req_form:
                    u_answer = req_form['answers']
                # before_q_contxt = before_q.question
                # before_q_type = before_q.question_type.type_name
                # before_q_options = before_q.options
            elif before_qtype_name == '多选题':
                if 'multi1' in req_form and req_form['multi1'] != '':
                    u_answer += 'A'
                if 'multi2' in req_form and req_form['multi2'] != '':
                    u_answer += 'B'
                if 'multi3' in req_form and req_form['multi3'] != '':
                    u_answer += 'C'
                if 'multi4' in req_form and req_form['multi4'] != '':
                    u_answer += 'D'
                if 'multi5' in req_form and req_form['multi5'] != '':
                    u_answer += 'E'
                if 'multi6' in req_form and req_form['multi6'] != '':
                    u_answer += 'F'
                if 'multi7' in req_form and req_form['multi7'] != '':
                    u_answer += 'G'
                if 'multi8' in req_form and req_form['multi8'] != '':
                    u_answer += 'H'
            elif before_qtype_name == '判断题':
                if 'truefalse' in req_form:
                    u_answer = req_form['truefalse']
            elif before_qtype_name == '填空题':
                if 'fill1' in req_form and req_form['fill1'] != '':
                    u_answer += req_form['fill1']
                if 'fill2' in req_form and req_form['fill2'] != '':
                    u_answer += '||' + req_form['fill2']
                if 'fill3' in req_form and req_form['fill3'] != '':
                    u_answer += '||' + req_form['fill3']
                if 'fill4' in req_form and req_form['fill4'] != '':
                    u_answer += '||' + req_form['fill4']
                if 'fill5' in req_form and req_form['fill5'] != '':
                    u_answer += '||' + req_form['fill5']
                if 'fill6' in req_form and req_form['fill6'] != '':
                    u_answer += '||' + req_form['fill6']
                if 'fill7' in req_form and req_form['fill7'] != '':
                    u_answer += '||' + req_form['fill7']
                if 'fill8' in req_form and req_form['fill8'] != '':
                    u_answer += '||' + req_form['fill8']
            elif before_qtype_name == '简答题':
                if 'ans' in req_form:
                    u_answer = req_form['ans']

            if u_answer == before_q.answer:
                correct = True
            else:
                correct = False
        except:
            correct = False

        # 更新Exercise表、Mistake表
        update_exercises(before_id, exerc, correct)
        update_mistakes(before_id, current_user.id, correct)

        session['before_id'] = before_id
        # session['question_type'] = before_qtype_id
        session['u_answer'] = u_answer
        # 如果上次答题错误，转到answer.html，正确则继续下一题并用falsh显示正确提示。
        if correct:
            flash('回答正确！')
            session.pop('u_answer')
        else:
            session['u_answer'] = u_answer
            return redirect(url_for('home.answer'))

    """如果不是点击"提 交"（即前一题答对或现在是第一题），则生成试题并显示"""
    if qtype != 0:
        q_next = random_question(exerc, sub_id, qtype)
    else:
        q_next = random_question(exerc, sub_id)  # 生成一道随机题目
    q_next_qtype_name = q_next.question_type.type_name  # 题型名称
    # 判断题目类型,根据题型创建不同类型的form
    if q_next_qtype_name == '单选题':
        form = ExerciseSingleForm(question=q_next)
    elif q_next_qtype_name == '多选题':
        form = ExerciseMultiChoiceForm(question=q_next)
    elif q_next_qtype_name == '判断题':
        form = ExerciseTrueFalseForm()
    elif q_next_qtype_name == '填空题':
        form = ExerciseFillForm()
    elif q_next_qtype_name == '简答题':
        form = ExerciseAnswerForm()

    # if form.submit.label != ExerciseNextQuestionForm.submit.label:  # 不是"下一题"的那个form，而是点击了"提交"或从其他页面转过来的。
    #     form = ExerciseNextQuestionForm()

    if q_next is None:  # 如果是最后一道题,则清空session变量，返回科目选择页面
        flash('恭喜！本专业下所有题目均已练习完毕！')
        session.pop('exercise_id', None)
        session.pop('subject_id', None)
        session.pop('before_id', None)
        session.pop('u_answer', None)
        session.pop('question_type', None)
        return redirect(url_for('home.exercise'))

    q_context = q_next.question  # 题干
    # todo: 显示下一题；所有题目答完的判断；如果session中题目列表为空，则生成所有题目的随机顺序id列表
    # exerc.question_list += str(q_next.id) 去掉，在点击submit提交后再插入exercise表

    session['before_id'] = str(q_next.id)
    # 取得form中的所有field，以便对于"多选"和填空按field进行渲染
    fields = []
    if q_next_qtype_name == '填空题' or q_next_qtype_name == '多选题':
        for field in form:
            fields.append(field)
            field.data=False
    if q_next_qtype_name=='单选题':  # 清空选项
        form.answers.data=None
    if q_next_qtype_name=='判断题':
        form.truefalse.data=None

    # 多选：为了在模版中将没有文字的选项隐藏，按field为单位来渲染并为包含其的<p>标签设置class="hide"来隐藏。其它题型则按整个form渲染。
    if isinstance(form, ExerciseMultiChoiceForm):
        return render_template('home/exercises.html', fields=fields, question_context=q_context,
                               question_type=q_next.question_type.type_name)
    # 填空：需要将多余的空格（）隐藏，因此额外想模版传入一个表示空格数的变量：blank_num
    if isinstance(form, ExerciseFillForm):
        blank_num = len(q_next.answer.split("||"))  # 取得填空题的答案数量
        return render_template('home/exercises.html', fields=fields, blank_num=blank_num, question_context=q_context,
                               question_type=q_next.question_type.type_name)
    return render_template('home/exercises.html', form=form, question_context=q_context, fields=fields,
                           question_type=q_next.question_type.type_name)


# 练习答题结果反馈页
@home.route('/answer', methods=['GET', 'POST'])
@login_required
def answer():
    form = ExerciseNextQuestionForm()
    if form.is_submitted():
        return redirect(url_for('home.exercises'))

    if 'before_id' in session and 'u_answer' in session:
        before_id = int(session['before_id'])
        # before_qtype_id = session['question_type']
        # u_answer = session['u_answer']
        q = Question.query.filter(Question.id == before_id).first()
        q_type_name = q.question_type.type_name
        answers = ''
        options = ''
        if q_type_name == '单选题':
            options = q.options.split('||')
            answers = q.answer
        elif q_type_name == '多选题':
            tmp = q.options.split('||')
            options = []
            alph = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
            for i in range(0, len(tmp)):  # 答案起那面添加A、B、C、D
                options.append(alph[i] + '. ' + tmp[i])

            answers = q.answer
        elif q_type_name == '判断题':
            if q.answer == 'T':
                answers = '正确'
            else:
                answers = '错误'
        elif q_type_name == '填空题':
            options = q.answer.split('||')  # 特殊！！直接把答案用options显示出来
        elif q_type_name == '简答题':
            answers = q.answer

    return render_template('home/answer.html', form=form, question_context=q.question, question_type=q_type_name,
                           answers=answers, options=options)


# 个人统计信息
@home.route('/statistic', methods=['GET', 'POST'])
@login_required
def statistic():
    return render_template('home/examine.html')


# 错题回顾
@home.route('/mistakes', methods=['GET', 'POST'])
@login_required
def mistakes():
    return render_template('home/examine.html')


# 试卷考试
@home.route('/examine', methods=['GET', 'POST'])
@login_required
def exam():
    return render_template('home/examine.html')


# 个人信息
@home.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    return render_template('home/index.html')


# --------------------------------------------------------------------------
# -------------------------------下面是内部函数-------------------------------
# --------------------------------------------------------------------------

# 生成随机题目函数
def random_question(exerc, s_id, qtypte_id=None):
    """生成随机题目
    :param exerc：Exercise对象
    :param s_id：科目（subject）的id)
    :param qtypte_id: 题型id，默认为None表示不限题型
    """
    # 已答问题id组成的","分隔的字串
    q_str = exerc.question_list
    if q_str != '':
        q_over_list = exerc.question_list.split(',')  # 已经练过的问题的id的列表
    else:
        q_over_list = []
    if qtypte_id is None:
        all_question = Question.query.filter_by(subject_id=int(s_id)).all()
    else:
        all_question = Question.query.filter(Question.subject_id == int(s_id)).filter(
            Question.qtype_id == int(qtypte_id)).all()

    if len(q_over_list) > 0:  # 如果有已经做过的题，则需要从备选题列表中删去
        for q in q_over_list:  # 把已经联系过的题目去掉
            que = Question.query.filter(Question.id == q).first()
            all_question.remove(que)

    if len(all_question) > 0:  # 如果未考题目列表中还有题目，则随即返回一道题目
        return random.choice(all_question)
    return None  # 否则（已练完所有题）返回None


def new_exercise():
    """创建一个新的exercise，写入Exercise表，返回exercise.id
    时间为当前时间
    两个字串为空
    """
    exerc = Exercise()
    exerc.user_id = current_user.id
    exerc.begin_time = datetime.utcnow()
    exerc.question_list = ''
    exerc.result_list = ''
    db.session.add(exerc)
    db.session.commit()
    return exerc.id


def update_mistakes(before_id, user_id, correct):
    """更新Mistake表
    :param before_id,试题（question）id
    :param user_id, 用户id
    :param correct,是否正确
    """
    mis_count = len(
        Mistake.query.filter(Mistake.question_id == before_id).filter(Mistake.user_id == user_id).all())
    if correct:
        if mis_count != 0:  # 说明该用户以前做错过这道题，这次做对了，要在正确次数上加一
            mis = Mistake.query.filter(Mistake.question_id == before_id).filter(
                Mistake.user_id == user_id).first()
            mis.correct_times += 1
            db.session.add(mis)
            db.session.commit()
    else:
        if mis_count != 0:  # 说明该用户以前做错过这道题，又做错了，要在错误次数上加一
            mis = Mistake.query.filter(Mistake.question_id == before_id).filter(
                Mistake.user_id == user_id).first()
            mis.wrong_times += 1
        else:
            mis = Mistake()
            mis.user_id = user_id
            mis.question_id = before_id
            mis.wrong_times = 1
        db.session.add(mis)
        db.session.commit()


def update_exercises(before_id, exerc, correct):
    """更新Exercise表
    :param before_id, 试题（question）id
    :param exerc, exercise对象
    :param correct,是否正确
    """
    exerc.result_list += ',' + before_id
    if correct:
        exerc.result_list += 'T'
    else:
        exerc.result_list += 'F'
    db.session.add(exerc)
    db.session.commit()
