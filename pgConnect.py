######################################
# Edited by:
###################################################

import psycopg2


def update(sql):
    conn = psycopg2.connect(database="Book",user="postgres",password="postgres",host="127.0.0.1",port="5432")
    cur = conn.cursor()
    print(sql)
    result, error_msg = True, ""
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        result, error_msg = False, str(e)
    conn.close()
    return result, error_msg


def select(sql):
    conn = psycopg2.connect(database="Book", user="postgres", password="postgres", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()
    return rows


sql = "insert into Users(user_nickname, user_password, user_type) values('user1', 'user1', 'consumer')"
update(sql)
sql = "insert into Users(user_nickname, user_password, user_type) values('owner1', 'owner1', 'owner')"
update(sql)
sql = "select * from Users"
select(sql)
