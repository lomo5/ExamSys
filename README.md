# ExamSys
计划：一个根据题库自动生成考卷并记录考试成绩的考试系统。

# 笔记：
1. url_for()函数最简单的用法是以视图函数名(或者 app.add_url_route() 定义路由时使用 的端点名)作为参数，返回对应的 URL。例如，在当前版本的 hello.py 程序中调用 url_ for('index')得到的结果是/。体检工作了吧玩调用url_for('index', _external=True)返回的则是绝对地 址，在这个示例中是 http://localhost:5000/。传入 url_for() 的关键字参数不仅限于动态路由中的参数。函数能将任何额外参数添加到 查询字符串中。例如，url_for('index', page=2)的返回结果是/?page=2。
    1. 注意：生成连接程序内不同路由的链接时，使用相对地址就足够了。如果要生成在浏览器之外使用的链接，则必须使用绝对地址，例如在电子邮件中发送的链接。
2. 点击"login"，在调用full_dispatch_request(self)函数时，try其中的request_started.send(self)和rv = self.preprocess_request()时先后出错（前者在蓝图注册中有auth时，后者在去掉auth后）。
3. 为什么不能再__init__()中动态添加field：WTForms uses a [metaclass](https://github.com/wtforms/wtforms/blob/2.0/wtforms/form.py#L167) to handle binding at instantiation time. This metaclass does its work before Form.__init__ is called, thus making it not possible for something in __init__ to create a field that's bound.[原文地址](https://stackoverflow.com/questions/23594448/wtforms-adding-dynamic-fields-with-multiple-inheritance)
4. 创建数据库表：
    1. 在配置文件中设置数据库链接参数：SQLALCHEMY_DATABASE_URI
    2. 命令行虚拟环境(venv)下执行export FLASK_APP=manage.py，添加环境变量。
    3. 命令行执行flask shell，来打开shell并导入manage.py中make_shell_context()定义的instance。
    4. python中执行db.create_all()创建所有表。
5. 数据迁移（migrate）
    1. 安装模块：(venv) $ pip install flask-migrate
        * 在manage.py中引入模块：from flask_migrate import Migrate
        * manage.py中创建migrate对象：migrate = Migrate(app, db)
            * 前面环境变量设置：export FLASK_APP=manage.py，因此这里是在manage.py中。
    2. 初始化：(venv) $ flask db init
    3. 改动了数据库模型（Models）
    4. 创建脚本：(venv) $ flask db migrate -m "say something to describe the modification"
    5. 检查脚本是否正确（自动生成的脚本可能会有错！！！）
    6. 将创建的脚本纳入版本管理
    7. 升级数据库：(venv) $ flask db upgrade
    8. 如果在升级之前又做了改动，可以回退，然后删除就脚本，重新生成脚本（步骤4）：(venv) $ flask db downgrade
    9. 问题：本地调试的时候，由于没有uwsgi做代理，当前目录即为项目根目录。写文件会写到项目根目录下。上传腾讯云后，写目录变成了/home/www/examsys，此时再用send_file("../" + filename)就会提示文件不存在（uwsgi的log中）
        1. 这是由于：上传到腾讯云后，uwsgi配置文件没有指定项目根目录，默认将是uwsgi的启动目录。这就使运行时，默认当前目录变成了/home/www/examsys,而不是/home/www/examsys/ExamSys
        2. 解决办法：需要在uwsgi的配置文件中添加chdir变量，将当前目录指定为：/home/www/examsys/ExamSys
    10. 下载文件名中文支持：通过将filename编码转为latin-1（server.py里边会严格按照latin-1编码来解析filename），将utf8编码的中文文件名默认转为latin-1编码文件名。
        1. response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        2. 参考：https://stackoverflow.com/questions/47575665/flask-raises-unicodeencodeerror-latin-1-when-send-attachment-with-utf-8-charac

