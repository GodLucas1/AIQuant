# 初始化模型包
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()

# 导入所有模型
from app.models.user import User
from app.models.strategy import Strategy
from app.models.backtest import Backtest, BacktestTrade
from app.models.market_data import DataSource, StockData, PriceData

# 导入交易相关模型
from app.models.trading import TradingAccount, TradingTask, TradeOrder, TradePosition