from app import db, scheduler
from app.models.trading import TradingTask, TradeOrder, TradePosition
from app.models.market_data import StockData, PriceData
from app.models.strategy import Strategy
from datetime import datetime, timedelta
import importlib
import json
import logging
import pytz
import yfinance as yf
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_tasks(scheduler):
    """注册所有定时任务"""
    # 每天更新股票基本数据
    scheduler.add_job(
        update_stock_data,
        'cron',
        day_of_week='mon-fri',
        hour=18,
        minute=0,
        id='update_stock_data'
    )
    
    # 每小时更新活跃股票的价格数据
    scheduler.add_job(
        update_active_stocks_price,
        'cron',
        day_of_week='mon-fri',
        hour='9-16',
        minute=5,
        id='update_active_stocks_price'
    )
    
    # 每分钟检查并执行交易任务
    scheduler.add_job(
        execute_trading_tasks,
        'cron',
        day_of_week='mon-fri',
        hour='9-15',
        minute='*',
        id='execute_trading_tasks'
    )
    
    # 启动调度器
    if not scheduler.running:
        scheduler.start()
    
    logger.info("所有定时任务已注册并启动")

def update_stock_data():
    """更新股票基本数据"""
    logger.info("开始更新股票基本数据")
    try:
        # 获取所有股票
        stocks = StockData.query.all()
        
        for stock in stocks:
            try:
                # 使用yfinance获取最新数据
                ticker = yf.Ticker(stock.symbol)
                info = ticker.info
                
                # 更新股票信息
                stock.name = info.get('shortName', stock.name)
                stock.exchange = info.get('exchange', stock.exchange)
                stock.industry = info.get('industry', stock.industry)
                stock.sector = info.get('sector', stock.sector)
                stock.last_price = info.get('regularMarketPrice', stock.last_price)
                stock.last_update = datetime.now(pytz.utc)
                
                db.session.add(stock)
                logger.info(f"更新股票数据: {stock.symbol}")
            except Exception as e:
                logger.error(f"更新股票 {stock.symbol} 时出错: {str(e)}")
        
        db.session.commit()
        logger.info("股票基本数据更新完成")
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新股票数据时发生错误: {str(e)}")

def update_active_stocks_price():
    """更新活跃股票的价格数据"""
    logger.info("开始更新活跃股票价格数据")
    try:
        # 获取所有活跃交易任务中的股票
        active_tasks = TradingTask.query.filter_by(status='active').all()
        symbols = set()
        
        for task in active_tasks:
            if task.symbols:
                task_symbols = json.loads(task.symbols) if isinstance(task.symbols, str) else task.symbols
                symbols.update(task_symbols)
        
        # 如果没有活跃股票，则退出
        if not symbols:
            logger.info("没有活跃股票需要更新")
            return
        
        # 获取这些股票的最新价格
        for symbol in symbols:
            try:
                stock = StockData.query.filter_by(symbol=symbol).first()
                if not stock:
                    logger.warning(f"股票 {symbol} 不存在于数据库中")
                    continue
                
                # 使用yfinance获取最新数据
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if hist.empty:
                    logger.warning(f"无法获取股票 {symbol} 的价格数据")
                    continue
                
                # 获取最新价格
                latest = hist.iloc[-1]
                
                # 更新股票最新价格
                stock.last_price = latest['Close']
                stock.last_update = datetime.now(pytz.utc)
                
                # 添加到价格历史数据
                price_data = PriceData(
                    stock_id=stock.id,
                    timestamp=datetime.now(pytz.utc),
                    open_price=latest['Open'],
                    high_price=latest['High'],
                    low_price=latest['Low'],
                    close_price=latest['Close'],
                    volume=latest['Volume'],
                    interval='1h'
                )
                
                db.session.add(stock)
                db.session.add(price_data)
                logger.info(f"更新股票价格: {symbol}, 价格: {latest['Close']}")
            except Exception as e:
                logger.error(f"更新股票 {symbol} 价格时出错: {str(e)}")
        
        db.session.commit()
        logger.info("活跃股票价格数据更新完成")
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新股票价格数据时发生错误: {str(e)}")

