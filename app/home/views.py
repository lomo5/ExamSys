import random
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user

from . import home  # 导入blueprint
from .forms import ExerciseBeginForm, ExerciseSingleForm, ExerciseTrueFalseForm, ExerciseMultiChoiceForm, \
    ExerciseFillForm, ExerciseAnswerForm, ExerciseNextQuestionForm
from .. import db
from ..models import Question, Exercise, QuestionType, Mistake


# [(qt.id, qt.type_name) for qt in QuestionType.query.order_by(QuestionType.id).all()]

# 主页
@home.route('/', methods=['GET', 'POST'])  # 如果methods没有指定，则视图函数只接收GET请求
def index():
    if current_user.is_authenticated:
        return render_template('home/index.html')
    return render_template('home/index.html')


@home.route('/beginexerc/<collection>', methods=['GET', 'POST'])
@login_required
def beginexerc(collection):
    """刷题开始页，选择Subject和题型
    :param collection:试题集来源，表示练习的试题集是练习（'exercise'）还是错题（'mistake'）
    """
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
        session['collection'] = collection  # 保存题库来源：练习/错题回顾
        session.pop('before_id', None)
        session.pop('u_answer', None)

        return redirect(url_for('home.exercises'))
    return render_template('home/beginexerc.html', form=form, collection=collection)


@home.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    """题目显示页"""
    if 'collection' not in session:  # 避免用户直接从地址栏跳转到练习或试题回顾页面的情况
        return redirect(url_for('home.index'))
    collection = session['collection']
    if 'subject_id' not in session or 'question_type' not in session:  # 如果session中没有subject_id，则返回选择科目页面
        flash('请先选择科目和题型！')
        return redirect(url_for('home.beginexerc', collection=collection))
    if 'exercise_id' not in session:
        exerc_id = new_exercise()
        session['exercise_id'] = exerc_id
    # 取得当前的Exercise对象
    exerc = Exercise.query.filter(Exercise.id == session['exercise_id']).first()
    sub_id = session['subject_id']  # 取得当前科目id
    qtype = session['question_type']  # 取得当前问题类型，即在beginexerc页面中选择的题型。
    if sub_id == '' or qtype == '':
        flash('请先选择科目和题型！')
        return redirect(url_for('home.beginexerc', collection=collection))

    if 'before_id' in session:
        before_id = session['before_id']  # 上一题id。  新打开浏览器直接取会出错（不存在），应该先判断是否存在！！
        before_qtype_id = Question.query.filter(Question.id == before_id).first().qtype_id
        before_qtype_name = QuestionType.query.filter(QuestionType.id == before_qtype_id).first().type_name
    else:
        before_id = ''
        before_qtype_id = ''
        before_qtype_name = ''

    # 生成一个临时的傀儡form，以便form.is_submitied()可以通过此对象检查form提交状态。todo：方法太笨！！！
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

    # 取得request对象中的form列表。通过request来进行提交内容的检查。todo：不是好办法，直接使用request太麻烦，wtform应该有更好的办法。
    req_form = request.form

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
            # 判断用户答案对错。todo: 方法太笨，需改进。
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
        update_exercises(before_id, exerc.id, correct)
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

    collection = session['collection']
    """如果不是点击"提 交"（即前一题答对或现在是第一题），则生成试题并显示。
    根据菜单选的是"练习"还是"错题回顾"来生成随机题目。    
    """
    if collection == 'mistake':  # 菜单选择的是"错题回顾"
        if qtype != 0:
            q_next = random_question(exerc, sub_id, qtype, revise=True)  # 生成一道指定题型的随机题目
        else:
            q_next = random_question(exerc, sub_id, revise=True)  # 生成一道随机题目
    else:  # 菜单选的是"练习"
        if qtype != 0:
            q_next = random_question(exerc, sub_id, qtype)  # 生成一道指定题型的随机题目
        else:
            q_next = random_question(exerc, sub_id)  # 生成一道随机题目

    if q_next is None:  # 如果是最后一道题,则清空session变量，返回科目选择页面
        flash('恭喜！所有题目均已练习完毕！')
        session.pop('exercise_id', None)
        session.pop('subject_id', None)
        session.pop('before_id', None)
        session.pop('u_answer', None)
        session.pop('question_type', None)
        return redirect(url_for('home.beginexerc', collection=collection))

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

    q_context = q_next.question  # 题干
    # exerc.question_list += str(q_next.id) 去掉，在点击submit提交后再插入exercise表

    session['before_id'] = str(q_next.id)
    # 取得form中的所有field，以便对于"多选"和填空按field进行渲染
    fields = []
    if q_next_qtype_name == '填空题' or q_next_qtype_name == '多选题':
        for field in form:
            fields.append(field)
            field.data = None
    if q_next_qtype_name == '单选题':  # 清空上一题留下的保存在session中等选项值（通过session自动保存）
        form.answers.data = None
    if q_next_qtype_name == '判断题':
        form.truefalse.data = None

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


@home.route('/answer', methods=['GET', 'POST'])
@login_required
def answer():
    """练习答题结果反馈页"""
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


