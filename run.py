from flask.cli import FlaskGroup
from app import create_app, db
from app.models.user import User
from app.models.bot import Bot

app = create_app()
cli = FlaskGroup(app)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Bot': Bot
    }

@cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print('Database initialized!')

@cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    with app.app_context():
        admin = User.query.filter_by(email='couragefx@info.co.ke').first()
        if admin:
            print('Admin user already exists!')
            return
        
        from werkzeug.security import generate_password_hash
        admin = User(
            email='couragefx@info.co.ke',
            password=generate_password_hash('70605040@Couragefx', method='pbkdf2:sha256'),
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created!')

def main():
    """Main entry point for direct Python execution"""
    with app.app_context():
        db.create_all()  # Ensure database is created
    app.run(debug=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        cli()  # Use CLI if arguments are provided
    else:
        main()  # Run development server directly if no arguments
