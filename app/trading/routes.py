from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.trading import trading_bp
from app.models.strategy import Strategy
from app.models.trading import TradingTask, TradingAccount, TradeOrder, TradePosition
from app import db
from datetime import datetime
import pytz

@trading_bp.route('/accounts', methods=['GET'])
@jwt_required()
def get_trading_accounts():
    """获取用户的交易账户列表"""
    user_id = get_jwt_identity()
    accounts = TradingAccount.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'accounts': [{
            'id': account.id,
            'name': account.name,
            'broker': account.broker,
            'account_type': account.account_type,
            'balance': account.balance,
            'status': account.status,
            'created_at': account.created_at.isoformat()
        } for account in accounts]
    })

@trading_bp.route('/accounts', methods=['POST'])
@jwt_required()
def create_trading_account():
    """创建新的交易账户"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['name', 'broker', 'account_type', 'api_key', 'api_secret']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400
    
    # 创建账户
    account = TradingAccount(
        user_id=user_id,
        name=data['name'],
        broker=data['broker'],
        account_type=data['account_type'],
        api_key=data['api_key'],
        api_secret=data['api_secret'],
        status='active'
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': '交易账户创建成功',
        'account_id': account.id
    }), 201

@trading_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_trading_tasks():
    """获取用户的交易任务列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 分页查询
    pagination = TradingTask.query.filter_by(user_id=user_id).order_by(
        TradingTask.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    tasks = pagination.items
    
    return jsonify({
        'tasks': [{
            'id': task.id,
            'name': task.name,
            'strategy_id': task.strategy_id,
            'account_id': task.account_id,
            'status': task.status,
            'created_at': task.created_at.isoformat()
        } for task in tasks],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@trading_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_trading_task():
    """创建新的交易任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['name', 'strategy_id', 'account_id', 'parameters']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400
    
    # 验证策略是否存在且属于当前用户
    strategy = Strategy.query.filter_by(id=data['strategy_id'], user_id=user_id).first()
    if not strategy:
        return jsonify({'error': '策略不存在或无权访问'}), 404
    
    # 验证交易账户是否存在且属于当前用户
    account = TradingAccount.query.filter_by(id=data['account_id'], user_id=user_id).first()
    if not account:
        return jsonify({'error': '交易账户不存在或无权访问'}), 404
    
    # 创建交易任务
    task = TradingTask(
        name=data['name'],
        strategy_id=data['strategy_id'],
        account_id=data['account_id'],
        user_id=user_id,
        parameters=data['parameters'],
        status='pending'
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': '交易任务创建成功',
        'task_id': task.id
    }), 201

@trading_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_trading_task(task_id):
    """获取交易任务详情"""
    user_id = get_jwt_identity()
    
    task = TradingTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': '交易任务不存在或无权访问'}), 404
    
    # 获取最近的交易订单记录
    orders = TradeOrder.query.filter_by(task_id=task_id).order_by(
        TradeOrder.created_at.desc()
    ).limit(20).all()
    
    return jsonify({
        'task': {
            'id': task.id,
            'name': task.name,
            'strategy_id': task.strategy_id,
            'account_id': task.account_id,
            'parameters': task.parameters,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        },
        'orders': [{
            'id': order.id,
            'symbol': order.symbol,
            'order_type': order.order_type,
            'side': order.side,
            'quantity': order.quantity,
            'price': order.price,
            'status': order.status,
            'filled_quantity': order.filled_quantity,
            'average_fill_price': order.average_fill_price,
            'commission': order.commission,
            'created_at': order.created_at.isoformat()
        } for order in orders]
    })

@trading_bp.route('/tasks/<int:task_id>/start', methods=['POST'])
@jwt_required()
def start_trading_task(task_id):
    """启动交易任务"""
    user_id = get_jwt_identity()
    
    task = TradingTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': '交易任务不存在或无权访问'}), 404
    
    if task.status == 'running':
        return jsonify({'error': '交易任务已在运行中'}), 400
    
    # 更新任务状态
    task.status = 'running'
    task.updated_at = datetime.now(pytz.timezone('UTC'))
    db.session.commit()
    
    # 这里应该异步启动交易任务
    # 在实际应用中，应该使用Celery等任务队列
    
    return jsonify({'message': '交易任务已启动'})

@trading_bp.route('/tasks/<int:task_id>/stop', methods=['POST'])
@jwt_required()
def stop_trading_task(task_id):
    """停止交易任务"""
    user_id = get_jwt_identity()
    
    task = TradingTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': '交易任务不存在或无权访问'}), 404
    
    if task.status != 'running':
        return jsonify({'error': '交易任务未在运行中'}), 400
    
    # 更新任务状态
    task.status = 'stopped'
    task.updated_at = datetime.now(pytz.timezone('UTC'))
    db.session.commit()
    
    # 这里应该异步停止交易任务
    # 在实际应用中，应该使用Celery等任务队列
    
    return jsonify({'message': '交易任务已停止'})

@trading_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_trading_task(task_id):
    """删除交易任务"""
    user_id = get_jwt_identity()
    
    task = TradingTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': '交易任务不存在或无权访问'}), 404
    
    if task.status == 'running':
        return jsonify({'error': '无法删除运行中的交易任务'}), 400
    
    # 删除相关的交易订单记录
    TradeOrder.query.filter_by(task_id=task_id).delete()
    
    # 删除任务
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': '交易任务删除成功'})

@trading_bp.route('/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """获取用户的所有持仓"""
    user_id = get_jwt_identity()
    
    # 获取用户的所有交易账户
    accounts = TradingAccount.query.filter_by(user_id=user_id).all()
    account_ids = [account.id for account in accounts]
    
    # 获取这些账户的所有持仓
    positions = TradePosition.query.filter(TradePosition.account_id.in_(account_ids)).all()
    
    return jsonify({
        'positions': [{
            'id': position.id,
            'account_id': position.account_id,
            'account_name': position.account.name,
            'symbol': position.symbol,
            'quantity': position.quantity,
            'average_cost': position.average_cost,
            'current_price': position.current_price,
            'market_value': position.market_value,
            'unrealized_pnl': position.unrealized_pnl,
            'realized_pnl': position.realized_pnl,
            'open_date': position.open_date.isoformat() if position.open_date else None,
            'last_update': position.last_update.isoformat() if position.last_update else None
        } for position in positions if position.quantity > 0]
    })

@trading_bp.route('/accounts/<int:account_id>/positions', methods=['GET'])
@jwt_required()
def get_account_positions(account_id):
    """获取特定账户的持仓"""
    user_id = get_jwt_identity()
    
    # 验证账户是否存在且属于当前用户
    account = TradingAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({'error': '交易账户不存在或无权访问'}), 404
    
    # 获取账户的所有持仓
    positions = TradePosition.query.filter_by(account_id=account_id).all()
    
    return jsonify({
        'account': {
            'id': account.id,
            'name': account.name,
            'broker': account.broker,
            'account_type': account.account_type,
            'current_balance': account.current_balance,
            'status': account.status
        },
        'positions': [{
            'id': position.id,
            'symbol': position.symbol,
            'quantity': position.quantity,
            'average_cost': position.average_cost,
            'current_price': position.current_price,
            'market_value': position.market_value,
            'unrealized_pnl': position.unrealized_pnl,
            'realized_pnl': position.realized_pnl,
            'open_date': position.open_date.isoformat() if position.open_date else None,
            'last_update': position.last_update.isoformat() if position.last_update else None
        } for position in positions if position.quantity > 0]
    })