@home.route('/statistic', methods=['GET', 'POST'])
@login_required
def statistic():
    """个人统计信息"""
    # 获取页面表格参数
    table = []  # 页面表格内容.行：统计周期（今天、本周、本月）、做题数量、错题数、正确率
    before = (datetime.utcnow() + timedelta(days=-1))  # 注 意：系统中时间均采用UTC时间！！！
    duration = '今天'
    q_count = 0
    r_count = 0
    for exe in Exercise.query.filter(Exercise.user_id == current_user.id, Exercise.begin_time > before).all():
        q_count += len(exe.result_list)
        r_count += exe.result_list.count('T')
    if q_count != 0 and r_count != 0:
        percent = round(r_count / q_count, 4) * 100  # 正确率。注意：这里乘了100
    else:
        percent = 0
    table.append([duration, q_count, r_count, str(percent) + "%"])

    duration = '本周'
    before = (datetime.utcnow() + timedelta(days=-7))  # 注 意：系统中时间均采用UTC时间！！！
    q_count = 0
    r_count = 0
    for exe in Exercise.query.filter(Exercise.user_id == current_user.id, Exercise.begin_time > before).all():
        q_count += len(exe.result_list)
        r_count += exe.result_list.count('T')
    if q_count != 0 and r_count != 0:
        percent = round(r_count / q_count, 4) * 100  # 正确率。注意：这里乘了100
    else:
        percent = 0
    table.append([duration, q_count, r_count, str(percent) + "%"])

    duration = '本月'
    before = (datetime.utcnow() + timedelta(days=-30))  # 注 意：系统中时间均采用UTC时间！！！
    q_count = 0
    r_count = 0
    for exe in Exercise.query.filter(Exercise.user_id == current_user.id, Exercise.begin_time > before).all():
        q_count += len(exe.result_list)
        r_count += exe.result_list.count('T')
    if q_count != 0 and r_count != 0:
        percent = round(r_count / q_count, 4) * 100  # 正确率。注意：这里乘了100
    else:
        percent = 0
    table.append([duration, q_count, r_count, str(percent) + "%"])

    return render_template('home/statistics.html', table=table)


# 错题回顾
@home.route('/mistakes', methods=['GET', 'POST'])
@login_required
def mistakes():
    exe = Exercise()
    print(random_question(exe, ))
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
def random_question(exerc, sub_id, qtypte_id=None, revise=False):
    """生成随机题目
    :param exerc：Exercise对象，是必须的参数
    :param sub_id：科目（subject）的id),是必须的参数
    :param qtypte_id: 题型id，默认为None表示不限题型
    :param revise: 表示是否是错题回顾模式。False表示非错题回顾，则从题库中随机选一个指定科目、指定题型、且本次exercise没做过的题；为True表示是错题回顾模式，则从错题中随机找（优先没做对过的）
    """
    # 已答问题id组成的","分隔的字串
    q_str = exerc.question_list
    if q_str != '':
        q_id_over_list = exerc.question_list.split(',')  # 已经练过的问题的id的列表
    else:
        q_id_over_list = []

    if revise:  # todo: 这里不对，需要输出的all_question是所有question对象的list
        if qtypte_id is None:
            # 未指定题型，则取得当前用户指定科目下的所有的错题
            all_question = Question.query.filter_by(subject_id=int(sub_id)).join(Mistake, Mistake.question_id == Question.id).filter(
                Mistake.user_id == current_user.id).distinct().all()
        else:  # 如果指定了题型，则取得当前用户指定科目下的指定题型的错题
            all_question = Question.query.filter_by(subject_id=int(sub_id)).join(Mistake, Mistake.question_id == Question.id).filter(
                Mistake.user_id == current_user.id).distinct().filter(
                Question.qtype_id == int(qtypte_id)).all()
    else:
        if qtypte_id is None:
            all_question = Question.query.filter_by(subject_id=int(sub_id)).all()
        else:
            all_question = Question.query.filter(Question.subject_id == int(sub_id)).filter(
                Question.qtype_id == int(qtypte_id)).all()

    if len(q_id_over_list) > 0:  # 如果有已经做过的题，则需要从备选题列表中删去
        for q in q_id_over_list:  # 把已经联系过的题目去掉
            que = Question.query.filter(Question.id == q).first()
            if que in all_question:
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
    m_list = Mistake.query.filter(Mistake.question_id == before_id).filter(Mistake.user_id == user_id).all()
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
            mis.correct_times = 0
        db.session.add(mis)
        db.session.commit()


def update_exercises(before_id, ex_id, correct):
    """更新Exercise表
    :param before_id, 试题（question）id
    :param exerc, exercise对象
    :param correct,是否正确,boolean
    """

    ex = Exercise.query.filter(Exercise.id == ex_id).first()
    q_list = ex.question_list.split(',')
    if before_id not in q_list:  # 入已经做过相同的题则不计入Exercise
        if ex.result_list is None or ex.question_list is None or ex.result_list == '' or ex.question_list == '':
            q_list_str = str(before_id)
            if correct:
                r_list_str = 'T'
            else:
                r_list_str = 'F'
        else:
            q_list_str = ex.question_list + ',' + str(before_id)
            if correct:
                r_list_str = ex.result_list + 'T'
            else:
                r_list_str = ex.result_list + 'F'

        ex.result_list = r_list_str
        ex.question_list = q_list_str
        db.session.add(ex)
        db.session.commit()
