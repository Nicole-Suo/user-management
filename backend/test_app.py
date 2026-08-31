import unittest

from app import create_app, db
from app.models import Permission, Role, User


class UserManagementAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            WTF_CSRF_ENABLED=False,
            SERVER_NAME='localhost'
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            dashboard = Permission(name='dashboard.view', description='Dashboard access')
            user_read = Permission(name='user.read', description='Read users')
            role_read = Permission(name='role.read', description='Read roles')
            admin_role = Role(name='admin', description='System administrator')
            admin_role.permissions.extend([dashboard, user_read, role_read])

            admin_user = User(username='admin', email='admin@example.com', full_name='Admin User')
            admin_user.set_password('admin123')
            admin_user.roles.append(admin_role)

            db.session.add_all([dashboard, user_read, role_read, admin_role, admin_user])
            db.session.commit()

        self.client = self.app.test_client()

    def test_login_and_dashboard_access(self):
        login_response = self.client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'admin123'}
        )
        self.assertEqual(login_response.status_code, 200)

        dashboard_response = self.client.get('/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn('Dashboard', dashboard_response.get_data(as_text=True))

    def test_me_contains_permissions(self):
        self.client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        me_response = self.client.get('/api/me')
        self.assertEqual(me_response.status_code, 200)
        data = me_response.get_json()
        self.assertIn('permissions', data)
        self.assertIn('user.read', data['permissions'])


if __name__ == '__main__':
    unittest.main()
