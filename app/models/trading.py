from app import db
from datetime import datetime


class TradingAccount(db.Model):
    """交易账户模型"""
    __tablename__ = 'trading_accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    account_type = db.Column(db.String(32), nullable=False)  # 账户类型：股票、期货、期权等
    broker = db.Column(db.String(64))  # 券商/经纪商
    account_number = db.Column(db.String(64), unique=True)  # 账户号码
    api_key = db.Column(db.String(128))  # API密钥
    api_secret = db.Column(db.String(256))  # API密钥
    initial_balance = db.Column(db.Float, default=0.0)  # 初始资金
    current_balance = db.Column(db.Float, default=0.0)  # 当前资金
    status = db.Column(db.String(16), default='active')  # active, inactive, suspended
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    orders = db.relationship('TradeOrder', backref='account', lazy='dynamic')
    positions = db.relationship('TradePosition', backref='account', lazy='dynamic')
    trading_tasks = db.relationship('TradingTask', backref='account', lazy='dynamic')

    def __repr__(self):
        return f'<TradingAccount {self.name} {self.account_number}>'


class TradingTask(db.Model):
    """交易任务模型，用于自动化交易"""
    __tablename__ = 'trading_tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('trading_accounts.id'), nullable=False)
    symbols = db.Column(db.JSON)  # 交易的股票代码列表
    parameters = db.Column(db.JSON)  # 策略参数
    schedule = db.Column(db.String(64))  # 执行计划，如 "每日9:30-15:00"
    status = db.Column(db.String(16), default='inactive')  # inactive, active, paused, completed, failed
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    last_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TradingTask {self.name} {self.status}>'


class TradeOrder(db.Model):
    """交易订单模型"""
    __tablename__ = 'trade_orders'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('trading_accounts.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('trading_tasks.id'))  # 可以为空，表示手动下单
    symbol = db.Column(db.String(32), nullable=False)
    order_type = db.Column(db.String(16), nullable=False)  # market, limit, stop, etc.
    side = db.Column(db.String(8), nullable=False)  # buy, sell
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float)  # 限价单的价格
    stop_price = db.Column(db.Float)  # 止损价
    status = db.Column(db.String(16), default='pending')  # pending, filled, partially_filled, canceled, rejected
    filled_quantity = db.Column(db.Float, default=0.0)
    average_fill_price = db.Column(db.Float)
    commission = db.Column(db.Float, default=0.0)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    fill_time = db.Column(db.DateTime)
    cancel_time = db.Column(db.DateTime)
    external_order_id = db.Column(db.String(64))  # 外部订单ID（券商系统）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    task = db.relationship('TradingTask', backref='orders', lazy=True, foreign_keys=[task_id])

    def __repr__(self):
        return f'<TradeOrder {self.symbol} {self.side} {self.quantity} @ {self.price} {self.status}>'


class TradePosition(db.Model):
    """交易持仓模型"""
    __tablename__ = 'trade_positions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('trading_accounts.id'), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    average_cost = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float)
    market_value = db.Column(db.Float)
    unrealized_pnl = db.Column(db.Float)  # 未实现盈亏
    realized_pnl = db.Column(db.Float, default=0.0)  # 已实现盈亏
    open_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('account_id', 'symbol', name='uix_position'),)

    def __repr__(self):
        return f'<TradePosition {self.symbol} {self.quantity} @ {self.average_cost}>'
