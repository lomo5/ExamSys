# coding:utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@127.0.0.1:8889/examsys"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True  # 设置为True表示每次请求结束都会自动提交数据库的变动

db = SQLAlchemy(app)


# 用户数据模型
class User(db.Model):
    """用户数据模型"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    staffid=db.Column(db.String(255), unique=True, nullable=False)  # 工号
    username = db.Column(db.String(100), unique=True, index=True, nullable=False)  # 唯一
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobilephone = db.Column(db.String(11), unique=True)
    faceurl = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    addtime=db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())  # 注册时间；index=True表示为该列建索引；
    # db.relationship的第一个参数表示这个关系的另一端是哪个模型。第二个参数为User模型添加了一个userlog属性
    userlogs=db.relationship('Userlog',backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

# 用户登录日志
class UserLog(db.Model):
    __tablename__='userlogs'
    id=db.Column(db.Integer,primary_key=True)
    userid=db.Column(db.Integer,db.ForeignKey('user.id'))
