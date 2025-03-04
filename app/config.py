import os
from datetime import timedelta

class BaseConfig:
    """基础配置类"""
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    )
    
    # 应用配置
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'csrf_dev_secret_key')

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class TestingConfig(BaseConfig):
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境特定配置
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """根据环境变量获取对应的配置类"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])