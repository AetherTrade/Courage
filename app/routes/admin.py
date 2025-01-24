from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User
from app.models.bot import Bot
from app import db
from app.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_view

@bp.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    pending_users = User.query.filter_by(is_approved=False).count()
    approved_users = User.query.filter_by(is_approved=True).count()
    
    return render_template('admin/index.html', 
                         total_users=total_users,
                         pending_users=pending_users,
                         approved_users=approved_users)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin/users.html', users=users)

@bp.route('/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.email} has been approved.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/disapprove/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def disapprove_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = False
    db.session.commit()
    flash(f'User {user.email} has been disapproved.', 'warning')
    return redirect(url_for('admin.users'))

@bp.route('/settings')
@login_required
@admin_required
def admin_settings():
    settings = {
        'general_settings': {
            'site_name': 'CourageFX Trading Bot',
            'maintenance_mode': False,
            'user_registration': True,
            'default_theme': 'light'
        },
        'api_settings': {
            'endpoint': 'https://api.couragefx.com/v1',
            'key': '********',
            'secret': '********',
            'timeout': 30
        },
        'trading_settings': {
            'max_bots_per_user': 5,
            'min_deposit': 100,
            'max_leverage': 100,
            'default_stop_loss': 50
        },
        'notification_settings': {
            'email_notifications': True,
            'telegram_notifications': False,
            'telegram_bot_token': '',
            'telegram_chat_id': ''
        }
    }
    return render_template('admin/settings.html', settings=settings)

@bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    data = request.form
    # Here you would typically save the settings to your database
    # For now, we'll just return success
    return jsonify({'success': True, 'message': 'Settings updated successfully'})

@bp.route('/api/user/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    })

@bp.route('/api/user/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'User updated successfully'})

@bp.route('/api/user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'error': 'Cannot delete admin user'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@bp.route('/user/remove/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'User {email} has been deleted.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/toggle-bot/<int:user_id>/<string:bot_type>', methods=['POST'])
@login_required
@admin_required
def toggle_bot_approval(user_id, bot_type):
    user = User.query.get_or_404(user_id)
    
    approval_map = {
        'precision_master': 'precision_master_approved',
        'trend_warrior': 'trend_warrior_approved',
        'pattern_hunter': 'pattern_hunter_approved'
    }
    
    if bot_type not in approval_map:
        flash('Invalid bot type specified.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Toggle the approval status
    setattr(user, approval_map[bot_type], not getattr(user, approval_map[bot_type]))
    db.session.commit()
    
    status = 'approved for' if getattr(user, approval_map[bot_type]) else 'disapproved from'
    flash(f'User {user.email} has been {status} {bot_type.replace("_", " ").title()}.', 'success')
    return redirect(url_for('admin.users'))
