from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    g
)

from board.auth import login_required
from board.database import get_db

bp = Blueprint("points", __name__)

@bp.route('/points')
def points():
    db = get_db()
    if 'user_id' in session:
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
            ).fetchone()
        user = g.user['id']        
        
        points = db.execute(
            "SELECT p.id, user_id, points, updated_at, username FROM points p JOIN users u ON p.user_id = u.id ORDER BY updated_at DESC;"
        ).fetchall()
        return render_template('points/points.html', user=user, points=points)
    return redirect(url_for('login'))


@bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    

    else:
        user_id = session.get('user_id')
        g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        user = g.user['id'] 

    sender_id = session['user_id']
    receiver_id = request.form['receiver_id']
    points = int(request.form['points'])

    db = get_db()

    sender_points = db.execute('SELECT points FROM points WHERE user_id = ?', [sender_id]).fetchone()
    if not sender_points or sender_points['points'] < points:
        flash('Insufficient points')
        return redirect(url_for('points.points'))

    db.execute('UPDATE points SET points = points - ? WHERE user_id = ?', [points, sender_id])
    db.execute('UPDATE points SET points = points + ? WHERE user_id = ?', [points, receiver_id])
    db.execute('INSERT INTO transactions (sender_id, receiver_id, points) VALUES (?, ?, ?)', 
               [sender_id, receiver_id, points])
    db.commit()


    # below code is using SQL Alchemy delete the following if unused
    # sender = Points.query.filter_by(user_id=sender_id).first()
    # receiver = Points.query.filter_by(user_id=receiver_id).first()

    # if sender.points < points:
    #     return jsonify({"error": "Insufficient points"}), 400

    # sender.points -= points
    # receiver.points += points
    
    # transaction = Transactions(sender_id=sender_id, receiver_id=receiver_id, points=points)
    # db.session.add(transaction)
    # db.session.commit()

    return redirect(url_for('points.points'))

@bp.route('/redeem', methods=['POST'])
@login_required
def redeem():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    points = int(request.form['points'])
    item = request.form['item']

    user_points = get_db().execute('SELECT points FROM points WHERE user_id = ?', [user_id]).fetchone()


    if user_points.points < points:
        return jsonify({"error": "Insufficient points"}), 400

    user_points.points -= points
    # redemption = Redemptions(user_id=user_id, points=points, item=item)
    # db.session.add(redemption)
    # db.session.commit()

    return redirect(url_for('points.points'))

# @bp.route("/transfer", methods=("GET", "POST"))
# def create():
#     if request.method == "POST":
#         author = g.user['id']
#         title = request.form["title"] or "No Title"
#         body = request.form["body"]
#         error = None

#         if not title:
#             error = 'Title is required.'
#         if not body:
#             error = 'A comment or message is required.'
#         if error is not None:
#             flash(error)
#         else:

#             db = get_db()
#             db.execute(
#                 "INSERT INTO blogposts (author_id, title, body) VALUES (?, ?, ?)",
#                 (g.user['id'], title, body),
#             )
#             db.commit()
#             return redirect(url_for("points.points"))

#     return render_template("posts/create.html")