def execute_trading_tasks():
    """执行所有活跃的交易任务"""
    logger.info("开始执行交易任务")
    try:
        # 获取所有活跃的交易任务
        active_tasks = TradingTask.query.filter_by(status='active').all()
        
        for task in active_tasks:
            try:
                # 检查是否在交易时间范围内
                if task.schedule and not is_in_schedule(task.schedule):
                    continue
                
                # 获取策略
                strategy = Strategy.query.get(task.strategy_id)
                if not strategy:
                    logger.error(f"任务 {task.id} 的策略不存在")
                    continue
                
                # 获取交易账户
                account = task.account
                if not account or account.status != 'active':
                    logger.error(f"任务 {task.id} 的交易账户不可用")
                    continue
                
                # 执行策略
                execute_strategy(task, strategy, account)
                
                # 更新任务最后执行时间
                task.last_run = datetime.now(pytz.utc)
                db.session.add(task)
            except Exception as e:
                logger.error(f"执行任务 {task.id} 时出错: {str(e)}")
        
        db.session.commit()
        logger.info("交易任务执行完成")
    except Exception as e:
        db.session.rollback()
        logger.error(f"执行交易任务时发生错误: {str(e)}")

def execute_strategy(task, strategy, account):
    """执行单个交易策略"""
    try:
        # 解析策略参数
        parameters = json.loads(task.parameters) if isinstance(task.parameters, str) else task.parameters
        symbols = json.loads(task.symbols) if isinstance(task.symbols, str) else task.symbols
        
        # 动态导入并执行策略代码
        strategy_code = compile(strategy.code, f"strategy_{strategy.id}", 'exec')
        strategy_namespace = {}
        exec(strategy_code, strategy_namespace)
        
        # 检查策略是否定义了generate_signals函数
        if 'generate_signals' not in strategy_namespace:
            logger.error(f"策略 {strategy.id} 没有定义generate_signals函数")
            return
        
        # 为每个股票获取数据并生成信号
        for symbol in symbols:
            # 获取股票数据
            stock = StockData.query.filter_by(symbol=symbol).first()
            if not stock:
                logger.warning(f"股票 {symbol} 不存在于数据库中")
                continue
            
            # 获取历史价格数据
            price_history = PriceData.query.filter_by(
                stock_id=stock.id
            ).order_by(PriceData.timestamp.desc()).limit(100).all()
            
            if not price_history:
                logger.warning(f"股票 {symbol} 没有足够的历史数据")
                continue
            
            # 转换为DataFrame
            df = pd.DataFrame([
                {
                    'timestamp': p.timestamp,
                    'open': p.open_price,
                    'high': p.high_price,
                    'low': p.low_price,
                    'close': p.close_price,
                    'volume': p.volume
                } for p in price_history
            ])
            df = df.sort_values('timestamp')
            
            # 调用策略生成信号
            signals = strategy_namespace['generate_signals'](df, parameters)
            
            if not signals or signals.empty:
                logger.info(f"股票 {symbol} 没有生成交易信号")
                continue
            
            # 处理最新的信号
            latest_signal = signals.iloc[-1]
            process_trading_signal(task, account, symbol, latest_signal)
    except Exception as e:
        logger.error(f"执行策略 {strategy.id} 时出错: {str(e)}")

