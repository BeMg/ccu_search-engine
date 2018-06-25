import sqlite3

def create_table(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('CREATE TABLE if not exists data (link, name, price, tags)')
    conn.commit()
    conn.close()

def get_all_data(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('SELECT * FROM data')
    rst = c.fetchall()
    return rst

def Insert_and_remove_already_have(filename, Data):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    for link, name, price, discount, feature in Data:
        c.execute("DELETE FROM data WHERE link=?", (link,))
        if discount is None:
            pass
        elif price is None:
            pass
        else:
            price = min(price, discount)
        c.execute("INSERT INTO data VALUES (?,?,?,?)", (link, name, price, feature))
    conn.commit()
    conn.close()

create_table('merge.db')
Insert_and_remove_already_have('merge.db' ,get_all_data('steamData.db'))
Insert_and_remove_already_have('merge.db' ,get_all_data('gogData.db'))

