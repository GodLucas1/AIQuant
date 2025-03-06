from datetime import datetime
from typing import List, Dict, Union
from app import db
from app.models.market_data import StockData, FuturesData, PriceData, FuturesPriceData
from app.trading.orders import StockOrder, FuturesOrder, OrderType, OrderDirection, OrderStatus
from app.trading.positions import StockPosition, FuturesPosition
from app.strategy.base import BaseStrategy

class BacktestEngine:
    """回测引擎"""
    def __init__(self, strategy: BaseStrategy, start_date: datetime, end_date: datetime,
                initial_capital: float = 1000000.0):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Union[StockPosition, FuturesPosition]] = {}
        self.orders: List[Union[StockOrder, FuturesOrder]] = []
        
    def run(self):
        """运行回测"""
        # 获取回测数据
        if self.strategy.strategy_type == 'stock':
            data = PriceData.query.join(StockData).filter(
                PriceData.timestamp.between(self.start_date, self.end_date)
            ).order_by(PriceData.timestamp.asc()).all()
        else:  # futures
            data = FuturesPriceData.query.join(FuturesData).filter(
                FuturesPriceData.timestamp.between(self.start_date, self.end_date)
            ).order_by(FuturesPriceData.timestamp.asc()).all()
        
        # 遍历数据
        for bar in data:
            self.current_timestamp = bar.timestamp
            self._process_orders()  # 处理订单
            self._update_positions(bar)  # 更新持仓
            self.strategy.on_bar(bar)  # 调用策略
    
    def _process_orders(self):
        """处理订单"""
        for order in self.orders:
            if order.status == OrderStatus.PENDING:
                # 模拟订单成交
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.filled_price = order.price
                
                # 更新持仓
                if isinstance(order, StockOrder):
                    self._update_stock_position(order)
                else:  # FuturesOrder
                    self._update_futures_position(order)
                
                # 更新资金
                self._update_capital(order)
                
                # 触发成交回调
                self.strategy.on_trade(order)
    
    def _update_stock_position(self, order: StockOrder):
        """更新股票持仓"""
        symbol = order.stock.symbol
        if symbol not in self.positions:
            self.positions[symbol] = StockPosition(
                account_id=order.account_id,
                strategy_id=order.strategy_id,
                stock_id=order.stock_id
            )
        
        position = self.positions[symbol]
        if order.direction == OrderDirection.BUY:
            position.quantity += order.filled_quantity
            position.average_cost = (
                (position.average_cost * (position.quantity - order.filled_quantity) +
                order.filled_price * order.filled_quantity) / position.quantity
            )
        else:  # SELL
            realized_pnl = (order.filled_price - position.average_cost) * order.filled_quantity
            position.realized_pnl += realized_pnl
            position.quantity -= order.filled_quantity
    
    def _update_futures_position(self, order: FuturesOrder):
        """更新期货持仓"""
        symbol = order.futures.symbol
        if symbol not in self.positions:
            self.positions[symbol] = FuturesPosition(
                account_id=order.account_id,
                strategy_id=order.strategy_id,
                futures_id=order.futures_id
            )
        
        position = self.positions[symbol]
        if order.is_close_position:
            # 平仓操作
            if order.direction == OrderDirection.BUY:
                # 买入平空
                realized_pnl = (position.short_avg_cost - order.filled_price) * order.filled_quantity
                position.realized_pnl += realized_pnl
                position.short_quantity -= order.filled_quantity
                position.short_margin -= order.margin
            else:  # SELL
                # 卖出平多
                realized_pnl = (order.filled_price - position.long_avg_cost) * order.filled_quantity
                position.realized_pnl += realized_pnl
                position.long_quantity -= order.filled_quantity
                position.long_margin -= order.margin
        else:
            # 开仓操作
            if order.direction == OrderDirection.BUY:
                # 买入开多
                position.long_quantity += order.filled_quantity
                position.long_avg_cost = (
                    (position.long_avg_cost * (position.long_quantity - order.filled_quantity) +
                    order.filled_price * order.filled_quantity) / position.long_quantity
                )
                position.long_margin += order.margin
            else:  # SELL
                # 卖出开空
                position.short_quantity += order.filled_quantity
                position.short_avg_cost = (
                    (position.short_avg_cost * (position.short_quantity - order.filled_quantity) +
                    order.filled_price * order.filled_quantity) / position.short_quantity
                )
                position.short_margin += order.margin
    
    def _update_positions(self, bar):
        """更新持仓盈亏"""
        for position in self.positions.values():
            if isinstance(position, StockPosition):
                # 更新股票持仓的未实现盈亏
                if position.quantity > 0:
                    position.unrealized_pnl = (
                        bar.close_price - position.average_cost
                    ) * position.quantity
            else:  # FuturesPosition
                # 更新期货持仓的未实现盈亏
                if position.long_quantity > 0:
                    position.unrealized_pnl = (
                        bar.close_price - position.long_avg_cost
                    ) * position.long_quantity
                if position.short_quantity > 0:
                    position.unrealized_pnl += (
                        position.short_avg_cost - bar.close_price
                    ) * position.short_quantity
    
    def _update_capital(self, order: Union[StockOrder, FuturesOrder]):
        """更新资金"""
        # 计算交易成本
        commission = order.filled_quantity * order.filled_price * 0.0003  # 假设手续费率为0.03%
        self.current_capital -= commission
        order.commission = commission
        
        if isinstance(order, StockOrder):
            # 股票交易资金变动
            if order.direction == OrderDirection.BUY:
                self.current_capital -= order.filled_quantity * order.filled_price
            else:  # SELL
                self.current_capital += order.filled_quantity * order.filled_price
        else:  # FuturesOrder
            # 期货交易资金变动（只考虑保证金）
            if order.is_close_position:
                self.current_capital += order.margin  # 平仓释放保证金
            else:
                self.current_capital -= order.margin  # 开仓占用保证金