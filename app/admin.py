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
    if g.user['role'] != 'admin':
        flash("Access Denied.")
        return redirect(url_for('traveler.dashboard'))

@bp.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Metrics
    cursor.execute("SELECT COUNT(*) as u FROM users")
    total_users = cursor.fetchone()['u']
    
    cursor.execute("SELECT COUNT(*) as w FROM watches")
    total_watches = cursor.fetchone()['w']
    
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'provider_mode'")
    mode = cursor.fetchone()['setting_value']
    
    return render_template('admin/dashboard.html', metrics={'users': total_users, 'watches': total_watches}, mode=mode)

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
    
    # 1. Get all active watches
    cursor.execute("SELECT * FROM watches WHERE is_active = TRUE")
    watches = cursor.fetchall()
    
    provider = ProviderFactory.get_provider()
    observer = NotificationObserver()
    
    count = 0
    for watch in watches:
        # 2. Fetch new price for each watch
        # (For demo simplicity, we search just the route logic here)
        flights = provider.search_flights(watch['origin'], watch['destination'], watch['depart_date'])
        
        if flights:
            lowest_flight = min(flights, key=lambda x: x['price'])
            
            # 3. Create Subject and Notify
            subject = PriceSubject(watch['id'], watch['user_id'], watch['threshold_price'], watch['origin'], watch['destination'])
            subject.attach(observer)
            subject.notify(lowest_flight['price'], lowest_flight['provider'])
            count += 1
            
    flash(f"Refreshed {count} routes. Notifications sent where applicable.")
    return redirect(url_for('admin.dashboard'))