from . import home  # 导入blueprint


@home.route('/')
def index():
    return '<h1 style="color:green">Hello world!<h1>'
