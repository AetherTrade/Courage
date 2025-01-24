from datetime import datetime
from app import db

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    initial_investment = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float)
    profit = db.Column(db.Float, default=0.0)
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_trade_at = db.Column(db.DateTime)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    @property
    def win_rate(self):
        if self.total_trades == 0:
            return 0
        return round((self.winning_trades / self.total_trades) * 100, 2)
    
    @property
    def profit_percentage(self):
        if self.initial_investment == 0:
            return 0
        return round((self.profit / self.initial_investment) * 100, 2)
    
    def update_stats(self, trade_result, profit_amount):
        self.total_trades += 1
        if trade_result == 'win':
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.profit += profit_amount
        self.current_balance = self.initial_investment + self.profit
        self.last_trade_at = datetime.utcnow() 