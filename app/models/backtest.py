from datetime import datetime
from app import db

class Backtest(db.Model):
    """回测模型"""
    __tablename__ = 'backtests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    initial_capital = db.Column(db.Float, default=100000.0)
    parameters = db.Column(db.JSON)  # 回测参数
    results = db.Column(db.JSON)  # 回测结果
    status = db.Column(db.String(16), default='pending')  # pending, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    trades = db.relationship('BacktestTrade', backref='backtest', lazy='dynamic')
    
    def __repr__(self):
        return f'<Backtest {self.name}>'

class BacktestTrade(db.Model):
    """回测交易记录模型"""
    __tablename__ = 'backtest_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    backtest_id = db.Column(db.Integer, db.ForeignKey('backtests.id'), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    order_type = db.Column(db.String(16))  # market, limit, stop, etc.
    side = db.Column(db.String(8), nullable=False)  # buy, sell
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BacktestTrade {self.symbol} {self.side} {self.quantity} @ {self.price}>'