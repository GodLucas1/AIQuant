from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.market_data import market_data_bp
from app.models.market_data import StockData, DataSource
from app import db
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

@market_data_bp.route('/sources', methods=['GET'])
@jwt_required()
def get_data_sources():
    """获取所有数据源"""
    sources = DataSource.query.all()
    return jsonify({
        'sources': [{
            'id': source.id,
            'name': source.name,
            'description': source.description,
            'is_active': source.is_active
        } for source in sources]
    })

@market_data_bp.route('/stocks/search', methods=['GET'])
@jwt_required()
def search_stocks():
    """搜索股票"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': '搜索关键词至少需要2个字符'}), 400
    
    # 这里使用简单的模糊匹配，实际应用中可能需要更复杂的搜索逻辑
    stocks = StockData.query.filter(
        (StockData.symbol.ilike(f'%{query}%')) | 
        (StockData.name.ilike(f'%{query}%'))
    ).limit(20).all()
    
    return jsonify({
        'stocks': [{
            'symbol': stock.symbol,
            'name': stock.name,
            'exchange': stock.exchange,
            'last_price': stock.last_price,
            'last_update': stock.last_update.isoformat() if stock.last_update else None
        } for stock in stocks]
    })

@market_data_bp.route('/stocks/<symbol>/price', methods=['GET'])
@jwt_required()
def get_stock_price(symbol):
    """获取股票价格数据"""
    interval = request.args.get('interval', '1d')  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    period = request.args.get('period', '1mo')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    
    # 使用yfinance获取数据
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        # 格式化数据
        data = []
        for index, row in hist.iterrows():
            data.append({
                'date': index.isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        # 更新数据库中的最新价格
        stock_data = StockData.query.filter_by(symbol=symbol).first()
        if stock_data:
            stock_data.last_price = float(hist['Close'].iloc[-1])
            stock_data.last_update = datetime.now(pytz.timezone('UTC'))
            db.session.commit()
        
        return jsonify({
            'symbol': symbol,
            'interval': interval,
            'period': period,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_data_bp.route('/stocks/sync', methods=['POST'])
@jwt_required()
def sync_stock_data():
    """同步股票数据"""
    data = request.get_json()
    symbols = data.get('symbols', [])
    
    if not symbols:
        return jsonify({'error': '请提供股票代码列表'}), 400
    
    results = []
    for symbol in symbols:
        try:
            # 使用yfinance获取基本信息
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # 检查数据库中是否已存在
            stock_data = StockData.query.filter_by(symbol=symbol).first()
            if not stock_data:
                stock_data = StockData(
                    symbol=symbol,
                    name=info.get('shortName', ''),
                    exchange=info.get('exchange', ''),
                    industry=info.get('industry', ''),
                    sector=info.get('sector', ''),
                    source_id=1  # 假设1是Yahoo Finance的数据源ID
                )
                db.session.add(stock_data)
            
            # 更新最新价格
            hist = stock.history(period='1d')
            if not hist.empty:
                stock_data.last_price = float(hist['Close'].iloc[-1])
                stock_data.last_update = datetime.now(pytz.timezone('UTC'))
            
            results.append({
                'symbol': symbol,
                'status': 'success',
                'message': '数据同步成功'
            })
        except Exception as e:
            results.append({
                'symbol': symbol,
                'status': 'error',
                'message': str(e)
            })
    
    db.session.commit()
    return jsonify({'results': results})

@market_data_bp.route('/indicators', methods=['GET'])
@jwt_required()
def get_technical_indicators():
    """获取技术指标"""
    symbol = request.args.get('symbol')
    indicator = request.args.get('indicator', 'sma')  # sma, ema, rsi, macd, etc.
    period = int(request.args.get('period', 14))
    
    if not symbol:
        return jsonify({'error': '请提供股票代码'}), 400
    
    try:
        # 获取历史数据
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1y')
        
        if hist.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        # 计算指标
        if indicator == 'sma':
            # 简单移动平均线
            hist['indicator'] = hist['Close'].rolling(window=period).mean()
        elif indicator == 'ema':
            # 指数移动平均线
            hist['indicator'] = hist['Close'].ewm(span=period, adjust=False).mean()
        elif indicator == 'rsi':
            # 相对强弱指标
            delta = hist['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            rs = avg_gain / avg_loss
            hist['indicator'] = 100 - (100 / (1 + rs))
        else:
            return jsonify({'error': '不支持的指标类型'}), 400
        
        # 格式化数据
        data = []
        for index, row in hist.iterrows():
            if not pd.isna(row['indicator']):
                data.append({
                    'date': index.isoformat(),
                    'value': float(row['indicator'])
                })
        
        return jsonify({
            'symbol': symbol,
            'indicator': indicator,
            'period': period,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500