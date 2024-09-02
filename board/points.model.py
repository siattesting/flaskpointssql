

from flask import g, session
from board.database import get_db


def getpoints():
    db = get_db()
    points = db.execute("SELECT * FROM points ORDER BY created DESC").fetchall()

    return points

def get_points_by_id(user_id):
    db = get_db()
    if 'user_id' in session:
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
            ).fetchone()
        
        points = db.execute(
            "SELECT p.id, user_id, points, updated_at, username FROM points p JOIN users u ON p.user_id = u.id ORDER BY updated_at DESC;"
        ).fetchall()

        return points

