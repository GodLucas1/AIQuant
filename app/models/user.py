from datetime import datetime
from app import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    strategies = db.relationship('Strategy', backref='author', lazy='dynamic')
    backtests = db.relationship('Backtest', backref='user', lazy='dynamic')
    trading_accounts = db.relationship('TradingAccount', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'