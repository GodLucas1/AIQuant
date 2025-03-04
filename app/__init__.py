from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
scheduler = BackgroundScheduler()

def create_app(config_class=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.auth import auth_bp
    from app.market_data import market_data_bp
    from app.strategy import strategy_bp
    from app.backtest import backtest_bp
    from app.trading import trading_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(market_data_bp, url_prefix='/api/market-data')
    app.register_blueprint(strategy_bp, url_prefix='/api/strategy')
    app.register_blueprint(backtest_bp, url_prefix='/api/backtest')
    app.register_blueprint(trading_bp, url_prefix='/api/trading')
    
    # 启动定时任务
    with app.app_context():
        from app.tasks import register_tasks
        register_tasks(scheduler)
        scheduler.start()
    
    return app