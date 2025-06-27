from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/robots.txt')
def robots_txt():
    return Response("""
    User-agent: *
    Disallow: /login
    Disallow: /register
    Disallow: /profile
    Disallow: /dashboard
    Disallow: /admin
    Allow: /

    Sitemap: https://taskmasterpro-b1nt.onrender.com/sitemap.xml
    """, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
