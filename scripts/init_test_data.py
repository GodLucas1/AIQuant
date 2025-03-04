import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
# 先加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # 加载项目根目录下的.env文件

from app import create_app, db
from app.models.user import User
from app.models.market_data import DataSource, StockData, PriceData
from app.models.strategy import Strategy, StrategyTemplate
from app.models.backtest import Backtest, BacktestTrade
from app.models.trading import TradingAccount
from app.models.trading import TradingTask, TradeOrder, TradePosition

# 添加这一行来指定哈希方法和盐长度
def create_password_hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
def init_test_data():
    """初始化测试数据"""
    # 创建测试用户
#
#     test_user = User(
#         username='test_user',
#         email='test@example.com',
#         password_hash=create_password_hash('password123'),
#         is_active=True
#     )
#     db.session.add(test_user)
#     db.session.commit()
#
#     # 创建数据源
#     yahoo_finance = DataSource(
#         name='Yahoo Finance',
#         description='雅虎财经数据源',
#         api_key='demo_key',
#         is_active=True
#     )
#     db.session.add(yahoo_finance)
#     db.session.commit()
#
#     # 创建股票数据
#     stocks = [
#         {
#             'symbol': 'AAPL',
#             'name': 'Apple Inc.',
#             'exchange': 'NASDAQ',
#             'industry': 'Technology',
#             'sector': 'Consumer Electronics'
#         },
#         {
#             'symbol': 'GOOGL',
#             'name': 'Alphabet Inc.',
#             'exchange': 'NASDAQ',
#             'industry': 'Technology',
#             'sector': 'Internet Services'
#         },
#         {
#             'symbol': 'BABA',
#             'name': 'Alibaba Group Holding Ltd',
#             'exchange': 'NYSE',
#             'industry': 'Technology',
#             'sector': 'E-commerce'
#         }
#     ]
#
#     for stock_info in stocks:
#         stock = StockData(
#             symbol=stock_info['symbol'],
#             name=stock_info['name'],
#             exchange=stock_info['exchange'],
#             industry=stock_info['industry'],
#             sector=stock_info['sector'],
#             last_price=100.0,
#             last_update=datetime.utcnow(),
#             source=yahoo_finance
#         )
#         db.session.add(stock)
#
#         # 生成过去30天的每日价格数据
#         base_price = 100.0
#         for i in range(30):
#             date = datetime.utcnow() - timedelta(days=i)
#             price_data = PriceData(
#                 stock=stock,
#                 timestamp=date,
#                 open_price=base_price * (0.99 + 0.02 * i / 30),
#                 high_price=base_price * (1.02 + 0.02 * i / 30),
#                 low_price=base_price * (0.98 + 0.02 * i / 30),
#                 close_price=base_price * (1.00 + 0.02 * i / 30),
#                 volume=1000000,
#                 interval='1d'
#             )
#             db.session.add(price_data)
#
#     db.session.commit()
#
#     # 创建策略模板
#     ma_cross_template = StrategyTemplate(
#         name='移动平均线交叉策略',
#         description='基于短期和长期移动平均线交叉的交易策略',
#         code_template='''
# def generate_signals(data, parameters):
#     short_window = parameters.get('short_window', 10)
#     long_window = parameters.get('long_window', 30)
#
#     data['short_ma'] = data['close'].rolling(window=short_window).mean()
#     data['long_ma'] = data['close'].rolling(window=long_window).mean()
#
#     data['signal'] = 0
#     data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1
#     data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1
#
#     return data
# ''',
#         default_parameters={'short_window': 10, 'long_window': 30},
#         category='趋势跟踪',
#         difficulty='初级'
#     )
#     db.session.add(ma_cross_template)
#     db.session.commit()
#
#     # 创建用户策略
#     user_strategy = Strategy(
#         name='AAPL移动平均线策略',
#         description='苹果股票的移动平均线交叉策略',
#         code=ma_cross_template.code_template,
#         parameters={'short_window': 5, 'long_window': 20},
#         is_active=True,
#         is_public=False,
#         user_id=test_user.id
#     )
#     db.session.add(user_strategy)
#     db.session.commit()
#
#     # 创建回测
#     backtest = Backtest(
#         name='AAPL策略回测',
#         description='苹果股票移动平均线策略的回测',
#         strategy_id=user_strategy.id,
#         user_id=test_user.id,
#         start_date=datetime.utcnow() - timedelta(days=30),
#         end_date=datetime.utcnow(),
#         initial_capital=100000.0,
#         parameters={'short_window': 5, 'long_window': 20},
#         status='completed',
#         results={
#             'final_value': 105000.0,
#             'return': 5.0,
#             'sharpe_ratio': 1.5,
#             'max_drawdown': 2.0,
#             'total_trades': 8,
#             'won_trades': 5,
#             'lost_trades': 3
#         }
#     )
#     db.session.add(backtest)
#     db.session.commit()
#
#     # 创建回测交易记录
#     trades = [
#         {
#             'timestamp': datetime.utcnow() - timedelta(days=25),
#             'side': 'buy',
#             'quantity': 100,
#             'price': 98.5
#         },
#         {
#             'timestamp': datetime.utcnow() - timedelta(days=20),
#             'side': 'sell',
#             'quantity': 100,
#             'price': 102.5
#         }
#     ]
#
#     for trade_info in trades:
#         trade = BacktestTrade(
#             backtest_id=backtest.id,
#             symbol='AAPL',
#             timestamp=trade_info['timestamp'],
#             order_type='market',
#             side=trade_info['side'],
#             quantity=trade_info['quantity'],
#             price=trade_info['price'],
#             commission=0.0
#         )
#         db.session.add(trade)

    # 创建交易账户
    trading_account = TradingAccount(
        name='测试交易账户',
        account_type='stock',
        broker='Interactive Brokers',
        account_number='U123456',
        api_key='demo_api_key',
        api_secret='demo_api_secret',
        initial_balance=100000.0,
        current_balance=105000.0,
        status='active',
        user_id=test_user.id
    )
    db.session.add(trading_account)
    db.session.commit()

    # 创建交易任务
    trading_task = TradingTask(
        name='AAPL自动交易',
        description='苹果股票的自动交易任务',
        strategy_id=user_strategy.id,
        account_id=trading_account.id,
        symbols=['AAPL'],
        parameters={'short_window': 5, 'long_window': 20},
        schedule='0 9 * * 1-5',  # 每个工作日上午9点
        status='active',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(trading_task)
    db.session.commit()

    # 创建交易订单
    order = TradeOrder(
        account_id=trading_account.id,
        task_id=trading_task.id,
        symbol='AAPL',
        order_type='market',
        side='buy',
        quantity=100,
        price=100.5,
        status='filled',
        filled_quantity=100,
        average_fill_price=100.5,
        commission=1.0,
        order_time=datetime.utcnow() - timedelta(hours=1),
        fill_time=datetime.utcnow() - timedelta(minutes=55),
        external_order_id='IB123456'
    )
    db.session.add(order)
    db.session.commit()

    # 创建持仓记录
    position = TradePosition(
        account_id=trading_account.id,
        symbol='AAPL',
        quantity=100,
        average_cost=100.5,
        current_price=102.0,
        market_value=10200.0,
        unrealized_pnl=150.0,
        realized_pnl=0.0
    )
    db.session.add(position)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_test_data()
        print('测试数据初始化完成！')
