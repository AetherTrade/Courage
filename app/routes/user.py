from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.bot import Bot
from app.decorators import approved_required, bot_access_required
from app import db

bp = Blueprint('user', __name__)  # Remove url_prefix to allow both /dashboard and /bot routes

@bp.route('/dashboard')
@login_required
def dashboard():
    user_bots = Bot.query.filter_by(user_id=current_user.id).all()
    stats = {
        'active_bots': len([bot for bot in user_bots if bot.is_active]),
        'total_profit': sum([bot.profit for bot in user_bots]),
        'win_rate': calculate_win_rate(user_bots),
        'total_trades': sum([bot.total_trades for bot in user_bots])
    }
    return render_template('user/dashboard.html', user=current_user, stats=stats, bots=user_bots)

@bp.route('/bot/precision-master')
@login_required
@bot_access_required('precision_master')
def precision_master():
    return render_template('user/bots/precision_master.html')

@bp.route('/bot/trend-warrior')
@login_required
@bot_access_required('trend_warrior')
def trend_warrior():
    return render_template('user/bots/trend_warrior.html')

@bp.route('/bot/pattern-hunter')
@login_required
@bot_access_required('pattern_hunter')
def pattern_hunter():
    return render_template('user/bots/pattern_hunter.html')

@bp.route('/bots')
@login_required
@approved_required
def bots():
    user_bots = Bot.query.filter_by(user_id=current_user.id).all()
    return render_template('user/bots.html', bots=user_bots)

@bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@bp.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.form
    current_user.first_name = data.get('first_name', current_user.first_name)
    current_user.last_name = data.get('last_name', current_user.last_name)
    current_user.phone = data.get('phone', current_user.phone)
    
    # Only update email if it's changed and not already taken
    new_email = data.get('email')
    if new_email and new_email != current_user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'error': 'Email already taken'}), 400
        current_user.email = new_email
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@bp.route('/api/profile/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.form
    if not check_password_hash(current_user.password, data.get('current_password')):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    current_user.password = generate_password_hash(data.get('new_password'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@bp.route('/api/trading/history')
@login_required
def trading_history():
    history = get_trading_history(current_user.id)
    return jsonify(history)

@bp.route('/api/bots/create', methods=['POST'])
@login_required
def create_bot():
    data = request.form
    new_bot = Bot(
        name=data.get('bot_name'),
        strategy=data.get('strategy'),
        initial_investment=float(data.get('investment')),
        user_id=current_user.id
    )
    db.session.add(new_bot)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bot created successfully'})

@bp.route('/api/bots/<int:bot_id>/stop', methods=['POST'])
@login_required
def stop_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    if bot.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bot.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bot stopped successfully'})

def calculate_win_rate(bots):
    total_wins = sum([bot.winning_trades for bot in bots])
    total_trades = sum([bot.total_trades for bot in bots])
    return round((total_wins / total_trades * 100) if total_trades > 0 else 0, 2)

def get_trading_history(user_id):
    return {
        'dates': [],
        'values': [],
        'statistics': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'profit_factor': 0
        }
    }
