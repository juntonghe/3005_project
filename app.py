######################################
# Edited by:
###################################################

import flask
from flask import Flask, session, Response, request, render_template, redirect, url_for
import flask_login

import datetime
from datetime import timedelta

import pgConnect


app = Flask(__name__)
app.secret_key = '123456'
app.config['SESSION_COOKIE_NAME'] = "session_key"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=3600)  # Seconds
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


def getUserList():
    sql = "select user_nickname from Users"
    rows = pgConnect.select(sql)
    return rows


class User(flask_login.UserMixin):
    pass


def getSessionNickName():
    nickname = None
    try:
        nickname = session['nickname']
    except:
        print("Need Login")
    return nickname


@login_manager.user_loader
def user_loader(nickname):
    users = getUserList()
    if nickname in users:
        user = User()
        user.nickname = nickname
        user.type = "owner"
        return user
    else:
        return


# default page
@app.route("/", methods=['GET'])
def hello():
    return flask.redirect(flask.url_for('login'))


@app.route("/owner_book", methods=['GET'])
def owner_book():
    sql = '''
        select book_isbn, book_name, book_pages, book_price, book_percentage,
          book_quantity, book_threshold, (a.author_firstname || ' ' ||a.author_lastname) author_name, g.genre_name, p.publisher_name
        from Book b, Author a, Genre g, Publisher p
        Where b.author_id = a. author_id
        And b.genre_id = g.genre_id
        And b.publisher_id = p.publisher_id
    '''
    books = pgConnect.select(sql)
    return render_template('owner_book.html', books=books)


@app.route("/owner_add_book", methods=['GET', 'POST'])
def owner_add_book():
    if flask.request.method == 'GET':
        return render_template('owner_add_book.html')
    else:
        book_isbn = flask.request.form['book_isbn']
        book_name = flask.request.form['book_name']
        book_pages = flask.request.form['book_pages']
        book_price = flask.request.form['book_price']
        book_percentage = flask.request.form['book_percentage']
        book_quantity = flask.request.form['book_quantity']
        book_threshold = flask.request.form['book_threshold']
        author_id = flask.request.form['author_id']
        genre_id = flask.request.form['genre_id']
        publisher_id = flask.request.form['publisher_id']
        sql = '''insert into Book(book_isbn,book_name,book_pages,book_price, book_percentage,
                  book_quantity, book_threshold, author_id, genre_id, publisher_id) 
                  values({},\'{}\',{},{},{},{},{},{},{},{})'''.format(
                    book_isbn, book_name, book_pages, book_price, book_percentage,
                    book_quantity, book_threshold, author_id, genre_id, publisher_id
        )
        result, error_msg = pgConnect.update(sql)
        if result:
            return flask.redirect(flask.url_for('owner_book'))
        else:
            return render_template('owner_add_book.html', error_msg=error_msg)


@app.route("/owner_remove_book", methods=['GET'])
def owner_remove_book():
    book_isbn = request.args.get('book_isbn')
    sql = '''
        delete from Book Where book_isbn={}
    '''.format(book_isbn)
    pgConnect.update(sql)
    return flask.redirect(flask.url_for('owner_book'))


@app.route("/owner_report", methods=['GET'])
def owner_report():
    sql = '''
        select order_id, order_totalprice
        from \"Order\"
    '''
    orders = pgConnect.select(sql)
    return render_template('owner_report.html', orders=orders)


@app.route("/owner_email", methods=['GET'])
def owner_email():
    sql = '''
        select email_id, b.book_isbn, b.book_name, p.publisher_id, p.publisher_name, book_num
        from email e, Book b, Publisher p
        Where e.book_isbn = b.book_isbn And e.publisher_id = p.publisher_id
    '''
    emails = pgConnect.select(sql)
    return render_template('owner_email.html', emails=emails)


