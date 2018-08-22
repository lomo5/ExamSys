from flask_migrate import Migrate  # 数据库迁移
from flask_script import Manager  # 旧版的实现命令行的程序包
import os
from app import create_app, db
from app.models import User, Role, Subject, QuestionType, Question, Paper, Score, Mistake


app = create_app(os.getenv('FLASK_CONFIG') or 'default')  # 以默认配置启动，如果存在操作系统环境变量中，则使用create_app(os.getenv('FLASK_CONFIG') or 'default')


# 命令行参数。
# 使用命令行前需要现在虚拟环境下执行export FLASK_APP=manage.py，添加环境变量。
# 然后才能通过flask shell来打开shell并导入以下dict中的instance。
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Subject=Subject,
                QuestionType=QuestionType, Question=Question, Paper=Paper, Score=Score, Mistake=Mistake)


# 以下内容为旧版的以flask-script实现的命令行：
# manager = Manager(app)
# migrate = Migrate(app, db)
# def make_shell_context():
#     return dict(app=app, db=db, User=User, Role=Role, Subject=Subject,
#                 QuestionType=QuestionType, Question=Question, Paper=Paper, Score=Score, Mistake=Mistake)
# # Shell命令会开启一个Python shell，可以传入一个make_context作为参数（必须是一个可调用函数并返回一个字典），一般情况都是返回一些你的Flask程序中的instance
# # 为命令行添加shell参数，并为其添加上下文
# manager.add_command("shell", Shell(make_context=make_shell_context))
# # 为命令行添加db参数
# manager.add_command('db', MigrateCommand)

