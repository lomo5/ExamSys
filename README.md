# ExamSys
计划：一个根据题库自动生成考卷并记录考试成绩的考试系统。

# 笔记：
1. url_for()函数最简单的用法是以视图函数名(或者 app.add_url_route() 定义路由时使用 的端点名)作为参数，返回对应的 URL。例如，在当前版本的 hello.py 程序中调用 url_ for('index')得到的结果是/。体检工作了吧玩调用url_for('index', _external=True)返回的则是绝对地 址，在这个示例中是 http://localhost:5000/。传入 url_for() 的关键字参数不仅限于动态路由中的参数。函数能将任何额外参数添加到 查询字符串中。例如，url_for('index', page=2)的返回结果是/?page=2。
    1. 注意：生成连接程序内不同路由的链接时，使用相对地址就足够了。如果要生成在浏览器之外使用的链接，则必须使用绝对地址，例如在电子邮件中发送的链接。
2. 点击"login"，在调用full_dispatch_request(self)函数时，try其中的request_started.send(self)和rv = self.preprocess_request()时先后出错（前者在蓝图注册中有auth时，后者在去掉auth后）。