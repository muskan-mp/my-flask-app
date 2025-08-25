from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import string
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database initialization
def init_db():
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  long_url TEXT NOT NULL,
                  short_code TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  clicks INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Generate short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Check if short code exists
def short_code_exists(short_code):
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Get total links and clicks
def get_stats():
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(clicks) FROM urls")
    result = c.fetchone()
    conn.close()
    return result[0] or 0, result[1] or 0

@app.route('/')
def index():
    total_links, total_clicks = get_stats()
    return render_template('index.html', total_links=total_links, total_clicks=total_clicks)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('long_url')
    custom_code = request.form.get('custom_code')
    
    if not long_url:
        flash('Please enter a URL', 'error')
        return redirect(url_for('index'))
    
    # Add https:// if missing
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url
    
    # Check if custom code is provided and valid
    if custom_code:
        if short_code_exists(custom_code):
            flash('Custom name already exists. Please choose another one.', 'error')
            return redirect(url_for('index'))
        short_code = custom_code
    else:
        # Generate a unique short code
        short_code = generate_short_code()
        while short_code_exists(short_code):
            short_code = generate_short_code()
    
    # Save to database
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", 
              (long_url, short_code))
    conn.commit()
    conn.close()
    
    short_url = request.host_url + short_code
    flash('URL shortened successfully!', 'success')
    total_links, total_clicks = get_stats()
    return render_template('index.html', short_url=short_url, long_url=long_url, 
                           total_links=total_links, total_clicks=total_clicks)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    
    if result:
        long_url = result[0]
        # Update click count
        c.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,))
        conn.commit()
        conn.close()
        return redirect(long_url)
    else:
        conn.close()
        flash('URL not found', 'error')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT * FROM urls ORDER BY created_at DESC")
    urls = c.fetchall()
    conn.close()
    
    # Format the data for the template
    url_list = []
    for url in urls:
        url_list.append({
            'id': url[0],
            'long_url': url[1],
            'short_code': url[2],
            'created_at': url[3],
            'clicks': url[4],
            'short_url': request.host_url + url[2]
        })
    
    return render_template('history.html', urls=url_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)