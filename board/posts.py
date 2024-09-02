from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    g
)

from board.auth import login_required
from board.database import get_db

bp = Blueprint("posts", __name__)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        author = g.user['id']
        title = request.form["title"] or "No Title"
        body = request.form["body"]
        error = None

        if not title:
            error = 'Title is required.'
        if not body:
            error = 'A comment or message is required.'
        if error is not None:
            flash(error)
        else:

            db = get_db()
            db.execute(
                "INSERT INTO blogposts (author_id, title, body) VALUES (?, ?, ?)",
                (g.user['id'], title, body),
            )
            db.commit()
            return redirect(url_for("posts.posts"))

    return render_template("posts/create.html")

@bp.route("/posts")
def posts():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, author_id, title, body, created, updated_at, username FROM blogposts p JOIN users u ON p.author_id = u.id ORDER BY updated_at DESC;"
    ).fetchall()
    return render_template("posts/posts.html", posts=posts)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, updated_at, author_id, username'
        ' FROM blogposts p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Comment or Message is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE blogposts SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('posts.posts'))

    return render_template('posts/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM blogposts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('posts.posts'))