def process_trading_signal(task, account, symbol, signal):
    """处理交易信号"""
    try:
        # 获取当前持仓
        position = TradePosition.query.filter_by(
            account_id=account.id,
            symbol=symbol
        ).first()
        
        # 获取股票当前价格
        stock = StockData.query.filter_by(symbol=symbol).first()
        if not stock or not stock.last_price:
            logger.error(f"无法获取股票 {symbol} 的价格信息")
            return
        
        current_price = stock.last_price
        
        # 根据信号类型处理
        if signal['action'] == 'buy' and (not position or position.quantity == 0):
            # 计算购买数量
            available_funds = account.current_balance * 0.95  # 保留5%资金作为缓冲
            quantity = min(signal.get('quantity', 0), int(available_funds / current_price))
            
            if quantity <= 0:
                logger.warning(f"账户 {account.id} 资金不足，无法购买 {symbol}")
                return
            
            # 创建买入订单
            order = TradeOrder(
                account_id=account.id,
                task_id=task.id,
                symbol=symbol,
                order_type='market',
                side='buy',
                quantity=quantity,
                price=current_price,
                status='filled',  # 简化处理，实际应用中应该有更复杂的订单执行逻辑
                filled_quantity=quantity,
                average_fill_price=current_price,
                commission=calculate_commission(quantity, current_price),
                order_time=datetime.now(pytz.utc),
                fill_time=datetime.now(pytz.utc)
            )
            
            # 更新账户余额
            total_cost = quantity * current_price + order.commission
            account.current_balance -= total_cost
            
            # 更新或创建持仓
            if not position:
                position = TradePosition(
                    account_id=account.id,
                    symbol=symbol,
                    quantity=quantity,
                    average_cost=current_price,
                    current_price=current_price,
                    market_value=quantity * current_price,
                    unrealized_pnl=0.0,
                    open_date=datetime.now(pytz.utc)
                )
            else:
                position.quantity = quantity
                position.average_cost = current_price
                position.current_price = current_price
                position.market_value = quantity * current_price
                position.unrealized_pnl = 0.0
                position.last_update = datetime.now(pytz.utc)
            
            db.session.add(order)
            db.session.add(account)
            db.session.add(position)
            logger.info(f"创建买入订单: {symbol}, 数量: {quantity}, 价格: {current_price}")
            
        elif signal['action'] == 'sell' and position and position.quantity > 0:
            # 计算卖出数量
            quantity = min(signal.get('quantity', position.quantity), position.quantity)
            
            if quantity <= 0:
                logger.warning(f"账户 {account.id} 没有持仓 {symbol}，无法卖出")
                return
            
            # 创建卖出订单
            order = TradeOrder(
                account_id=account.id,
                task_id=task.id,
                symbol=symbol,
                order_type='market',
                side='sell',
                quantity=quantity,
                price=current_price,
                status='filled',  # 简化处理
                filled_quantity=quantity,
                average_fill_price=current_price,
                commission=calculate_commission(quantity, current_price),
                order_time=datetime.now(pytz.utc),
                fill_time=datetime.now(pytz.utc)
            )
            
            # 计算收益
            proceeds = quantity * current_price - order.commission
            realized_pnl = proceeds - (position.average_cost * quantity)
            
            # 更新账户余额
            account.current_balance += proceeds
            
            # 更新持仓
            position.quantity -= quantity
            position.realized_pnl += realized_pnl
            
            if position.quantity > 0:
                # 更新剩余持仓的市场价值和未实现盈亏
                position.current_price = current_price
                position.market_value = position.quantity * current_price
                position.unrealized_pnl = position.market_value - (position.average_cost * position.quantity)
                position.last_update = datetime.now(pytz.utc)
            else:
                # 如果全部卖出，则清空持仓
                position.current_price = 0
                position.market_value = 0
                position.unrealized_pnl = 0
                position.last_update = datetime.now(pytz.utc)
            
            db.session.add(order)
            db.session.add(account)
            db.session.add(position)
            logger.info(f"创建卖出订单: {symbol}, 数量: {quantity}, 价格: {current_price}")
    except Exception as e:
        logger.error(f"处理交易信号时出错: {str(e)}")

def calculate_commission(quantity, price):
    """计算交易佣金"""
    # 简化的佣金计算，实际应用中可能更复杂
    # 假设佣金为交易金额的0.1%，最低5元
    commission = max(5.0, quantity * price * 0.001)
    return commission

def is_in_schedule(schedule):
    """检查当前时间是否在交易计划时间范围内"""
    try:
        # 解析时间范围，格式如 "每日9:30-15:00"
        if not schedule or '每日' not in schedule:
            return False
        
        # 提取时间范围
        time_range = schedule.split('每日')[1].strip()
        start_time_str, end_time_str = time_range.split('-')
        
        # 解析时间
        start_hour, start_minute = map(int, start_time_str.split(':'))
        end_hour, end_minute = map(int, end_time_str.split(':'))
        
        # 获取当前时间
        now = datetime.now(pytz.utc)
        china_tz = pytz.timezone('Asia/Shanghai')
        now_china = now.astimezone(china_tz)
        
        # 创建今天的开始和结束时间
        start_time = china_tz.localize(
            datetime(now_china.year, now_china.month, now_china.day, start_hour, start_minute)
        )
        end_time = china_tz.localize(
            datetime(now_china.year, now_china.month, now_china.day, end_hour, end_minute)
        )
        
        # 检查当前时间是否在范围内
        return start_time <= now_china <= end_time
    except Exception as e:
        logger.error(f"解析交易时间表时出错: {str(e)}")
        return False