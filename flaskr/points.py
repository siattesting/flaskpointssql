import random
from flask import Blueprint, session
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash


from .auth import login_required
from .db import get_db

bp = Blueprint("points", __name__, url_prefix="/points")

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    db = get_db()
    user_id = int(g.user['id'])
    user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()

    return render_template('points/dashboard.html', user=user)

@bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        receiver_email = request.form['receiver']
        points_transferred = int(request.form['points'])

        if not receiver_email or not points_transferred:
            flash('Please fill out all fields.')
            return redirect(url_for('points.transfer'))
        
        db = get_db()
        receiver = db.execute("SELECT * FROM user WHERE email =?", (receiver_email,)).fetchone()
        sender = db.execute("SELECT * FROM user WHERE id =?", (session['user_id'],)).fetchone()

        if not receiver:
            flash('No user found with that email.')
            return redirect(url_for('points.transfer'))
        elif points_transferred > sender['points']:
            flash('Insufficient points.')
            return redirect(url_for('points.transfer'))
        else:
            try:
                with db:
                    db.execute("BEGIN TRANSACTION")
                    db.execute("UPDATE user SET points = points - ? WHERE id = ?", (points_transferred, session['user_id']))
                    db.execute("UPDATE user SET points = points + ? WHERE email = ?", (points_transferred, receiver_email))
                    # Update the transactions table to log this ytransaction
                    db.execute("INSERT INTO transactions (sender_id, receiver_id, points) VALUES (?,?,?)", (sender['id'], receiver['id'], points_transferred))
                    db.commit() # commit transaction
                    flash('Points transferred successfully.')
                    print('Points transferred successfully')
                return redirect(url_for('points.dashboard'))
            except Exception as e:
                db.rollback() # rollback transaction if something goes wrong
                flash(f'An error occurred: {str(e)}')
                print(f'An error occurred: {str(e)}')
                return redirect(url_for('points.transfer'))
    return render_template('points/dashboard.html')

@bp.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        voucher = request.form['voucher']

        db = get_db()
        user_id = int(session['user_id'])
        voucher_row = db.execute("SELECT * FROM vouchers WHERE code = ? AND status = ?", (voucher, 'active')).fetchone()

        if not voucher_row:
            flash('Invalid voucher.')
            print('Invalid voucher code')
            return redirect(url_for('points.redeem'))
        else:
            try:
                with db:
                    db.execute("BEGIN TRANSACTION")
                    db.execute("UPDATE user SET points = points + ? WHERE id = ?", (voucher_row['points_redeemed'], session['user_id']))
                    db.execute("UPDATE vouchers SET status = 'paid', user_id = ? WHERE code = ?", (user_id, voucher,))
                    db.commit() # commit transaction
                    flash('voucher redeemed successfully.')
                    print('Voucher redeemed successfully')
                return redirect(url_for('points.dashboard'))
            except Exception as e:
                db.rollback() # rollback transaction if something goes wrong
                flash(f'An error occurred: {str(e)}')
                print(f'An error occurred: {str(e)}')
                return redirect(url_for('points.redeem'))
            
    return render_template('points/dashboard.html')

