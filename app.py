import datetime
from flask import Flask, request, render_template_string, render_template, g, request, redirect, url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

import sqlite3
from flask_bootstrap import Bootstrap



# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app3.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'djangoman34@gmail.com'
    MAIL_PASSWORD = 'beehive34'
    MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"


def create_app():
    """ Flask application factory """

    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask-BabelEx
    babel = Babel(app)

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

        # Define the relationship to Role via UserRoles
        roles = db.relationship('Role', secondary='user_roles')


    # Define the Role data-model
    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # Create all database tables
    db.create_all()

    # Create 'member@example.com' user with no roles
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            email='member@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'luke.fernandez@gmail.com').first():
        user = User(
            email='luke.fernandez@gmail.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password2'),
        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    ##############  Books Stuff Below  ####################
    PATH = 'books.sqlite'

    def open_connection():
        connection = getattr(g, '_connection', None)
        if connection == None:
            connection = g._connection = sqlite3.connect(PATH)
        connection.row_factory = sqlite3.Row
        return connection

    def execute_sql(sql,values=(), commit=False, single=False):
        connection = open_connection()
        cursor = connection.execute(sql,values)
        if commit == True:
            results = connection.commit()
        else:
            results = cursor.fetchone() if single else cursor.fetchall()

        cursor.close()
        return results

    @app.teardown_appcontext
    def close_connection(exception):
        connection = getattr(g, '_connection', None)
        if connection is not None:
            connection.close()

    bootstrap = Bootstrap( app)

    @app.route('/xx')
    def home():
        db_admin()
        return render_template('index.html')

    @app.route('/all_books')
    def books():
        books = execute_sql('SELECT Category.description AS c_description, Book.description AS b_description, * FROM Category INNER JOIN Book ON Category.rowID=Book.category_id  ORDER BY c_description ASC')
        print(len(books))
        return render_template('all_books.html', books=books)

    @app.route('/seedDB')
    @roles_required('Admin')
    def seedDB():
        sqlQuery2 = execute_sql('INSERT INTO Book (author,title,isbn, description, category_id) VALUES ("Mary Shelly","Frankenstein","1", "A horror story written by a romantic.","1")',commit=True)
        sqlQuery2 = execute_sql('INSERT INTO Book (author,title,isbn, description, category_id) VALUES ("Henry James","The Turn of the Screw","2", "Another British horror story.","1")',commit=True)
        sqlQuery2 = execute_sql('INSERT INTO Book (author,title,isbn, description, category_id) VALUES ("Max Weber","The Protestant Work Ethic and The Spirit of Capitalism","3", "A classic early 20th C. sociology text","2")',commit=True)
        sqlQuery2 = execute_sql('INSERT INTO Book (author,title,isbn, description, category_id) VALUES ("Robert Putnam","Bowling Alone","4", "A classic late 20th C. sociology test","2")',commit=True)
        sqlQuery2 = execute_sql('INSERT INTO Category (description) VALUES ("Horror")',commit=True)
        sqlQuery2 = execute_sql('INSERT INTO Category (description) VALUES ("Sociology")',commit=True)

        booksQuery = execute_sql('SELECT rowid, * FROM Book')
        for book in booksQuery:
            print(book['rowid'])
            print(book['author'])

        books = execute_sql('SELECT Category.description AS c_description, Book.description AS b_description, * FROM Category INNER JOIN Book ON Category.rowID=Book.category_id ')
        for book in books:
            print('ddd')
            print(book['c_description'])
            print(book['b_description'])
            print(book['title'])

        return '<h1>DB Seeded!</h1>'

    @app.route('/erase_DB')
    @roles_required('Admin')
    def eraseDB():
            # sqlQ = execute_sql('DROP TABLE IF EXISTS Book',commit=True)
            # sqlQ = execute_sql('DROP TABLE IF EXISTS Category',commit=True)
            sqlQ = execute_sql('DELETE FROM Book',commit=True)
            sqlQ = execute_sql('DELETE FROM Category',commit=True)
            return '<h1>DB Erased!</h1>'

    def db_admin():
        sqlQuery = execute_sql('CREATE TABLE IF NOT EXISTS Book (author TEXT,title TEXT, isbn INTEGER, description TEXT, category_id INTEGER)',commit=True)
        sqlQuery = execute_sql('CREATE TABLE IF NOT EXISTS Category (description TEXT)',commit=True)


    @app.route('/addbook', methods={'GET','POST'})
    @login_required
    def addbook():
        if request.method == 'POST':
            author = request.form['author']
            title = request.form['title']
            isbn = request.form['isbn']
            description = request.form['description']
            category_field = request.form['category']

            categoryID = execute_sql('SELECT rowid, * FROM Category WHERE description = ? ',[category_field])
            if len(categoryID) == 0:
                returnStatus = execute_sql('INSERT INTO Category (description) VALUES (?)',[category_field],commit=True)
                returnQuery = execute_sql('SELECT last_insert_rowid()')
                categoryID = returnQuery[0][0]
                # or, instead of above two lines use this one instead:
                # categoryID = execute_sql('SELECT rowid, * FROM Category WHERE description = ? ',[category_field])
            else:
                categoryID = categoryID[0]['rowid']

            returnStatus = execute_sql('INSERT INTO Book (author, title, isbn, description, category_id) VALUES (?, ?, ?, ?, ?)',
            (author, title, isbn, description, categoryID),commit=True)

            return redirect(url_for('home'))

        categories = execute_sql('SELECT * FROM Category ORDER BY description ASC')
        return render_template('addbook.html', categories=categories)

    @app.route('/categories')
    @login_required
    def categories():
        categories = execute_sql('SELECT rowid, * FROM Category ORDER BY description ASC')
        for cat in categories:
            print(cat['rowid'])
        return render_template('categories.html', categories=categories)

    @app.route('/books_in_category/<categoryID>')
    @login_required
    def books_in_cat(categoryID):
        categories = execute_sql('SELECT * FROM Category WHERE rowid = ? ',[categoryID])
        categoryDescription= categories[0]['description']
        books = execute_sql('SELECT * FROM Book WHERE category_id = ? ',[categoryID])
        for book in books:
            print('dddd')
        print('debug')
        return render_template('books_in_cat.html', books=books, categoryDescription=categoryDescription)


    @app.route('/sql', methods={'GET','POST'})
    @roles_required('Admin')
    def sql():
        data=""
        if request.method == 'POST':
            sqlField = request.form['sqlField']
            try:
                returnVar = execute_sql(sqlField)
            except:
                data="An error occurred. . .look in the console"
            else:
                try:
                    for row in returnVar:
                        print('')
                        print(type(row))
                        rowAsDict = dict(row)
                        print(type(rowAsDict))
                        data = data + "\n"
                        for key, value in rowAsDict.items():
                            print(key, ":", value)
                            data= data + key + ":" + str(value) + "\n"
                except:
                     data="Data returned from sql was not iterable"
            return render_template('sql.html',data=data)

        return render_template('sql.html',data=data)

    @app.route('/tinker')
    def tinker():
        return '<h1>Tinker function executed, check console</h1>'

    @app.route('/tink')
    def tink():
         return render_template('tink.html')

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        return render_template('index.html')


    # The Admin page requires an 'Admin' role.
    @app.route('/admin')
    @roles_required('Admin')    # Use of @roles_required decorator
    def admin_page():
        return render_template('admin.html')


    @app.context_processor
    def example():
        return dict(myexample='This is an example')

    @app.context_processor
    def utility_processor():
        def format_price(amount, currency=u'€'):
            return u'{0:.2f}{1}'.format(amount, currency)
        return dict(format_price=format_price)

    return app


# Start development web server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=1000, debug=True)
