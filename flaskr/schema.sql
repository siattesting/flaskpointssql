-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS merchants;
DROP TABLE IF EXISTS redemptions;
DROP TABLE IF EXISTS vouchers;

-- Create the tables.

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  points INTEGER DEFAULT 0
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_id INTEGER,
  receiver_id INTEGER,
  points INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sender_id) REFERENCES user (id),
  FOREIGN KEY (receiver_id) REFERENCES user (id)
);

DROP TABLE IF EXISTS merchants;
CREATE TABLE merchants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL DEFAULT "testing1234",
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

);

DROP TABLE IF EXISTS redemptions;
CREATE TABLE redemptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  merchant_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  points INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (merchant_id) REFERENCES merchants (id),
  FOREIGN KEY (user_id) REFERENCES user (id)
);

DROP TABLE IF EXISTS vouchers;
CREATE TABLE vouchers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  merchant_id INTEGER NOT NULL,
  user_id INTEGER, 
  voucher_id INTEGER,
  code TEXT UNIQUE NOT NULL,
  points_redeemed INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (merchant_id) REFERENCES merchants (id),
  FOREIGN KEY (user_id) REFERENCES user (id)
);
