from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ..models import User, Department, Role, Subject


class AddUserForm(FlaskForm):
    """新增用户Form"""
    staff_number_add = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    email_add = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username_add = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    # coerce，参考：https://stackoverflow.com/questions/13964152/not-a-valid-choice-for-dynamic-select-field-wtforms
    department_add = SelectField('部门', coerce=int, validators=[DataRequired()])
    role_add = SelectField('角色', coerce=int, validators=[DataRequired()])
    password_add = PasswordField('密码', validators=[DataRequired(),
                                                   EqualTo('password2_add', message='两次输入的密码必须相同。')])
    password2_add = PasswordField('确认密码', validators=[DataRequired()])
    submit_add = SubmitField('新增用户')

    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_email_add(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册！')

    def validate_username_add(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被占用！')

    def validate_staff_number_add(self, field):
        if User.query.filter_by(staff_number=field.data).first():
            raise ValidationError('该工号已注册！')

    # 在初始化Form实例时指定selectField的choices内容。参考：https://blog.csdn.net/agmcs/article/details/45308431
    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.department_add.choices = [(department.id, department.department_name) for department in
                                       Department.query.order_by(Department.department_name).all()]
        self.role_add.choices = [(role.id, role.role_name) for role in Role.query.order_by(Role.role_name).all()]


class ModifyUserForm(FlaskForm):
    """修改用户信息"""
    staff_number_modify = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    username_modify = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    email_modify = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    department_modify = SelectField('部门', coerce=int, validators=[DataRequired()])
    role_modify = SelectField('角色', coerce=int , validators=[DataRequired()])
    submit_modify = SubmitField('修改信息')

    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def vlidate_staff_number_modify(self, field):
        user = User.query.filter_by(staff_id=field.data).first()
        if user is None:
            raise ValidationError('该用户名不存在！')

    def validate_email_modify(self, field):
        if User.query.filter(User.email==field.data, User.staff_number != self.staff_number_modify.data).first():
            raise ValidationError('该邮箱已被占用！')

    def validate_username_modify(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            raise ValidationError('该用户名不存在！')
        if user.staff_number != self.staff_number_modify.data:
            raise ValidationError('该用户名与工号不匹配！')

    # 在初始化Form实例时指定selectField的choices内容。参考：https://blog.csdn.net/agmcs/article/details/45308431
    def __init__(self, *args, **kwargs):
        super(ModifyUserForm, self).__init__(*args, **kwargs)
        self.department_modify.choices = [(department.id, department.department_name) for department in
                                          Department.query.order_by(Department.department_name).all()]
        self.role_modify.choices = [(role.id, role.role_name) for role in Role.query.order_by(Role.role_name).all()]


class DeleteUserForm(FlaskForm):
    """删除用户"""
    staff_number_delete = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    username_delete = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    department_delete = SelectField('部门', coerce=int, validators=[DataRequired()])
    submit_delete = SubmitField('删除员工')

    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_staff_number_delete(self, field):
        user = User.query.filter_by(staff_number=field.data).first()
        if user is None:
            raise ValidationError('该用户名不存在！')
        if field.data == '11111111':
            raise ValidationError('该工号为管理员，不能删除！')

    def validate_username_delete(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            raise ValidationError('该用户名不存在！')
        if field.data == 'admin':
            raise ValidationError('admin管理员为超级用户，不能删除！')
        if user.staff_number != self.staff_number_delete.data:
            raise ValidationError('该用户名与工号不匹配！')

    def validate_department_delete(self, field):
        users = User.query.filter(User.staff_number==self.staff_number_delete.data, User.department_id==int(field.data)).all()
        if len(users) == 0:
            raise ValidationError('所选部门无法找到该工号！')

    # 在初始化Form实例时指定selectField的choices内容。参考：https://blog.csdn.net/agmcs/article/details/45308431
    def __init__(self, *args, **kwargs):
        super(DeleteUserForm, self).__init__(*args, **kwargs)
        self.department_delete.choices = [(department.id, department.department_name) for department in
                                       Department.query.order_by(Department.department_name).all()]


class ChangePwdForm(FlaskForm):
    """修改密码"""
    staff_number_change = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    username_change = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    password_change = PasswordField('密码', validators=[DataRequired(),
                                                      EqualTo('password2_change', message='两次输入的密码必须相同。')])
    password2_change = PasswordField('确认密码', validators=[DataRequired()])
    submit_change = SubmitField('修改密码')

    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_staff_number_change(self, field):
        if not User.query.filter_by(staff_number=field.data).first():
            raise ValidationError('该工号不存在！')

    def validate_username_change(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名不存在！')
        if User.query.filter_by(username=field.data).first().staff_number != self.staff_number_change.data:
            raise ValidationError('用户名与工号不匹配！')


class AdminReport(FlaskForm):
    """管理员报表"""
    period = SelectField('统计周期', validators=[DataRequired()], choices=[('D', '今天'), ('W', '本周'), ('M', '本月')])
    unit = SelectField('统计单位', validators=[DataRequired()], choices=[('department', '部门'), ('individual', '个人')])
    submit = SubmitField('生成报表')


class CreatePaper(FlaskForm):
    """创建试卷"""
    title = StringField('试卷名称', validators=[DataRequired()])
    subject = SelectField('选择专业',
                          coerce=int)  # choices在view中填充；参数”coerce”参数来强制转换选择项值的类型（默认是string，由于id实际上是int类型，因此会导致提交时始终验证不过Not a valid choice
    question_type = SelectField('选择题型', coerce=int)  # , validators=[DataRequired])
    single = BooleanField('单选题', default=True)
    multi = BooleanField('多选题', default=False)
    tf = BooleanField('判断题', default=False)
    fill = BooleanField('填空题', default=False)
    saq = BooleanField('简答题', default=False)
    single_count = StringField('数量', default=0, coerce=int)
    multi_count = StringField('数量', default=0, coerce=int)
    tf_count = StringField('数量', default=0, coerce=int)
    fill_count = StringField('数量', default=0, coerce=int)
    saq_count = StringField('数量', default=0, coerce=int)
    single_score = StringField('每题分值', default=0, coerce=int)
    multi_score = StringField('每题分值', default=0, coerce=int)
    tf_score = StringField('每题分值', default=0, coerce=int)
    fill_score = StringField('每题分值', default=0, coerce=int)
    saq_score = StringField('每题分值', default=0, coerce=int)
    # total_score = StringField('总分', validators=[DataRequired()])
    departments = SelectMultipleField('部门', validators=[DataRequired()])
    submit = SubmitField('生成试卷')

    # 在初始化Form实例时指定selectField的choices内容。参考：https://blog.csdn.net/agmcs/article/details/45308431
    def __init__(self, *args, **kwargs):
        super(CreatePaper, self).__init__(*args, **kwargs)
        # self.subject.choices = [(subject.id, subject.subject_name) for subject in
        #                         Subject.query.order_by(Subject.subject_name).all()]
        depart_list = list()
        depart_list.append((0, '所有部门'))  # 表示不限定题型，随机选
        tmp_dpart_list = [(depart.id, depart.department_name) for depart in
                      Department.query.order_by(Department.department_name).all()]
        depart_list.append(tmp_dpart_list)
        self.departments.choices = depart_list


class ReleasePaper(FlaskForm):
    """发布试卷"""
    submit = SubmitField('发布试卷')


