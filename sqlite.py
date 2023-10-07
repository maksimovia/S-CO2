import sqlite3


def open_db():
    global connection
    global cursor

    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    if cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='streams' ''').fetchone() is None:
        cursor.execute('''CREATE TABLE IF NOT EXISTS streams
        (NAME TEXT DEFAULT NULL,
        T REAL DEFAULT NULL,
        P REAL DEFAULT NULL,
        H REAL DEFAULT NULL,
        S REAL DEFAULT NULL,
        Q REAL DEFAULT NULL,
        G REAL DEFAULT NULL,
        X TEXT DEFAULT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
        (NAME TEXT DEFAULT NULL,
        Q REAL DEFAULT NULL,
        dT REAL DEFAULT NULL)''')

        cursor.execute('''INSERT INTO streams(NAME) VALUES
        ('R-RHE'),
        ('RHE-R'),
        ('RHE-T'),
        ('T-HTR'),
        ('HTR-LTR'),
        ('LTR-SPLIT'),
        ('SPLIT-C'),
        ('SPLIT-RC'),
        ('C-MC'),
        ('MC-LTR'),
        ('LTR-MIX'),
        ('RC-MIX'),
        ('MIX-HTR'),
        ('HTR-RHE'),
        ('IN-C'),
        ('C-OUT')
        ''')

        cursor.execute('''INSERT INTO blocks(NAME) VALUES
        ('R'),
        ('RHE'),
        ('HTR'),
        ('LTR'),
        ('T'),
        ('RC'),
        ('MC'),
        ('C'),
        ('SPLIT'),
        ('MIX')
        ''')
    pass


def close_db():
    connection.commit()
    cursor.close()
    connection.close()
    pass


def write_stream(stream, t, p, h, s, q, g, x):
    cursor.execute('''UPDATE streams SET T=?,P=?, H=?, S=?, Q=?, G=?, X=? WHERE NAME==? ''',
                   [t, p, h, s, q, g, x, stream])
    pass


def write_block(block, q, dt):
    cursor.execute('''UPDATE blocks SET Q=?, DT=? WHERE NAME==? ''', [q, dt, block])
    pass


def read_block(block):
    q = cursor.execute('''SELECT Q FROM blocks WHERE NAME==? ''', [block]).fetchone()
    dt = cursor.execute('''SELECT DT FROM blocks WHERE NAME==? ''', [block]).fetchone()
    return {'Q': q[0],'DT': dt[0]}


def read_stream(stream):
    t = cursor.execute('''SELECT T FROM streams WHERE NAME==? ''', [stream]).fetchone()
    p = cursor.execute('''SELECT P FROM streams WHERE NAME==? ''', [stream]).fetchone()
    h = cursor.execute('''SELECT H FROM streams WHERE NAME==? ''', [stream]).fetchone()
    s = cursor.execute('''SELECT S FROM streams WHERE NAME==? ''', [stream]).fetchone()
    q = cursor.execute('''SELECT Q FROM streams WHERE NAME==? ''', [stream]).fetchone()
    g = cursor.execute('''SELECT G FROM streams WHERE NAME==? ''', [stream]).fetchone()
    x = cursor.execute('''SELECT X FROM streams WHERE NAME==? ''', [stream]).fetchone()
    return {'T': t[0], 'P': p[0], 'H': h[0], 'S': s[0], 'Q': q[0], 'G': g[0], 'X': x[0]}
