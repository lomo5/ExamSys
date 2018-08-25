from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, SubmitField, SelectField, TextAreaField, Label
from wtforms.validators import DataRequired

from ..models import Subject, QuestionType


# todo: 点击提交后如果验证通过，则转到答题页面，同时将subject存入session
# 开始练习
class ExerciseBeginForm(FlaskForm):
    #
    # todo:研究一下：还有这种field：'QuerySelectField', 'QuerySelectMultipleField','QueryRadioField', 'QueryCheckboxField',(网址：https://github.com/wtforms/wtforms-sqlalchemy）
    subject = SelectField('选择专业',
                          coerce=int)  # choices在view中填充；参数”coerce”参数来强制转换选择项值的类型（默认是string，由于id实际上是int类型，因此会导致提交时始终验证不过Not a valid choice
    question_type = SelectField('选择题型', coerce=int)  #, validators=[DataRequired])
    submit = SubmitField('开始')

    # 在初始化Form实例时指定selectField的choices内容。参考：https://blog.csdn.net/agmcs/article/details/45308431
    def __init__(self, *args, **kwargs):
        super(ExerciseBeginForm, self).__init__(*args, **kwargs)
        self.subject.choices = [(subject.id, subject.subject_name) for subject in
                                Subject.query.order_by(Subject.subject_name).all()]
        self.question_type.choices = [(qtype.id, qtype.type_name) for qtype in
                                      QuestionType.query.order_by(QuestionType.type_name).all()]
        # todo:后期加上随机题型的选项

    # 以下是自己原来写的：
    # def __init__(self):
    #     subject_list = Subject.query.all()  # 取得所有subject用来提供给下拉选择框
    #     resp_list = []  #（科目id，科目名）的list
    #     for subject in subject_list:
    #         resp_list.append((subject.id, subject.subject_name))
    #     self.subject = SelectField('选择专业', choices=resp_list)


# todo:开始答题后分两步：
# 1、显示试题和"提交"按钮；如果
# 2、提交后根据对错来决定下一步是显示答案还是继续下一题（继续的话flash显示正确）；同时将答过的题存入session中的一个list中，如果做错则存入错题表中（同时将改错题的错误次数加1）
# 注意：显示答案时，需要将用户的答案显示出来（选择题保持用户的选中状态，填空简答在文本框中显示用户的输入）正确答案另外显示。
# 注意：


# 一个包含所有题型所需field的form，渲染时根据每个field的label是否为空来判断是否显示（或根据传过来的题型），提交的时候不验证是否选了答案，没选就当做错。
class ExercisesForm(FlaskForm):
    # 单选
    single = RadioField('请选择：', choices=None)
    # 多选
    multi1 = BooleanField('')
    multi2 = BooleanField('')
    multi3 = BooleanField('')
    multi4 = BooleanField('')
    multi5 = BooleanField('')
    multi6 = BooleanField('')
    multi7 = BooleanField('')
    multi8 = BooleanField('')
    # 判断
    truefalse = RadioField('请选择：', choices=None)
    # 填空，初始化时根据空格数动态生成
    fill = []
    # 简答
    saq = TextAreaField(render_kw={"placeholder": "答案写在这里"})

    def __init__(self, single_choises=None, multi_num=0, fill_num=0):
        """
        single_choises：单选题radiofield 的choices属性；
        fill_num:填空题的空格数
        multi_num:多选题的选项数
            但是根据官方文档（https://wtforms.readthedocs.io/en/stable/fields.html#field-enclosures）的描述，FieldList不能包含（enclose） BooleanField 或 SubmitField 实例。
            是否意味着BooleanField 和 SubmitField 不能动态创建？
        todo:确定form中能否这样动态生成field！！！！
        """
        self.single = RadioField(choices=single_choises)  # 初始化单选题
        for i in range(fill_num):  # 初始化填空题
            self.fill.append(StringField())


# 单选选择题的选项
class ExerciseSingleForm(FlaskForm):
    # todo:初始选项(choices)为空，view中动态添加choices
    answers = RadioField('请选择：', choices=None, validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        # super(ExerciseSingleForm, self).__init__(*args, **kwargs)
        answer_list = kwargs['question'].options.split('||')
        alph = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        self.answers.choices = list(zip(alph, answer_list))  # 超长对一个list将被截取


# 多选题的选项
class ExerciseMultiChoiceForm(FlaskForm):
    # todo:view中设置每个checkbox的label，template中通过判断label是否为空来决定是否显示某个选项；label前可加上A、B、C、D
    # todo:如何验证用户有没有做选择？至少选中一项
    # multi = []
    # for i in range(0, 8):
    #     multi.append(BooleanField('', default=False))
    multi0 = BooleanField('', default=False)
    multi1 = BooleanField('', default=False)
    multi2 = BooleanField('', default=False)
    multi3 = BooleanField('', default=False)
    multi4 = BooleanField('', default=False)
    multi5 = BooleanField('', default=False)
    multi6 = BooleanField('', default=False)
    multi7 = BooleanField('', default=False)

    submit = SubmitField('提 交')

    # 对于多选，需要在__init__()时传入question对象来初始化field的label属性。
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        # super(ExerciseMultiChoiceForm, self).__init__(**kwargs)  # for python2!  ?????
        if len(kwargs) > 0:
            opt_list = kwargs['question'].options.split('||')
            alph = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
            # ans_list = list(question.answer)  # 把"ABCD"形式的字符串拆成单个字母的list
            for i in range(0, len(opt_list)):  # 为BooleanField添加label
                # self.multi[i].label = alph[i] + '. ' + opt_list[i]
                self['multi' + str(i)].label = Label(self['multi' + str(i)].id,
                                                     alph[i] + '. ' + opt_list[i])  # 显示到页面之后通过控件id来修改label


# 填空题的空
class ExerciseFillForm(FlaskForm):
    # fill = []
    # for i in range(0, 8):  # 定义8个StringField。todo：简单起见，不管空格有没有8个都显示8个空。回头再改！！
    #     fill.append(StringField())
    fill1 = StringField()
    fill2 = StringField()
    fill3 = StringField()
    fill4 = StringField()
    fill5 = StringField()
    fill6 = StringField()
    fill7 = StringField()
    fill8 = StringField()
    submit = SubmitField('提 交')


# 简答题
class ExerciseAnswerForm(FlaskForm):
    ans = TextAreaField()
    submit = SubmitField('提 交')


# 判断
class ExerciseTrueFalseForm(FlaskForm):
    truefalse = RadioField('请选择：', choices=[(True, '对'), (False, '错')])
    submit = SubmitField('提 交')


# 下一题
class ExerciseNextQuestionForm(FlaskForm):
    submit = SubmitField('下一题')