@app.route("/customer_book", methods=['GET', 'POST'])
def customer_book():
    if flask.request.method == 'GET':
        sql = '''
            select book_isbn, book_name, book_pages, book_price,
              book_quantity, (a.author_firstname || ' ' ||a.author_lastname) author_name, g.genre_name, p.publisher_name
            from Book b, Author a, Genre g, Publisher p
            Where b.author_id = a. author_id
            And b.genre_id = g.genre_id
            And b.publisher_id = p.publisher_id
        '''
        books = pgConnect.select(sql)
        return render_template('customer_book.html', books=books)
    else:
        search_value = flask.request.form['search_value']
        search_type = flask.request.form['search_type']
        sql = '''
            select *
            from (
                select book_isbn, book_name, book_pages, book_price,
                  book_quantity, (a.author_firstname || ' ' ||a.author_lastname) author_name, g.genre_name, p.publisher_name
                from Book b, Author a, Genre g, Publisher p
                Where b.author_id = a. author_id
                And b.genre_id = g.genre_id
                And b.publisher_id = p.publisher_id
            )temp
            Where {}='{}'
        '''.format(search_type, search_value)
        books = pgConnect.select(sql)
        return render_template('customer_book.html', books=books)


@app.route("/customer_basket", methods=['GET'])
def customer_basket():
    nickname = getSessionNickName()
    if not nickname:
        return flask.redirect(flask.url_for('login'))
    sql = '''
        select book_isbn, book_num
        from Basket
        Where user_nickname = '{}'
    '''.format(nickname)
    baskets = pgConnect.select(sql)
    return render_template('customer_basket.html', baskets=baskets)


@app.route("/customer_add_basket", methods=['GET'])
def customer_add_basket():
    nickname = getSessionNickName()
    if not nickname:
        return flask.redirect(flask.url_for('login'))
    book_isbn = request.args.get('book_isbn')
    sql = '''
        select book_num from Basket 
        Where user_nickname = '{}' And book_isbn = {} 
    '''.format(nickname, book_isbn)
    rows = pgConnect.select(sql)
    if rows:
        sql = '''
            Update Basket Set book_num = book_num + 1
            Where user_nickname = '{}' And book_isbn = {};
        '''.format(nickname, book_isbn)
        result, error_msg = pgConnect.update(sql)
    else:
        sql = '''
                    insert into Basket(user_nickname, book_isbn, book_num)
                    values('{}', {}, {})
                '''.format(nickname, book_isbn, 1)
        result, error_msg = pgConnect.update(sql)
    return flask.redirect(flask.url_for('customer_book'))


@app.route("/customer_add_order", methods=['GET', 'POST'])
def customer_add_order():
    nickname = getSessionNickName()
    if not nickname:
        return flask.redirect(flask.url_for('login'))
    if flask.request.method == 'GET':
        sql = '''
        select sum(ba.book_num * bo.book_price) as order_totalprice
        from Basket ba, Book bo
        where ba.book_isbn = bo.book_isbn
        And user_nickname = '{}'
        group by ba.user_nickname
        '''.format(nickname)
        rows = pgConnect.select(sql)
        order_totalprice = rows[0][0]
        return render_template('customer_add_order.html', user_nickname=nickname, order_totalprice=order_totalprice)
    if flask.request.method == 'POST':
        nickname = flask.request.form['user_nickname']
        order_totalprice = flask.request.form['order_totalprice']
        order_billing = flask.request.form['order_billing']
        order_shipping = flask.request.form['order_shipping']
        sql = '''
            select user_nickname, book_isbn, book_num
            from Basket
            where user_nickname='{}'
        '''.format(nickname)
        rows = pgConnect.select(sql)
        for row in rows:
            book_isbn, book_num = row[1], row[2]
            sql = '''
                update Book Set book_quantity = book_quantity - {}
                where book_isbn = {}
            '''.format(book_num, book_isbn)
            result, error_msg = pgConnect.update(sql)
            print("update Book {}".format(str(result)))
            sql = '''
                select book_quantity, book_threshold, publisher_id
                from Book
                Where book_isbn = {}
            '''.format(book_isbn)
            books = pgConnect.select(sql)
            book_quantity, book_threshold, publisher_id = books[0][0], books[0][1], books[0][2]
            if book_quantity < book_threshold:
                sql = '''
                    insert into Email(book_isbn, publisher_id, book_num)
                    values({},{},{})
                '''.format(book_isbn, publisher_id, (book_threshold - book_quantity))
                result, error_msg = pgConnect.update(sql)
                print("insert into Email {}".format(str(result)))
        sql = '''
            insert into \"Order\"(user_nickname, order_totalprice, order_billing, order_shipping)
            values('{}', {}, '{}', '{}');
            delete from Basket Where user_nickname='{}';
        '''.format(nickname, order_totalprice, order_billing, order_shipping, nickname)
        result, error_msg = pgConnect.update(sql)
        if result:
            return flask.redirect(flask.url_for('customer_order'))
        else:
            return render_template('customer_add_order.html', user_nickname=nickname, order_totalprice=order_totalprice,
                                   error_msg=error_msg)


