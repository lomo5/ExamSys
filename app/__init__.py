from flask import Flask

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment  # 时间本地化
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

app = Flask(__name__)
app.debug = True  # 开启调试模式

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

# 注册蓝图时添加等url_prefix将会在使用蓝图时添加到装饰器中的url字段之前
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
