from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def approved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_approved:
            flash('Your account is pending approval. Please contact support.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def bot_access_required(bot_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            approval_map = {
                'precision_master': 'precision_master_approved',
                'trend_warrior': 'trend_warrior_approved',
                'pattern_hunter': 'pattern_hunter_approved'
            }
            
            if not getattr(current_user, approval_map[bot_type], False):
                flash(f'You need approval to access the {bot_type.replace("_", " ").title()} bot.', 'warning')
                return redirect(url_for('user.bots'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator 