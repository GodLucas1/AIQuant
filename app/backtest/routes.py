from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.backtest import backtest_bp
from app.models.backtest import Backtest, BacktestTrade
from app.models.strategy import Strategy
from app import db
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import pytz
import backtrader as bt
import io
import os
import tempfile

@backtest_bp.route('/list', methods=['GET'])
@jwt_required()
def get_backtests():
    """获取用户的回测列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 分页查询
    pagination = Backtest.query.filter_by(user_id=user_id).order_by(
        Backtest.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    backtests = pagination.items
    
    return jsonify({
        'backtests': [{
            'id': backtest.id,
            'name': backtest.name,
            'description': backtest.description,
            'strategy_id': backtest.strategy_id,
            'strategy_name': backtest.strategy.name,
            'start_date': backtest.start_date.isoformat(),
            'end_date': backtest.end_date.isoformat(),
            'initial_capital': backtest.initial_capital,
            'status': backtest.status,
            'created_at': backtest.created_at.isoformat()
        } for backtest in backtests],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@backtest_bp.route('/<int:backtest_id>', methods=['GET'])
@jwt_required()
def get_backtest(backtest_id):
    """获取回测详情"""
    user_id = get_jwt_identity()
    
    backtest = Backtest.query.filter_by(id=backtest_id, user_id=user_id).first()
    if not backtest:
        return jsonify({'error': '回测不存在或无权访问'}), 404
    
    # 获取交易记录
    trades = BacktestTrade.query.filter_by(backtest_id=backtest_id).all()
    
    return jsonify({
        'backtest': {
            'id': backtest.id,
            'name': backtest.name,
            'description': backtest.description,
            'strategy_id': backtest.strategy_id,
            'strategy_name': backtest.strategy.name,
            'start_date': backtest.start_date.isoformat(),
            'end_date': backtest.end_date.isoformat(),
            'initial_capital': backtest.initial_capital,
            'parameters': backtest.parameters,
            'results': backtest.results,
            'status': backtest.status,
            'created_at': backtest.created_at.isoformat(),
            'updated_at': backtest.updated_at.isoformat()
        },
        'trades': [{
            'id': trade.id,
            'symbol': trade.symbol,
            'timestamp': trade.timestamp.isoformat(),
            'order_type': trade.order_type,
            'side': trade.side,
            'quantity': trade.quantity,
            'price': trade.price,
            'commission': trade.commission
        } for trade in trades]
    })

@backtest_bp.route('/create', methods=['POST'])
@jwt_required()
def create_backtest():
    """创建新的回测"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['name', 'strategy_id', 'start_date', 'end_date', 'initial_capital']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400
    
    # 验证策略是否存在且属于当前用户
    strategy = Strategy.query.filter_by(id=data['strategy_id']).first()
    if not strategy or strategy.user_id != user_id:
        return jsonify({'error': '策略不存在或无权访问'}), 404
    
    # 解析日期
    try:
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
    except ValueError:
        return jsonify({'error': '日期格式无效'}), 400
    
    # 创建回测记录
    backtest = Backtest(
        name=data['name'],
        description=data.get('description', ''),
        strategy_id=data['strategy_id'],
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        initial_capital=data['initial_capital'],
        parameters=data.get('parameters', {}),
        status='pending'
    )
    
    db.session.add(backtest)
    db.session.commit()
    
    return jsonify({
        'message': '回测创建成功',
        'backtest_id': backtest.id
    }), 201

@backtest_bp.route('/<int:backtest_id>/run', methods=['POST'])
@jwt_required()
def run_backtest(backtest_id):
    """运行回测"""
    user_id = get_jwt_identity()
    
    # 验证回测是否存在且属于当前用户
    backtest = Backtest.query.filter_by(id=backtest_id, user_id=user_id).first()
    if not backtest:
        return jsonify({'error': '回测不存在或无权访问'}), 404
    
    # 检查回测状态
    if backtest.status == 'running':
        return jsonify({'error': '回测已在运行中'}), 400
    
    # 更新回测状态
    backtest.status = 'running'
    db.session.commit()
    
    try:
        # 获取策略代码
        strategy = Strategy.query.get(backtest.strategy_id)
        if not strategy:
            raise ValueError('策略不存在')
        
        # 这里应该异步执行回测，但为了简化，我们同步执行
        # 在实际应用中，应该使用Celery等任务队列
        results = execute_backtest(backtest, strategy)
        
        # 更新回测结果
        backtest.results = results
        backtest.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'message': '回测执行成功',
            'results': results
        })
    except Exception as e:
        # 回测失败，更新状态
        backtest.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'回测执行失败: {str(e)}'}), 500

