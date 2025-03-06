from datetime import datetime
from abc import ABC, abstractmethod
from app import db
from app.models.market_data import StockData, FuturesData
from app.trading.orders import StockOrder, FuturesOrder, OrderType, OrderDirection
from app.trading.positions import StockPosition, FuturesPosition

class BaseStrategy(db.Model, ABC):
    """策略基类"""
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 策略类型
    strategy_type = db.Column(db.String(32))
    __mapper_args__ = {
        'polymorphic_identity': 'base',
        'polymorphic_on': strategy_type
    }
    
    @abstractmethod
    def on_bar(self, data):
        """K线数据更新时的回调"""
        pass
    
    @abstractmethod
    def on_trade(self, order):
        """成交回调"""
        pass

class BaseStockStrategy(BaseStrategy):
    """股票策略基类"""
    __mapper_args__ = {
        'polymorphic_identity': 'stock'
    }
    
    def place_order(self, stock: StockData, quantity: int, order_type: OrderType,
                    direction: OrderDirection, price: float = None):
        """下单方法"""
        order = StockOrder(
            account_id=self.account_id,
            strategy_id=self.id,
            stock_id=stock.id,
            order_type=order_type,
            direction=direction,
            quantity=quantity,
            price=price
        )
        db.session.add(order)
        db.session.commit()
        return order

class BaseFuturesStrategy(BaseStrategy):
    """期货策略基类"""
    __mapper_args__ = {
        'polymorphic_identity': 'futures'
    }
    
    def place_order(self, futures: FuturesData, quantity: int, order_type: OrderType,
                    direction: OrderDirection, price: float = None, leverage: float = 1.0,
                    stop_price: float = None, take_profit_price: float = None,
                    is_close_position: bool = False):
        """下单方法"""
        # 计算保证金
        margin = futures.last_price * quantity * futures.contract_size * futures.margin_rate / leverage
        
        order = FuturesOrder(
            account_id=self.account_id,
            strategy_id=self.id,
            futures_id=futures.id,
            order_type=order_type,
            direction=direction,
            quantity=quantity,
            price=price,
            margin=margin,
            leverage=leverage,
            stop_price=stop_price,
            take_profit_price=take_profit_price,
            is_close_position=is_close_position
        )
        db.session.add(order)
        db.session.commit()
        return order

class TrendFollowingStrategy(BaseFuturesStrategy):
    """趋势跟踪策略"""
    __mapper_args__ = {
        'polymorphic_identity': 'trend_following'
    }
    
    # 策略参数
    lookback_period = db.Column(db.Integer, default=20)  # 回看周期
    volatility_period = db.Column(db.Integer, default=20)  # 波动率计算周期
    position_size = db.Column(db.Float, default=0.01)  # 仓位大小
    stop_loss_atr = db.Column(db.Float, default=2.0)  # 止损ATR倍数
    
    def on_bar(self, data):
        # 实现趋势跟踪策略逻辑
        pass

class MeanReversionStrategy(BaseFuturesStrategy):
    """均值回归策略"""
    __mapper_args__ = {
        'polymorphic_identity': 'mean_reversion'
    }
    
    # 策略参数
    ma_period = db.Column(db.Integer, default=20)  # 均线周期
    std_period = db.Column(db.Integer, default=20)  # 标准差周期
    entry_std = db.Column(db.Float, default=2.0)  # 入场标准差倍数
    exit_std = db.Column(db.Float, default=0.0)  # 出场标准差倍数
    position_size = db.Column(db.Float, default=0.01)  # 仓位大小
    
    def on_bar(self, data):
        # 实现均值回归策略逻辑
        pass