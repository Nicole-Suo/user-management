"""Create initial DB and an admin user."""
from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    db.create_all()
    # create permissions
    perms = ['user.create','user.read','user.update','user.delete',
             'role.create','role.read','role.update','role.delete']
    for p in perms:
        if not Permission.query.filter_by(name=p).first():
            db.session.add(Permission(name=p, description=p))
    db.session.commit()

    # create admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
        db.session.commit()
    # assign all permissions to admin
    admin_role.permissions = Permission.query.all()
    db.session.commit()

    # create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin')
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
    print('Seed complete. admin/admin created')