@backtest_bp.route('/<int:backtest_id>', methods=['DELETE'])
@jwt_required()
def delete_backtest(backtest_id):
    """删除回测"""
    user_id = get_jwt_identity()
    
    backtest = Backtest.query.filter_by(id=backtest_id, user_id=user_id).first()
    if not backtest:
        return jsonify({'error': '回测不存在或无权访问'}), 404
    
    # 删除相关的交易记录
    BacktestTrade.query.filter_by(backtest_id=backtest_id).delete()
    
    # 删除回测
    db.session.delete(backtest)
    db.session.commit()
    
    return jsonify({'message': '回测删除成功'})

# 辅助函数：执行回测
def execute_backtest(backtest, strategy):
    """执行回测的核心逻辑"""
    # 创建backtrader引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    cerebro.broker.setcash(backtest.initial_capital)
    
    # 设置佣金
    cerebro.broker.setcommission(commission=0.001)  # 0.1%
    
    # 添加数据
    # 这里应该从数据库或外部API获取数据
    # 为了简化，我们使用Yahoo Finance的数据
    import yfinance as yf
    
    # 假设策略参数中包含了交易的股票代码
    symbols = backtest.parameters.get('symbols', ['AAPL'])
    
    for symbol in symbols:
        data = yf.download(symbol, 
                          start=backtest.start_date, 
                          end=backtest.end_date)
        if len(data) > 0:
            # 转换为backtrader可用的数据格式
            datafeed = bt.feeds.PandasData(
                dataname=data,
                name=symbol,
                fromdate=backtest.start_date,
                todate=backtest.end_date
            )
            cerebro.adddata(datafeed)
    
    # 动态创建策略类
    strategy_code = strategy.code
    strategy_params = backtest.parameters
    
    # 这里需要安全地执行用户代码，实际应用中应该有更多的安全措施
    # 为了简化，我们直接执行代码
    try:
        # 创建临时文件来存储策略代码
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(strategy_code)
            strategy_file = f.name
        
        # 导入策略模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("user_strategy", strategy_file)
        user_strategy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_strategy)
        
        # 添加策略
        cerebro.addstrategy(user_strategy.Strategy, **strategy_params)
        
        # 删除临时文件
        os.unlink(strategy_file)
    except Exception as e:
        raise ValueError(f'策略代码执行失败: {str(e)}')
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    results = cerebro.run()
    strat = results[0]
    
    # 收集回测结果
    portfolio_value = cerebro.broker.getvalue()
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    # 记录交易
    for i, trade in enumerate(strat.trades):
        db_trade = BacktestTrade(
            backtest_id=backtest.id,
            symbol=trade.data._name,
            timestamp=backtest.start_date + timedelta(days=i),  # 简化处理
            order_type='market',
            side='buy' if trade.size > 0 else 'sell',
            quantity=abs(trade.size),
            price=trade.price,
            commission=trade.commission
        )
        db.session.add(db_trade)
    
    # 返回结果
    return {
        'final_value': portfolio_value,
        'return': (portfolio_value / backtest.initial_capital - 1) * 100,  # 百分比
        'sharpe_ratio': sharpe.get('sharperatio', 0),
        'max_drawdown': drawdown.get('max', {}).get('drawdown', 0) * 100,  # 百分比
        'total_trades': trades.get('total', {}).get('total', 0),
        'won_trades': trades.get('won', {}).get('total', 0),
        'lost_trades': trades.get('lost', {}).get('total', 0),
        'win_rate': trades.get('won', {}).get('total', 0) / trades.get('total', {}).get('total', 1) * 100 if trades.get('total', {}).get('total', 0) > 0 else 0,
        'equity_curve': [cerebro.broker.get_value() for _ in range(10)]  # 简化的权益曲线
    }