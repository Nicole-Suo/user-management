from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import User

bp = Blueprint('auth', __name__)


@bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or request.form or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'missing credentials'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        permissions = []
        for role in user.roles:
            for permission in role.permissions:
                permissions.append(permission.name)
        return jsonify({'message': 'ok', 'username': user.username, 'permissions': sorted(set(permissions))}), 200

    return jsonify({'error': 'invalid credentials'}), 401


@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged out'}), 200


@bp.route('/api/me', methods=['GET'])
@login_required
def me():
    user = current_user
    perms = []
    for role in user.roles:
        for permission in role.permissions:
            perms.append(permission.name)

    return jsonify({
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'permissions': sorted(set(perms)),
    })
