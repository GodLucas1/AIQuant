from datetime import datetime
from app import db

class Strategy(db.Model):
    """交易策略模型"""
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.Text, nullable=False)  # 策略代码
    parameters = db.Column(db.JSON)  # 策略参数，使用JSON格式存储
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开分享
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    backtests = db.relationship('Backtest', backref='strategy', lazy='dynamic')
    trading_tasks = db.relationship('TradingTask', backref='strategy', lazy='dynamic')
    
    def __repr__(self):
        return f'<Strategy {self.name}>'

class StrategyTemplate(db.Model):
    """策略模板模型"""
    __tablename__ = 'strategy_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    code_template = db.Column(db.Text, nullable=False)  # 模板代码
    default_parameters = db.Column(db.JSON)  # 默认参数
    category = db.Column(db.String(32))  # 策略分类：趋势跟踪、均值回归、套利等
    difficulty = db.Column(db.String(16))  # 难度级别：初级、中级、高级
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StrategyTemplate {self.name}>'