@bp.route('/transactions/', methods=['GET', 'POST'])
@login_required
def transactions():
    # ths route is to view the history of tranasctions for the active user
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    user_id = int(session['user_id'])

    user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()

    transactions2 = db.execute("SELECT sender_id, receiver_id, points, created FROM transactions WHERE sender_id = ? OR receiver_id = ? ORDER BY created DESC", (user_id, user_id)).fetchall()

    # Fetch all transactions of points from the currently logged in user
    transactions = db.execute(
        'SELECT t.sender_id, t.receiver_id, t.points, t.created, u.email from transactions t '
        ' JOIN  user u ON t.sender_id = u.id OR t.receiver_id = u.id AND t.sender_id = ? OR t.receiver_id = ? ORDER BY created DESC', (user_id, user_id)).fetchall()
    
    # make a sum of all points received by the current user
    total_points_received = sum(t[2] for t in transactions if t[1] == user_id)
    total_points_sent = sum(t[2] for t in transactions if t[0] == user_id)

   
    # Fetch all redemptions of points from the currently logged in user
    redemptions = db.execute(
        "SELECT v.id,  code, points_redeemed, v.created, name FROM vouchers v JOIN merchants m ON v.merchant_id = m.id AND v.user_id = ? ORDER BY v.created DESC", (user_id,)).fetchall()
    for r in redemptions:
        print(r['name'])

    # make a sume of all points redeemed by the user
    total_points_redeemed = sum(r[2] for r in redemptions)

    balance_from_totals = total_points_received + total_points_redeemed - total_points_sent


    return render_template('points/transactions.html', 
                           transactions=transactions,
                            redemptions=redemptions, 
                            user=user,
                            total_points_received=total_points_received,
                            total_points_sent = total_points_sent,
                            total_points_redeemed=total_points_redeemed,
                            balance_from_totals=balance_from_totals)

@bp.route('/merchants', methods=['GET', 'POST'])
@login_required
def merchants():
    db = get_db()
    user = db.execute("SELECT * FROM user WHERE id = ?", (session['user_id'],)).fetchone()

    # Select all merchants
    merchants = db.execute("SELECT * FROM merchants").fetchall()

    # select data from vouchers combined with merchants to list vouchers with the name of the merchant and combined with USER to output the user's email
    voucherlist = db.execute(
        'SELECT v.id, v.code, v.points_redeemed,v. status, v.created, m.name,u.email '
        'FROM ((vouchers v JOIN merchants m ON v.merchant_id = m.id) '
        'LEFT JOIN user u ON v.user_id = u.id)').fetchall()
   
    # for v in voucherlist:
        # print(v['code'], v['name'], v['email'])

    return render_template('points/merchants.html', merchants=merchants, user=user, voucherlist=voucherlist)


@bp.route('/populate', methods=['GET', 'POST'])
@login_required
def populate():
    db = get_db()

    # Make this route accessible only to demba@me.com
    if 'user_id' not in session or session['email'] != 'demba@me.com':
        return redirect(url_for('auth.login'))
    
    # Create 5 users
    for i in range(5):
        db.execute(
            "INSERT INTO user (username, email, password) VALUES (?,?,?)",
            ("user" + str(i+1) + "@example.com", "user" + str(i+1) + "@example.com", generate_password_hash("testing1234"))

        )
        db.commit()


    # Make sure the database is empty before populating it
    # db = get_db()
    # db.execute("DELETE FROM merchants")
    # db.execute("DELETE FROM vouchers")
    # db.commit()
    # this route is to populate the database with sample data for testing
    merchants = [
        ("Merchant  11", "123 Main St", "merchant11@example.com", "password11"),
        ("Merchant 12", "456 Elm St", "merchant12@example.com", "password12"),
        ("Merchant 13", "789 Oak St", "merchant13@example.com", "password13"),
        ("Merchant 14", "101 Maple St", "merchant14@example.com", "password14"),
        ("Merchant 15", "123 Willow St", "merchant15@example.com", "password15"),
    ]

    for merchant in merchants:
        db.execute(
            "INSERT INTO merchants (name, description, email, password) VALUES (?,?,?,?)",
            merchant
        )
        db.commit()

    # get all the merchants from the database and create some vouchers
    merchants = db.execute("SELECT * FROM merchants").fetchall()

    for merchant in merchants:
        for _ in range(5):
            code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
            points_redeemed = random.randint(400, 1000)

            db.execute(
                "INSERT INTO vouchers (merchant_id, code, points_redeemed) VALUES (?,?,?)",
                (merchant['id'], code, points_redeemed)
            )
            db.commit()
    vouchers = db.execute("SELECT * FROM vouchers").fetchall()

    return render_template('points/merchants.html', merchants=merchants, vouchers=vouchers)