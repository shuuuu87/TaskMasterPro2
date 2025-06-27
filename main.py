from app import app  # this imports the real app from app.py
from flask import send_from_directory

# Serve robots.txt from the static folder
@app.route('/robots.txt')
def static_robots():
    return send_from_directory('static', 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
