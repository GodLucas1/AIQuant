from datetime import datetime
from app import db

class BasePosition(db.Model):
    """持仓基类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'))
    quantity = db.Column(db.Integer, default=0)  # 持仓数量
    average_cost = db.Column(db.Float)  # 平均成本
    realized_pnl = db.Column(db.Float, default=0.0)  # 已实现盈亏
    unrealized_pnl = db.Column(db.Float, default=0.0)  # 未实现盈亏
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockPosition(BasePosition):
    """股票持仓"""
    __tablename__ = 'stock_positions'
    
    stock_id = db.Column(db.Integer, db.ForeignKey('stock_data.id'), nullable=False)
    stock = db.relationship('StockData', backref='positions')
    
    def __repr__(self):
        return f'<StockPosition {self.stock.symbol} {self.quantity}>'

class FuturesPosition(BasePosition):
    """期货持仓"""
    __tablename__ = 'futures_positions'
    
    futures_id = db.Column(db.Integer, db.ForeignKey('futures_data.id'), nullable=False)
    futures = db.relationship('FuturesData', backref='positions')
    margin = db.Column(db.Float)  # 保证金
    leverage = db.Column(db.Float, default=1.0)  # 杠杆倍数
    long_quantity = db.Column(db.Integer, default=0)  # 多头持仓
    short_quantity = db.Column(db.Integer, default=0)  # 空头持仓
    long_avg_cost = db.Column(db.Float)  # 多头平均成本
    short_avg_cost = db.Column(db.Float)  # 空头平均成本
    long_margin = db.Column(db.Float, default=0.0)  # 多头保证金
    short_margin = db.Column(db.Float, default=0.0)  # 空头保证金
    
    def __repr__(self):
        return f'<FuturesPosition {self.futures.symbol} L:{self.long_quantity} S:{self.short_quantity}>'