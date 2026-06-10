import sqlite3
import datetime
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        referred_by INTEGER,
        is_verified INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        wallet_balance REAL DEFAULT 0.0,
        total_earned REAL DEFAULT 0.0,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Points Table
    c.execute('''CREATE TABLE IF NOT EXISTS points (
        user_id INTEGER PRIMARY KEY,
        total_points INTEGER DEFAULT 0,
        lifetime_points INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')

    # Referrals Table
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER,
        points_given INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(referred_id)
    )''')

    # Channels Table
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT UNIQUE,
        channel_name TEXT,
        channel_link TEXT,
        is_active INTEGER DEFAULT 1,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Redeem Requests Table
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        points_used INTEGER,
        amount REAL,
        payment_details TEXT,
        payment_method TEXT DEFAULT 'UPI',
        status TEXT DEFAULT 'pending',
        admin_note TEXT,
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
        processed_at TEXT
    )''')

    # Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # Transactions/Wallet History Table
    c.execute('''CREATE TABLE IF NOT EXISTS wallet_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        points INTEGER DEFAULT 0,
        amount REAL DEFAULT 0.0,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Admins Table
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        added_by INTEGER,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Default Settings
    defaults = [
        ("points_per_referral", "10"),
        ("bot_active", "1"),
        ("welcome_message", "Swagat hai aapka! 🎉"),
        ("min_redeem_points", "100"),
    ]
    for key, val in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ============================================================
# USER FUNCTIONS
# ============================================================

def add_user(user_id, username, full_name, referred_by=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, full_name, referred_by)
                 VALUES (?, ?, ?, ?)''', (user_id, username, full_name, referred_by))
    c.execute("INSERT OR IGNORE INTO points (user_id, total_points, lifetime_points) VALUES (?, 0, 0)", (user_id,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def is_user_exists(user_id):
    return get_user(user_id) is not None

def set_verified(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_verified(user_id):
    user = get_user(user_id)
    return user and user["is_verified"] == 1

def is_banned(user_id):
    user = get_user(user_id)
    return user and user["is_banned"] == 1

def ban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_total_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_user_ids():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    ids = [row[0] for row in c.fetchall()]
    conn.close()
    return ids

# ============================================================
# POINTS & WALLET FUNCTIONS
# ============================================================

def get_points(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT total_points, lifetime_points FROM points WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"total": row[0], "lifetime": row[1]}
    return {"total": 0, "lifetime": 0}

def add_points(user_id, points, description="Points added"):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE points SET total_points = total_points + ?,
                 lifetime_points = lifetime_points + ?
                 WHERE user_id = ?''', (points, points, user_id))
    # Wallet history
    c.execute('''INSERT INTO wallet_history (user_id, type, points, description)
                 VALUES (?, 'credit', ?, ?)''', (user_id, points, description))
    conn.commit()
    conn.close()

def deduct_points(user_id, points, description="Points deducted"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE points SET total_points = total_points - ? WHERE user_id = ?", (points, user_id))
    c.execute('''INSERT INTO wallet_history (user_id, type, points, description)
                 VALUES (?, 'debit', ?, ?)''', (user_id, points, description))
    conn.commit()
    conn.close()

def get_wallet_history(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM wallet_history WHERE user_id = ?
                 ORDER BY created_at DESC LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def get_wallet_balance(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT wallet_balance, total_earned FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"balance": row[0], "total_earned": row[1]}
    return {"balance": 0, "total_earned": 0}

# ============================================================
# REFERRAL FUNCTIONS
# ============================================================

def add_referral(referrer_id, referred_id, points):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO referrals (referrer_id, referred_id, points_given)
                     VALUES (?, ?, ?)''', (referrer_id, referred_id, points))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_referral_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def has_been_referred(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM referrals WHERE referred_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

# ============================================================
# CHANNEL FUNCTIONS
# ============================================================

def add_channel(channel_id, channel_name, channel_link):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO channels (channel_id, channel_name, channel_link)
                     VALUES (?, ?, ?)''', (str(channel_id), channel_name, channel_link))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def remove_channel(channel_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE channel_id = ?", (str(channel_id),))
    conn.commit()
    conn.close()

def get_all_channels():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM channels WHERE is_active = 1")
    rows = c.fetchall()
    conn.close()
    return rows

# ============================================================
# REDEEM FUNCTIONS
# ============================================================

def create_redeem_request(user_id, points, amount, payment_details, payment_method="UPI"):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO redeem_requests (user_id, points_used, amount, payment_details, payment_method)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, points, amount, payment_details, payment_method))
    req_id = c.lastrowid
    conn.commit()
    conn.close()
    return req_id

def get_pending_redeems():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT r.*, u.username, u.full_name FROM redeem_requests r
                 JOIN users u ON r.user_id = u.user_id
                 WHERE r.status = 'pending'
                 ORDER BY r.requested_at ASC''')
    rows = c.fetchall()
    conn.close()
    return rows

def process_redeem(req_id, status, admin_note=""):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute('''UPDATE redeem_requests SET status = ?, admin_note = ?, processed_at = ?
                 WHERE id = ?''', (status, admin_note, now, req_id))
    # Get request details
    c.execute("SELECT * FROM redeem_requests WHERE id = ?", (req_id,))
    req = c.fetchone()
    conn.commit()
    conn.close()
    return req

def get_redeem_by_id(req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM redeem_requests WHERE id = ?", (req_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_redeems(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM redeem_requests WHERE user_id = ?
                 ORDER BY requested_at DESC LIMIT 5''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ============================================================
# SETTINGS FUNCTIONS
# ============================================================

def get_setting(key, default=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

# ============================================================
# LEADERBOARD & STATS
# ============================================================

def get_leaderboard(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT u.user_id, u.username, u.full_name,
                        p.total_points, p.lifetime_points,
                        COUNT(r.id) as referral_count
                 FROM users u
                 LEFT JOIN points p ON u.user_id = p.user_id
                 LEFT JOIN referrals r ON u.user_id = r.referrer_id
                 WHERE u.is_banned = 0
                 GROUP BY u.user_id
                 ORDER BY p.lifetime_points DESC
                 LIMIT ?''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_rank(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) + 1 FROM points
                 WHERE lifetime_points > (SELECT lifetime_points FROM points WHERE user_id = ?)
                 AND user_id IN (SELECT user_id FROM users WHERE is_banned = 0)''', (user_id,))
    rank = c.fetchone()[0]
    conn.close()
    return rank

def get_admin_stats():
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM users")
    stats["total_users"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_verified = 1")
    stats["verified_users"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM referrals")
    stats["total_referrals"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM redeem_requests WHERE status = 'pending'")
    stats["pending_redeems"] = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM redeem_requests WHERE status = 'approved'")
    total = c.fetchone()[0]
    stats["total_paid"] = total if total else 0
    c.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
    stats["active_channels"] = c.fetchone()[0]
    conn.close()
    return stats

# ============================================================
# ADMIN FUNCTIONS
# ============================================================

def add_admin(user_id, username, added_by):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id, username, added_by) VALUES (?, ?, ?)",
              (user_id, username, added_by))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_all_admins():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins")
    ids = [row[0] for row in c.fetchall()]
    conn.close()
    return ids

def is_admin(user_id):
    from config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        return True
    return user_id in get_all_admins()
