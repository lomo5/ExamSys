from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ..models import User


# 用户管理界面
class UserManageForm(FlaskForm):
    staff_number = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    department = SelectField('部门', validators=[DataRequired()])
    role = SelectField('角色', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(),
                                               EqualTo('password2', message='两次输入的密码必须相同。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被占用！')

    def validate_staff_number(self, field):
        if User.query.filter_by(staff_number=field.data).first():
            raise ValidationError('该工号已注册！')


class AdminReport(FlaskForm):
    """管理员报表"""
    period = SelectField('统计周期', validators=[DataRequired()], choices=[('D', '今天'), ('W', '本周'), ('M', '本月')])
    unit = SelectField('统计单位', validators=[DataRequired()], choices=[('department', '部门'), ('individual', '个人')])
    submit = SubmitField('生成报表')
