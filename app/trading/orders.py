from datetime import datetime
from enum import Enum
from app import db

class OrderType(Enum):
    """订单类型"""
    MARKET = 'market'  # 市价单
    LIMIT = 'limit'    # 限价单
    STOP = 'stop'      # 止损单
    STOP_LIMIT = 'stop_limit'  # 止损限价单

class OrderStatus(Enum):
    """订单状态"""
    PENDING = 'pending'      # 待处理
    SUBMITTED = 'submitted'  # 已提交
    FILLED = 'filled'        # 已成交
    CANCELLED = 'cancelled'  # 已取消
    REJECTED = 'rejected'    # 已拒绝
    EXPIRED = 'expired'      # 已过期

class OrderDirection(Enum):
    """订单方向"""
    BUY = 'buy'        # 买入
    SELL = 'sell'      # 卖出

class BaseOrder(db.Model):
    """订单基类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'))
    order_type = db.Column(db.Enum(OrderType))
    direction = db.Column(db.Enum(OrderDirection), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    price = db.Column(db.Float)  # 限价单价格
    quantity = db.Column(db.Integer, nullable=False)
    filled_quantity = db.Column(db.Integer, default=0)
    filled_price = db.Column(db.Float)  # 成交均价
    commission = db.Column(db.Float, default=0.0)  # 手续费
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockOrder(BaseOrder):
    """股票订单"""
    __tablename__ = 'stock_orders'
    
    stock_id = db.Column(db.Integer, db.ForeignKey('stock_data.id'), nullable=False)
    stock = db.relationship('StockData', backref='orders')

class FuturesOrder(BaseOrder):
    """期货订单"""
    __tablename__ = 'futures_orders'
    
    futures_id = db.Column(db.Integer, db.ForeignKey('futures_data.id'), nullable=False)
    futures = db.relationship('FuturesData', backref='orders')
    margin = db.Column(db.Float)  # 保证金
    leverage = db.Column(db.Float, default=1.0)  # 杠杆倍数
    stop_price = db.Column(db.Float)  # 止损价格
    take_profit_price = db.Column(db.Float)  # 止盈价格
    is_close_position = db.Column(db.Boolean, default=False)  # 是否平仓单