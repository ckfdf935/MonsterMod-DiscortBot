import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1)''')

    conn.commit()
    conn.close()


def update_xp(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))

    res = c.fetchone()
    if not res:
        c.execute("INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)", (user_id, 1, 1))
        conn.commit()
        conn.close()
        return False

    xp, level = res
    new_xp = xp + 1
    next_lvl_xp = level *10

    if new_xp >= next_lvl_xp:

        c.execute("UPDATE users SET xp = 0, level = ? WHERE user_id = ?", (level + 1, user_id))
        conn.commit()
        c.close()
        return level + 1

    else:

        c.execute("UPDATE users SET xp = ? WHERE user_id = ?", (new_xp, user_id))
        conn.commit()
        conn.close()
        return False

def get_profile(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return res
    else:
        return (0,1)
