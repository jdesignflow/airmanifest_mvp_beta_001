from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g, session
)
from app.auth import login_required
from app.db import get_db
from app.patterns.factory import ProviderFactory

bp = Blueprint('traveler', __name__, url_prefix='/traveler')

@bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get recent notifications
    cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (g.user['id'],))
    notifications = cursor.fetchall()
    
    # Get active watches count
    cursor.execute("SELECT COUNT(*) as count FROM watches WHERE user_id = %s AND is_active = TRUE", (g.user['id'],))
    watch_count = cursor.fetchone()['count']
    
    return render_template('traveler/dashboard.html', notifications=notifications, watch_count=watch_count)

@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    results = []
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        date = request.form['date']
        
        provider = ProviderFactory.get_provider()
        results = provider.search_flights(origin, destination, date)
        
        # Pass search params back to template to prepopulate "Watch This Route" modal
        return render_template('traveler/results.html', flights=results, search_params={
            'origin': origin, 'destination': destination, 'date': date
        })
        
    return render_template('traveler/search.html')

@bp.route('/watch', methods=['POST'])
@login_required
def add_watch():
    origin = request.form['origin']
    destination = request.form['destination']
    date = request.form['date']
    threshold = request.form['threshold']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO watches (user_id, origin, destination, depart_date, threshold_price) VALUES (%s, %s, %s, %s, %s)",
        (g.user['id'], origin, destination, date, threshold)
    )
    flash("Route added to Watchlist!")
    return redirect(url_for('traveler.dashboard'))

@bp.route('/watchlist')
@login_required
def watchlist():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM watches WHERE user_id = %s", (g.user['id'],))
    watches = cursor.fetchall()
    return render_template('traveler/watchlist.html', watches=watches)