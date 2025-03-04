from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.auth import auth_bp
from app.models.user import User
from app import db
from passlib.hash import pbkdf2_sha256

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=pbkdf2_sha256.hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    if not user or not pbkdf2_sha256.verify(data['password'], user.password_hash):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    })

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'email' in data:
        if User.query.filter(User.id != current_user_id, User.email == data['email']).first():
            return jsonify({'error': '邮箱已被使用'}), 400
        user.email = data['email']
    
    if 'password' in data:
        user.password_hash = pbkdf2_sha256.hash(data['password'])
    
    db.session.commit()
    return jsonify({'message': '个人信息更新成功'}), 200