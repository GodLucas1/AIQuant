from datetime import datetime
from app import db

class DataSource(db.Model):
    """数据源模型"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    api_key = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    stock_data = db.relationship('StockData', backref='source', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataSource {self.name}>'

class StockData(db.Model):
    """股票数据模型"""
    __tablename__ = 'stock_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128))
    exchange = db.Column(db.String(32))
    industry = db.Column(db.String(64))
    sector = db.Column(db.String(64))
    last_price = db.Column(db.Float)
    last_update = db.Column(db.DateTime)
    source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    price_data = db.relationship('PriceData', backref='stock', lazy='dynamic')
    
    def __repr__(self):
        return f'<StockData {self.symbol}>'

class PriceData(db.Model):
    """价格数据模型"""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock_data.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    interval = db.Column(db.String(8))  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('stock_id', 'timestamp', 'interval', name='uix_price_data'),)
    
    def __repr__(self):
        return f'<PriceData {self.stock.symbol} {self.timestamp} {self.interval}>'