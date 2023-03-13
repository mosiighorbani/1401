import os 



class Config(object):
    # ========================================================================================
    # SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456789@localhost/dashboard"
    # SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SQLALCHEMY_TRACK_MODIFICATIONS = "False"
    # SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE')
    # SQLALCHEMY_MAX_OVERFLOW = os.getenv('SQLALCHEMY_MAX_OVERFLOW')
    # SQLALCHEMY_PRE_PING = os.getenv('SQLALCHEMY_PRE_PING')
    # SQLALCHEMY_RECYCLE = os.getenv('SQLALCHEMY_RECYCLE')
    # ========================================================================================
    UPLOAD_DIR = os.path.curdir + '/static/uploads/'
    # SECRET_KEY = os.getenv('SECRET_KEY')
    SECRET_KEY = "my_name_is_mostafa_ghorbani"
    # ========================================================================================
    MAIL_SERVER = os.getenv('MAIL_SERVER') 
    MAIL_PORT = os.getenv('MAIL_PORT') 
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') 
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') 
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') 
    # ========================================================================================
    GITHUB_OAUTH_CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID')
    GITHUB_OAUTH_CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')
    CSRF_ENABLED = os.getenv('CSRF_ENABLED')
     # ========================================================================================
    CKEDITOR_PKG_TYPE = os.getenv('CKEDITOR_PKG_TYPE')
    CKEDITOR_SERVE_LOCAL = os.getenv('CKEDITOR_SERVE_LOCAL')
    CKEDITOR_LANGUAGE = os.getenv('CKEDITOR_LANGUAGE')
    CKEDITOR_FILE_UPLOADER = os.getenv('CKEDITOR_FILE_UPLOADER')


    # UPLOAD_FOLDER = ''
    # MAX_CONTENT_PATH = ''
    





class Development(Config):
    DEBUG = True




class Production(Config):
    DEBUG = False
    