from functools import wraps

from flask import Blueprint, jsonify, redirect, render_template
from flask import request
from flask_login import current_user, login_required

from app import db
from app.models import Permission, Role, User

bp = Blueprint('routes', __name__)


def requires_permission(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'unauthenticated'}), 401
            if not current_user.has_permission(name):
                return jsonify({'error': 'forbidden'}), 403
            return f(*args, **kwargs)

        return wrapped

    return decorator


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return redirect('/login')


@bp.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return render_template('login.html')


@bp.route('/dashboard')
@login_required
@requires_permission('dashboard.view')
def dashboard_page():
    return render_template('dashboard.html', user=current_user)


@bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=current_user)


@bp.route('/users')
@login_required
@requires_permission('user.read')
def users_page():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('users.html', users=users, user=current_user)


@bp.route('/roles')
@login_required
@requires_permission('role.read')
def roles_page():
    roles = Role.query.order_by(Role.id.asc()).all()
    return render_template('roles.html', roles=roles, user=current_user)


@bp.route('/api/users', methods=['GET'])
@login_required
@requires_permission('user.read')
def list_users():
    users = User.query.all()
    data = [{'id': u.id, 'username': u.username, 'email': u.email, 'full_name': u.full_name} for u in users]
    return jsonify(data)


@bp.route('/api/roles', methods=['GET'])
@login_required
@requires_permission('role.read')
def list_roles():
    roles = Role.query.all()
    result = []
    for role in roles:
        result.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': [permission.name for permission in role.permissions],
        })
    return jsonify(result)


@bp.route('/api/debug/cookies', methods=['GET', 'POST', 'OPTIONS'])
def debug_cookies():
    # Return the cookies and select headers so the browser can show whether
    # the session cookie is being sent on requests.
    data = {
        'cookies': request.cookies,
        'headers': {k: v for k, v in request.headers.items() if k.lower().startswith('cookie') or k.lower().startswith('origin') or k.lower().startswith('host')}
    }
    return jsonify(data)


# --- Users / Roles CRUD APIs ---


def user_to_dict(u):
    return {
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'full_name': u.full_name,
        'roles': [{'id': r.id, 'name': r.name} for r in u.roles],
        'created_at': u.created_at.isoformat() if getattr(u, 'created_at', None) else None,
    }


def role_to_dict(r):
    return {
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'permissions': [p.name for p in r.permissions],
        'created_at': r.created_at.isoformat() if getattr(r, 'created_at', None) else None,
    }


@bp.route('/api/users', methods=['POST'])
@login_required
@requires_permission('user.create')
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    role_ids = data.get('role_ids') or []

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'user exists'}), 409

    user = User(username=username, email=email, full_name=full_name)
    user.set_password(password)
    if role_ids:
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        for r in roles:
            user.roles.append(r)

    db.session.add(user)
    db.session.commit()
    return jsonify(user_to_dict(user)), 201


@bp.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@requires_permission('user.read')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_to_dict(user))


@bp.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
@login_required
@requires_permission('user.update')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    if 'username' in data:
        user.username = data.get('username')
    if 'email' in data:
        user.email = data.get('email')
    if 'full_name' in data:
        user.full_name = data.get('full_name')
    if 'password' in data and data.get('password'):
        user.set_password(data.get('password'))
    if 'role_ids' in data:
        role_ids = data.get('role_ids') or []
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        user.roles = roles

    db.session.commit()
    return jsonify(user_to_dict(user))


@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@requires_permission('user.delete')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


@bp.route('/api/roles', methods=['POST'])
@login_required
@requires_permission('role.create')
def create_role():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    permissions = data.get('permissions') or []

    if not name:
        return jsonify({'error': 'name required'}), 400
    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'role exists'}), 409

    role = Role(name=name, description=description)
    if permissions:
        perms = Permission.query.filter(Permission.name.in_(permissions)).all()
        role.permissions = perms

    db.session.add(role)
    db.session.commit()
    return jsonify(role_to_dict(role)), 201


@bp.route('/api/roles/<int:role_id>', methods=['GET'])
@login_required
@requires_permission('role.read')
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify(role_to_dict(role))


@bp.route('/api/roles/<int:role_id>', methods=['PUT', 'PATCH'])
@login_required
@requires_permission('role.update')
def update_role(role_id):
    role = Role.query.get_or_404(role_id)
    data = request.get_json() or {}
    if 'name' in data:
        role.name = data.get('name')
    if 'description' in data:
        role.description = data.get('description')
    if 'permissions' in data:
        permissions = data.get('permissions') or []
        perms = Permission.query.filter(Permission.name.in_(permissions)).all()
        role.permissions = perms

    db.session.commit()
    return jsonify(role_to_dict(role))


@bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@login_required
@requires_permission('role.delete')
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    return '', 204

