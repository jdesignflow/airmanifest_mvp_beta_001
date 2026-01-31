from flask import Blueprint, render_template
from app.utils import get_destination_image

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Dynamic "Popular Destinations" for the homepage
    destinations = [
        {"city": "Tokyo", "country": "Japan", "price": "1,200"},
        {"city": "Paris", "country": "France", "price": "850"},
        {"city": "New York", "country": "USA", "price": "450"},
        {"city": "Dubai", "country": "UAE", "price": "920"}
    ]
    
    # Fetch images dynamically (In production, you'd cache this to save API calls)
    for dest in destinations:
        dest['image'] = get_destination_image(dest['city'])

    return render_template('main/index.html', destinations=destinations)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/careers')
def careers():
    return render_template('main/careers.html')

@bp.route('/legal')
def legal():
    return render_template('main/legal.html')