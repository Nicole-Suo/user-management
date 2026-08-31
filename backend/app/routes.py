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