@app.route("/customer_order", methods=['GET'])
def customer_order():
    nickname = getSessionNickName()
    if not nickname:
        return flask.redirect(flask.url_for('login'))
    sql = '''
        select order_id, user_nickname, order_totalprice, order_billing, order_shipping
        from \"Order\"
        Where user_nickname = '{}'
    '''.format(nickname)
    orders = pgConnect.select(sql)
    return render_template('customer_order.html', orders=orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')
    else:
        #The request method is POST (page is recieving data)
        user_nickname = flask.request.form['user_nickname']
        user_password = flask.request.form['user_password']
        user_type = flask.request.form['user_type']
        sql = "select user_password, user_type from Users where user_nickname='{}'".format(user_nickname)
        rows = pgConnect.select(sql)
        if rows and user_password == rows[0][0] and user_type == rows[0][1]:
            user = User()
            user.nickname = user_nickname
            user.type = user_type
            session['nickname'] = str(user_nickname)
            if user_type == 'customer':
                return flask.redirect(flask.url_for('customer_book'))
            elif user_type == 'owner':
                return flask.redirect(flask.url_for('owner_add_book'))
        #information did not match
        error_msg = "Login Failed!"
        return render_template('login.html', error_msg=error_msg)


@app.route("/customer_order_track", methods=['GET'])
def customer_order_track():
    nickname = getSessionNickName()
    if not nickname:
        return flask.redirect(flask.url_for('login'))
    order_id = request.args.get('order_id')
    curr_time = datetime.datetime.now()
    time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
    order_tracks = [[order_id, time_str, 'Shipped in transit']]
    sql = '''
            select order_id, user_nickname, order_totalprice, order_billing, order_shipping
            from \"Order\"
            Where user_nickname = '{}'
        '''.format(nickname)
    orders = pgConnect.select(sql)
    return render_template('customer_order.html', orders=orders, order_tracks=order_tracks)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html')


@app.route("/register_user", methods=['POST'])
def register_user():
    user_nickname = flask.request.form['user_nickname']
    user_password = flask.request.form['user_password']
    user_type = flask.request.form['user_type']
    user_firstname = flask.request.form['user_firstname']
    user_lastname = flask.request.form['user_lastname']
    user_dob = flask.request.form['user_dob']
    user_billing = flask.request.form['user_billing']
    user_shipping = flask.request.form['user_shipping']
    sql = '''insert into Users(user_nickname,user_password,user_type,user_firstname, user_lastname,
                      user_dob, user_billing, user_shipping) 
                      values(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'''.format(
        user_nickname, user_password, user_type, user_firstname, user_lastname,
        user_dob, user_billing, user_shipping
    )
    result, error_msg = pgConnect.update(sql)
    if result:
        return flask.redirect(flask.url_for('login'))
    else:
        return render_template('register.html', error_msg=error_msg)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
