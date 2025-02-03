from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    avatar_url = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    
    # Bot-specific approval flags
    precision_master_approved = db.Column(db.Boolean, default=False)
    trend_warrior_approved = db.Column(db.Boolean, default=False)
    pattern_hunter_approved = db.Column(db.Boolean, default=False)
    courage_flux_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    bots = db.relationship('Bot', backref='user', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_bot_stats(self):
        total_profit = sum(bot.profit for bot in self.bots)
        active_bots = sum(1 for bot in self.bots if bot.is_active)
        total_trades = sum(bot.total_trades for bot in self.bots)
        return {
            'total_profit': total_profit,
            'active_bots': active_bots,
            'total_trades': total_trades
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
