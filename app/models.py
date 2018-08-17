# coding:utf-8

from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


# app = Flask(__name__)  # 实例化app对象
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@127.0.0.1:8889/examsys"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# # app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True  # 设置为True表示每次请求结束都会自动提交数据库的变动


class Role(db.Model):
    """用户角色：admins，表示管理员。user，表示普通用户"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    # 关系、外键：
    users = db.relationship('User', backref='role', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Role %r>' % self.name


class Department(db.Model):
    """用户所在部门"""
    __tablename__='departments'
    id=db.Column(db.Integer, primary_key=True)
    department_name=db.Column(db.String(100), nullable=False)
    # 关系、外键：
    users = db.relationship('User', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Department %r>' % self.name


# # department和subject表的多对多关系中间表。说明：为了简化目前的需求，暂时不关联科目表。
# departmentsubject = db.Table('departmentsubject',
#                              db.Column('department_id', db.Integer, db.ForeignKey('departments.id')),
#                              db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id')))


class Subject(db.Model):
    """科目"""
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)
    # 关系、外键：
    questions = db.relationship('Question', backref='subject', lazy='dynamic',
                                cascade='all, delete-orphan')  # 关系：多对一/试题
    papers = db.relationship('Paper', backref='subject', lazy='dynamic', cascade='all, delete-orphan')  # 关系：多对一/试卷
    # # 为了简化目前的需求，暂时不关联部门表：
    # departments = db.relationship('Department',
    #                               secondary=departmentsubject,
    #                               backref=db.backref('subjects', lazy='dynamic'),
    #                               lazy='dynamic'
    #                               )

    def __repr__(self):
        return '<Subject %r>' % self.name


#
# class UserLog(db.Model):
#     """用户登录日志条目"""
#     __tablename__ = 'userlogs'
#     id = db.Column(db.Integer, primary_key=True)
#     ip = db.Column(db.String, nullable=True)  # 登录ip
#     # 注意，datetime.utcnow后面没有()，因为db.Column()的default参数可以接受函数作为默认值，所以每次需要生成默认值时，db.Column()都会调用指定的函数。
#     login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 登陆时间
#     # 关系、外键：
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 用户id


# 用户数据模型
class User(UserMixin, db.Model):
    """用户数据模型"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    staff_number = db.Column(db.String(255), index=True, unique=True, nullable=False)  # 工号
    username = db.Column(db.String(100), unique=True, index=True, nullable=False)  # 唯一
    password_hash = db.Column(db.String(100), nullable=False)  # 密码
    email = db.Column(db.String(100), nullable=True)
    mobile_phone = db.Column(db.String(11), nullable=True)  # 手机号
    face_url = db.Column(db.String(255), nullable=True)  # 头像网址
    info = db.Column(db.Text, nullable=True)  # 信息
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow,
                         nullable=False)  # 注册时间；index=True表示为该列建索引；
    last_time = db.Column(db.DateTime(), default=datetime.utcnow)  # 上次登陆时间
    # 关系、外键：
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 角色ID
    department_id=db.Column(db.Integer, db.ForeignKey('departments.id'))  # 部门id
    # db.relationship给User添加了userlogs属性
    # db.relationship的第一个参数表示这个关系的另一端是哪个模型。backref参数为UserLog模型添加了一个user属性
    # db.relationship一般放在"一对多"关系的"一"这一边
    # user_logs = db.relationship('UserLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 关系：一对多/该用户的登录日志
    created_papers = db.relationship('Paper', backref='create_user', lazy='dynamic')  # 关系：一对多/该用户创建的试卷
    scores = db.relationship('Score', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 关系：一对多/成绩
    mistakes = db.relationship('Mistake', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 关系：一对多/错题

    # 计算密码散列值的函数通过名为 password 的只写属性实现。设定这个属性的值时，赋值方法会调用 Werkzeug 提供的 generate_password_hash() 函数
    # ，并把得到的结果赋值给password_hash 字段。如果试图读取 password 属性的值，则会返回错误。
    @property
    def password(self):
        raise AttributeError('密码是不可读属性！')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码的函数，如果返回True表示密码正确。
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 刷新用户的最后访问时间
    def ping(self):
        self.last_time = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.name


# 回调函数，用于从会话中存储的用户 ID 重新加载用户对象。它应该接受一个用户的 unicode ID 作为参数，并且返回相应的用户对象。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class QuestionType(db.Model):
    """题型"""
    __tablename__ = 'questiontypes'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), nullable=False, unique=True)  # 题型：单选、多选、不定项选择题、判断题、填空题（有序填空/无序填空）、简答
    # 关系、外键：
    questions = db.relationship('Question', backref='question_type', lazy='dynamic')  # 关系：一对多/试题

    def __repr__(self):
        return '<QuestionType %r>' % self.name


