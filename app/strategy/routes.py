from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.strategy import strategy_bp
from app.models.strategy import Strategy, StrategyTemplate
from app import db
import json

@strategy_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_strategy_templates():
    """获取策略模板列表"""
    templates = StrategyTemplate.query.all()
    return jsonify({
        'templates': [{
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'difficulty': template.difficulty
        } for template in templates]
    })

@strategy_bp.route('/templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_strategy_template(template_id):
    """获取单个策略模板详情"""
    template = StrategyTemplate.query.get_or_404(template_id)
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'code_template': template.code_template,
        'default_parameters': template.default_parameters,
        'category': template.category,
        'difficulty': template.difficulty
    })

@strategy_bp.route('/strategies', methods=['GET'])
@jwt_required()
def get_user_strategies():
    """获取用户的策略列表"""
    current_user_id = get_jwt_identity()
    strategies = Strategy.query.filter_by(user_id=current_user_id).all()
    return jsonify({
        'strategies': [{
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'is_active': strategy.is_active,
            'is_public': strategy.is_public,
            'created_at': strategy.created_at.isoformat()
        } for strategy in strategies]
    })

@strategy_bp.route('/strategies', methods=['POST'])
@jwt_required()
def create_strategy():
    """创建新策略"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['name', 'code']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 创建新策略
    strategy = Strategy(
        name=data['name'],
        description=data.get('description', ''),
        code=data['code'],
        parameters=data.get('parameters', {}),
        is_public=data.get('is_public', False),
        user_id=current_user_id
    )
    
    db.session.add(strategy)
    db.session.commit()
    
    return jsonify({
        'id': strategy.id,
        'name': strategy.name,
        'message': '策略创建成功'
    }), 201

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
@jwt_required()
def get_strategy(strategy_id):
    """获取单个策略详情"""
    current_user_id = get_jwt_identity()
    strategy = Strategy.query.get_or_404(strategy_id)
    
    # 检查权限
    if strategy.user_id != current_user_id and not strategy.is_public:
        return jsonify({'error': '没有权限访问此策略'}), 403
    
    return jsonify({
        'id': strategy.id,
        'name': strategy.name,
        'description': strategy.description,
        'code': strategy.code,
        'parameters': strategy.parameters,
        'is_active': strategy.is_active,
        'is_public': strategy.is_public,
        'created_at': strategy.created_at.isoformat(),
        'updated_at': strategy.updated_at.isoformat()
    })

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['PUT'])
@jwt_required()
def update_strategy(strategy_id):
    """更新策略"""
    current_user_id = get_jwt_identity()
    strategy = Strategy.query.get_or_404(strategy_id)
    
    # 检查权限
    if strategy.user_id != current_user_id:
        return jsonify({'error': '没有权限修改此策略'}), 403
    
    data = request.get_json()
    
    # 更新策略信息
    if 'name' in data:
        strategy.name = data['name']
    if 'description' in data:
        strategy.description = data['description']
    if 'code' in data:
        strategy.code = data['code']
    if 'parameters' in data:
        strategy.parameters = data['parameters']
    if 'is_active' in data:
        strategy.is_active = data['is_active']
    if 'is_public' in data:
        strategy.is_public = data['is_public']
    
    db.session.commit()
    return jsonify({'message': '策略更新成功'})

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['DELETE'])
@jwt_required()
def delete_strategy(strategy_id):
    """删除策略"""
    current_user_id = get_jwt_identity()
    strategy = Strategy.query.get_or_404(strategy_id)
    
    # 检查权限
    if strategy.user_id != current_user_id:
        return jsonify({'error': '没有权限删除此策略'}), 403
    
    db.session.delete(strategy)
    db.session.commit()
    return jsonify({'message': '策略删除成功'})

@strategy_bp.route('/public-strategies', methods=['GET'])
@jwt_required()
def get_public_strategies():
    """获取公开策略列表"""
    strategies = Strategy.query.filter_by(is_public=True).all()
    return jsonify({
        'strategies': [{
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'author': strategy.author.username,
            'created_at': strategy.created_at.isoformat()
        } for strategy in strategies]
    })

@strategy_bp.route('/strategies/<int:strategy_id>/clone', methods=['POST'])
@jwt_required()
def clone_strategy(strategy_id):
    """克隆公开策略"""
    current_user_id = get_jwt_identity()
    source_strategy = Strategy.query.get_or_404(strategy_id)
    
    # 检查权限
    if not source_strategy.is_public and source_strategy.user_id != current_user_id:
        return jsonify({'error': '没有权限克隆此策略'}), 403
    
    # 创建新策略
    new_strategy = Strategy(
        name=f"{source_strategy.name} (克隆)",
        description=source_strategy.description,
        code=source_strategy.code,
        parameters=source_strategy.parameters,
        is_public=False,
        user_id=current_user_id
    )
    
    db.session.add(new_strategy)
    db.session.commit()
    
    return jsonify({
        'id': new_strategy.id,
        'name': new_strategy.name,
        'message': '策略克隆成功'
    }), 201