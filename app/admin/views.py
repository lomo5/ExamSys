from . import admin  # 导入blueprint

# 虽热此处路由只写了'/'，但是由于蓝图admin注册时添加了'/admin'前缀，因此实际以下路由为'/admin/'
@admin.route('/')
def index():
    return '<h1 style="color:red">This is admin.<h1>'
