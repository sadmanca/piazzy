from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os
from piazza_api import Piazza

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        piazza = Piazza()
        try:
            piazza.user_login(email=email, password=password)
            session['email'] = email
            session['password'] = password
            return redirect(url_for('courses'))
        except Exception as e:
            flash('Login failed: {}'.format(e))
    return render_template('login.html')

@app.route('/courses')
def courses():
    if 'email' not in session:
        return redirect(url_for('login'))
    piazza = Piazza()
    piazza.user_login(email=session['email'], password=session['password'])
    courses = piazza.get_user_classes()
    return render_template('courses.html', courses=courses)

@app.route('/course/<nid>')
def course_discussions(nid):
    if 'email' not in session:
        return redirect(url_for('login'))
    piazza = Piazza()
    piazza.user_login(email=session['email'], password=session['password'])
    network = piazza.network(nid)
    # Fetch all posts using pagination
    all_posts = []
    limit = 100
    offset = 0
    while True:
        feed = network.get_feed(limit=limit, offset=offset)
        posts = feed.get('feed', [])
        if not posts:
            break
        all_posts.extend(posts)
        if len(posts) < limit:
            break
        offset += limit
    # Fetch full post data for each post
    full_posts = []
    for post in all_posts:
        try:
            full_post = network.get_post(post['id'])
            full_posts.append(full_post)
        except Exception:
            continue
    return render_template('discussions.html', posts=full_posts, nid=nid)

@app.route('/course/<nid>/post/<cid>')
def view_post(nid, cid):
    if 'email' not in session:
        return redirect(url_for('login'))
    piazza = Piazza()
    piazza.user_login(email=session['email'], password=session['password'])
    network = piazza.network(nid)
    post = network.get_post(cid)
    return render_template('post.html', post=post)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
