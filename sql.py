from conf import cur, conn


def add_user(first_name, username, user_id):
    cur.execute('SELECT EXISTS(SELECT 1 FROM about WHERE user_id = %s)', (user_id,))
    if cur.fetchone()[0]:
        cur.execute('UPDATE about SET name = %s, username = %s WHERE user_id = %s', (first_name, username, user_id))
    else:
        cur.execute("INSERT INTO about (user_id, name, username) VALUES (%s, %s, %s)",
                    (user_id, first_name, username))
    conn.commit()


def add_links(user_id, ozon='', wb='', price=''):
    cur.execute('SELECT EXISTS(SELECT 1 FROM decrip WHERE user_id = %s AND (ozon = %s AND wb = %s))', (user_id, ozon, wb))
    if cur.fetchone()[0]:
        cur.execute("UPDATE decrip SET price = %s WHERE user_id = %s AND (ozon = %s AND wb = %s)", (price, user_id, ozon, wb))
    else:
        cur.execute("INSERT INTO decrip (user_id, ozon, wb, price) VALUES (%s, %s, %s, %s)", (user_id, ozon, wb, price))
    conn.commit()

"""
def dicount_on_WB(user_id, discount):
    cur.execute('UPDATE about SET "dicount_on_WB" = %s WHERE user_id = %s',
                (discount, user_id))
    conn.commit()


def get_discount(user_id):
    cur.execute('SELECT "dicount_on_WB" FROM about WHERE user_id = %s;', (user_id,))
    discount = cur.fetchone()[0]
    return discount"""