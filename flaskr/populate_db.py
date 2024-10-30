import random

from flask import Flask

from flaskr.db import get_db

db = get_db()

# generate 5 random merchants using the schema in schema.sql with their name, address, email, password
def create_random_merchants():
    merchants = [
        ("Merchant 1", "123 Main St", "merchant1@example.com", "password1"),
        ("Merchant 2", "456 Elm St", "merchant2@example.com", "password2"),
        ("Merchant 3", "789 Oak St", "merchant3@example.com", "password3"),
        ("Merchant 4", "101 Maple St", "merchant4@example.com", "password4"),
        ("Merchant 5", "123 Willow St", "merchant5@example.com", "password5"),
    ]

    for merchant in merchants:
        db.execute(
            "INSERT INTO merchant (name, address, email, password) VALUES (?,?,?,?)",
            merchant
        )
        db.commit()

# for each merchant, generate 5 coupons code randomly between 400 and 100 points. according to the following schema:
# CREATE TABLE vouchers (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   merchant_id INTEGER NOT NULL,
#   code TEXT UNIQUE NOT NULL,
#   points_redeemed INTEGER NOT NULL,
#   status TEXT NOT NULL DEFAULT 'active',
#   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   FOREIGN KEY (merchant_id) REFERENCES merchants (id)
# );

def create_random_coupons():
    merchants = db.execute("SELECT id FROM merchants").fetchall()

    for merchant in merchants:
        for _ in range(5):
            code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
            points_redeemed = random.randint(400, 1000)

            db.execute(
                "INSERT INTO vouchers (merchant_id, code, points_redeemed) VALUES (?,?,?)",
                (merchant['id'], code, points_redeemed)
            )
            db.commit()



