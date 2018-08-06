from flask import Flask

app = Flask(__name__)
app.debug = True  # 开启调试模式

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

# 注册蓝图时添加等url_prefix将会在使用蓝图时添加到装饰器中的url字段之前
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
