
from flask import Flask
from flask_bootstrap import Bootstrap
# from flask_mail import Mail
from flask_moment import Moment  # 时间本地化
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
# mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


# 工厂函数，根据所选配置（config_name）创建app对象
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化用到的组件（参数为前面创建的app)
    bootstrap.init_app(app)
    # mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.admin import admin as admin_blueprint
    # 注册蓝图时添加等url_prefix将会在使用蓝图时添加到装饰器中的url字段之前
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
