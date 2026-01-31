from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g
)
from app.auth import login_required
from app.db import get_db
from app.patterns.observer import PriceSubject, NotificationObserver
from app.patterns.factory import ProviderFactory

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
def admin_only():
    # Strict Role Check
    if g.user['role'] != 'admin':
        flash("Access Denied: Administrator privileges required.")
        return redirect(url_for('traveler.dashboard'))

@bp.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Live Metrics
    cursor.execute("SELECT COUNT(*) as u FROM users")
    metrics = {'users': cursor.fetchone()['u']}
    
    cursor.execute("SELECT COUNT(*) as w FROM watches WHERE is_active = TRUE")
    metrics['watches'] = cursor.fetchone()['w']
    
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'provider_mode'")
    mode = cursor.fetchone()['setting_value']
    
    # Mock API Usage (Randomized for Demo)
    import random
    metrics['api_calls'] = random.randint(120, 450) 
    
    return render_template('admin/dashboard.html', metrics=metrics, mode=mode)

@bp.route('/users')
def users():
    """User Management Page"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, first_name, last_name, email, role, is_banned, created_at FROM users ORDER BY created_at DESC")
    all_users = cursor.fetchall()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_banned = NOT is_banned WHERE id = %s", (user_id,))
    flash(f"User status updated.")
    return redirect(url_for('admin.users'))

@bp.route('/cms', methods=('GET', 'POST'))
def cms():
    """Content Management System for Destinations"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Add new destination
        city = request.form['city']
        country = request.form['country']
        price = request.form['price']
        image = request.form['image']
        
        cursor.execute("INSERT INTO destinations (city, country, price_estimate, image_url) VALUES (%s, %s, %s, %s)",
                       (city, country, price, image))
        flash("Destination added successfully!")
        return redirect(url_for('admin.cms'))
        
    cursor.execute("SELECT * FROM destinations ORDER BY id DESC")
    destinations = cursor.fetchall()
    return render_template('admin/cms.html', destinations=destinations)

@bp.route('/cms/delete/<int:dest_id>', methods=['POST'])
def delete_dest(dest_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM destinations WHERE id = %s", (dest_id,))
    flash("Destination removed.")
    return redirect(url_for('admin.cms'))

@bp.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    new_mode = request.form['mode']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("REPLACE INTO settings (setting_key, setting_value) VALUES ('provider_mode', %s)", (new_mode,))
    flash(f"System switched to {new_mode.upper()} mode.")
    return redirect(url_for('admin.dashboard'))

@bp.route('/refresh_all', methods=['POST'])
def refresh_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM watches WHERE is_active = TRUE")
    watches = cursor.fetchall()
    
    provider = ProviderFactory.get_provider()
    observer = NotificationObserver()
    
    count = 0
    for watch in watches:
        flights = provider.search_flights(watch['origin'], watch['destination'], watch['depart_date'])
        if flights:
            lowest = min(flights, key=lambda x: x['price'])
            subject = PriceSubject(watch['id'], watch['user_id'], watch['threshold_price'], watch['origin'], watch['destination'])
            subject.attach(observer)
            subject.notify(lowest['price'], lowest['provider'])
            count += 1
            
    flash(f"Refreshed {count} routes. Notifications sent.")
    return redirect(url_for('admin.dashboard'))