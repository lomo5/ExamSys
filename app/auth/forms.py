from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError


# 登录form
class LoginForm(FlaskForm):
    staff_number = StringField('员工编号', validators=[DataRequired(), Length(1, 8)])
    # password = PasswordField('密码', validators=[DataRequired()])
    # # remember_me = BooleanField('记住我的登录状态')
    submit = SubmitField('登录')


# class RegistrationForm(FlaskForm):
#     email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
#                                              Email()])
#     username = StringField('用户名', validators=[
#         DataRequired(), Length(1, 64),
#         Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能由字母、数字、"."或者"_"组成。')])
#
#     password = PasswordField('Password', validators=[
#         DataRequired(), EqualTo('password2', message='Passwords must match.')])
#     password2 = PasswordField('Confirm password', validators=[DataRequired()])
#     submit = SubmitField('Register')
#
#     def validate_email(self, field):
#         if User.query.filter_by(email=field.data).first():
#             raise ValidationError('Email already registered.')
#
#     def validate_username(self, field):
#         if User.query.filter_by(username=field.data).first():
#             raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('原密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码必须相同')])
    password2 = PasswordField('确认新密码',
                              validators=[DataRequired()])
    submit = SubmitField('修改密码')