class Question(db.Model):
    """试题
    说明:
    1、对于判断题：
       用一位二进制数表示对错
    2、对于选择题：
       此列为以特殊字符分开的字串（或干脆用4位二进制数表示，对应位为0为错，为1为对）
    3、对于填空题：
       为用特殊符号分割的字串
       如果存在多个可能答案，则用&&之类的特定符号链接
    4、对于答案的分离处理及显示格式，均由前台来处理
    5、对于简答题，直接存储答案。
    """
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)  # 题干
    answer = db.Column(db.Text, nullable=False)  # 答案
    pic_url = db.Column(db.Text, nullable=True)  # 关联图片链接
    add_time = db.Column(db.DateTime, default=datetime.utcnow)  # 添加时间
    # 关系、外键：
    qtype_id = db.Column(db.Integer, db.ForeignKey('questiontypes.id'))  # 外键：题型
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))  # 外键：科目
    mistakes = db.relationship('Mistake', backref='question', lazy='dynamic')  # 关系：一对多/错题

    def __repr__(self):
        return '<Question %r>' % self.name


# 试卷、试题关联表。在多对多关系中，用来关联paper表和question表的helper表，我们不需要关心这张表，因为这张表将会由SQLAlchemy接管，
# 它唯一的作用是作为papers表和questions表关联表，所以必须在db.relationship()中指出sencondary关联表参数。
paperquestion = db.Table('paperquestion', db.Column('paper_id', db.Integer, db.ForeignKey('papers.id')),
                         db.Column('question_id', db.Integer, db.ForeignKey('questions.id')))


class Paper(db.Model):
    """试卷"""
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)  # 添加时间
    # 关系、外键：
    create_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 外键：创建用户id
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))  # 外键：科目
    scores = db.relationship('Score', backref='paper', lazy='dynamic', cascade='all, delete-orphan')  # 关系：多对一/成绩
    '''
    paperquestion表由db.Table声明，我们不需要关心这张表，因为这张表将会由SQLAlchemy接管，
    它唯一的作用是作为papers表和questions表关联表，所以必须在db.relationship()
    中指出sencondary关联表参数。
    '''
    questions = db.relationship('Question',
                                secondary=paperquestion,
                                backref=db.backref('papers', lazy='dynamic'),
                                lazy='dynamic'
                                )
    mistakes = db.relationship('Mistake', backref='paper', lazy='dynamic')

    def __repr__(self):
        return '<Paper %r>' % self.name


class Score(db.Model):
    """成绩"""
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)  # 成绩
    begin_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)  # 开始考试时间
    end_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)  # 结束考试时间
    # 关系、外键：
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'))  # 外键：试卷id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键：用户id

    def __repr__(self):
        return '<Score %r>' % self.name


class Mistake(db.Model):
    """错题
    与用户为多对一关系，与试卷为多对一关系，与试题为多对一关系。
    """
    __tablename__ = 'mistakes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键：用户id
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'))  # 外键：试卷id
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))  # 外键：试题id

    def __repr__(self):
        return '<Mistake %r>' % self.name
