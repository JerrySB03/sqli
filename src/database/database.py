import sqlite3
# Import hashing algorithm
from hashlib import sha256

def query(con, query, args=(), one=False):
    c = con.cursor()
    # Make it sql injection vulnerable
    for arg in args:
        query = query.replace('?',  '\'' + str(arg) + '\'', 1)
    c.execute(query)
    rv = [dict((c.description[idx][0], value)
               for idx, value in enumerate(row) if value != None) for row in c.fetchall()]
    return (rv[0] if rv else None) if one else rv


def db_init():
    con = sqlite3.connect('data.db')
    # Create users database
    query(con, '''
    CREATE TABLE IF NOT EXISTS users (
        id integer PRIMARY KEY,
        username text UNIQUE NOT NULL,
        password text NOT NULL,
        description text
    );
    ''')
    query(con, '''
    CREATE TABLE IF NOT EXISTS notes (
        id integer PRIMARY KEY,
        user_id integer REFERENCES users (id),
        title text NOT NULL UNIQUE,
        content text NOT NULL
    );
    ''')
    # Database seeding
    try:
        query(con, '''
            INSERT INTO users(
                username,
                password,
                description)
                VALUES (
            'admin',
            'uwu',
            'I am the admin!!!'
            );
            ''')
    except:
        pass
    try:
        query(con, '''
        INSERT INTO notes (user_id,
        title,
        content)
        VALUES (
            1,
            'flag',
            'flag{$ql_!nj3cti0n_1s_4w3s0m3}'
        );
        ''')
    except:
        pass

    


    con.commit()


def db_login(username, password):
    con = sqlite3.connect('data.db')
    user = query(con, 'SELECT username FROM users WHERE username = ? AND password = ?',
                 (username, sha256(password.encode()).hexdigest(),), True)

    return user


def db_register(username, password, description):
    con = sqlite3.connect('data.db')
    user = query(con, 'SELECT username FROM users WHERE username = ?',
                 (username,), True)

    if user:
        return False
    
    query(con, 'INSERT into users (username, password, description) VALUES (?, ?, ?)',
            (username, sha256(password.encode()).hexdigest(), description, ))
    result = query(
        con, 'SELECT id FROM users WHERE username = ?', (username,), True)
    con.commit()

    return result['id']


def db_get_user_by_username(username):
    con = sqlite3.connect('data.db')
    user = query(con, 'SELECT * FROM users WHERE username = ?',
                 (username,), True)
    user['notes'] = query(con, 'SELECT * FROM notes WHERE user_id = ?',
                          (user['id'],))

    con.commit()

    return user


def db_get_user_by_id(id):
    con = sqlite3.connect('data.db')
    user = query(con, 'SELECT * FROM users WHERE id = ?', (id,), True)
    if user == None:
        return None
    user['notes'] = query(con, 'SELECT * FROM notes WHERE user_id = ?',
                          (user['id'],))
    con.commit()

    return user


def db_get_users():
    con = sqlite3.connect('data.db')
    users = query(con, 'SELECT * FROM users')

    con.commit()

    return users


def db_get_user_id(username):
    con = sqlite3.connect('data.db')
    user = query(con, 'SELECT id FROM users WHERE username = ?',
                 (username,), True)

    con.commit()

    return user['id']

def db_new_note(user_id, title, content):
    con = sqlite3.connect('data.db')
    note_id = query(con, 'INSERT into notes (user_id, title, content) VALUES (?, ?, ?) RETURNING id',
          (user_id, title, content, ), True)['id']
    con.commit()

    return note_id

def db_remove_note_by_id(id, user_id):
    con = sqlite3.connect('data.db')
    query(con, 'DELETE FROM notes WHERE id = ? AND user_id = ?', (id, user_id,))
    con.commit()

    return True

def db_get_note_by_id(id):
    con = sqlite3.connect('data.db')
    note = query(con, 'SELECT * FROM notes WHERE id = ?',
                 (id,), True)

    con.commit()

    return note