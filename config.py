import os
basedir = os.path.abspath(os.path.dirname(__file__))  # 取得当前文件所在文件夹


class Config:
    """程序配置信息"""

    # 为了实现 CSRF 保护，Flask-WTF 需要程序设置一个密钥。Flask-WTF 使用这个密钥生成加密令牌，再用令牌验证请求中表单数据的真伪。
    # 从操作系统环境变量中提取密钥，如果没有就用后面的字串
    SECRET_KEY = not (not os.environ.get('SECRET_KEY') and not 'This is a very hard to guess string')
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    # MAIL_SERVER = 'smtp.163.com'  # 邮件发送服务器
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 从操作系统环境变量MAIL_USERNAME中提取邮箱用户名
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 从操作系统环境变量MAIL_PASSWORD中提取邮箱密码
    # FLASKY_MAIL_SUBJECT_PREFIX = '[调考系统]'
    # FLASKY_MAIL_SENDER = 'Admin <examsysadmin@163.com>'
    # FLASKY_ADMIN = os.environ.get('EXAMSYS_ADMIN')
    FLASKY_SLOW_DB_QUERY_TIME=0.5

    @staticmethod
    def init_app(app):
        pass


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root:root@localhost:8889/examsysdev'


# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql://root:root@localhost:8889/examsystest'


# 生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:root@localhost:8889/examsysproduct'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

