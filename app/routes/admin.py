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

@bp.route('/admin')
@login_required
def index():  # This is the main admin index route
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('user.dashboard'))
    return render_template('admin/index.html')

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('user.dashboard'))
    return render_template('admin/dashboard.html')

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

@bp.route('/update_bot_access', methods=['POST'])
@login_required
def update_bot_access():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})

    data = request.get_json()
    user_id = data.get('user_id')
    bot_type = data.get('bot_type')
    approved = data.get('approved')

    print(f"Received request - User ID: {user_id}, Bot: {bot_type}, Approved: {approved}")

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})

    try:
        if bot_type == 'courage_flux':
            user.courage_flux_approved = bool(approved)
            db.session.commit()
            db.session.refresh(user)
            return jsonify({
                'success': True, 
                'message': 'Access updated successfully',
                'new_value': user.courage_flux_approved
            })
        else:
            bot_attributes = {
                'precision_master': 'precision_master_approved',
                'trend_warrior': 'trend_warrior_approved',
                'pattern_hunter': 'pattern_hunter_approved'
            }
            if bot_type in bot_attributes:
                setattr(user, bot_attributes[bot_type], approved)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Access updated successfully'})
            
            return jsonify({'success': False, 'message': 'Invalid bot type'})
            
    except Exception as e:
        db.session.rollback()
        print(f"Error updating bot access: {str(e)}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
