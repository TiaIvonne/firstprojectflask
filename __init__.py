import os
import functools
 
#while data set on g is only available for the lifetime of this request.
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask_migrate import Migrate
#hash password, hide password, encrypted password
from werkzeug.security import generate_password_hash, check_password_hash

# declare an init file to start with flask
#import flask class

def create_app(test_config=None):
    app = Flask(__name__)
   #set configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from .models import db, User, Note

    db.init_app(app)
    migrate = Migrate(app, db)

    def require_login(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not g.user:
                return redirect(url_for('log_in'))
            return view(**kwargs)
        return wrapped_view
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.before_request
    def load_user():
        user_id = session.get('user_id')
        if user_id:
            g.user = User.query.get(user_id)
        else:
            g.user = None

    #declare routes
    @app.route('/sign_up', methods=('GET', 'POST'))
    def sign_up():
    #gives access to the request information to the server
        if request.method == 'POST':
            username=request.form['username']
            password=request.form['password']
            error = None
            
            if not username:
                error = 'Username is required'
            elif not password:
                error = 'Password is required'
            elif User.query.filter_by(username=username).first():
                error = 'Username is already taken'

            if error is None:
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash('Succesfully signed up!, Please log in', 'success')
                #url_for The same helper that we're using in the template files, allowing us to get the route for a given view function
                return redirect(url_for('log_in'))

            # flash allow a list of messages to display
            flash(error, 'error')
        return render_template('sign_up.html')
    
    @app.route('/log_in', methods=('GET', 'POST'))
    def log_in():
        if request.method == 'POST':
            username=request.form['username']
            password=request.form['password']
            error = None
        
            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password, password):
                error = 'Username or password are incorrect'

            #session section The session object is a dictionary that our Flask app store as a cookie in the user's browser.
            if error is None:
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for('index'))

            flash(error, category='error')

        return render_template('log_in.html')

    # we use DELETE request because we're "deleting" the session. 
    @app.route('/log_out', methods=('GET', 'DELETE'))
    def log_out():
        session.clear()
        #display a flash message to indicates your out of session
        flash('Succesfully logged out.', 'success')
        return redirect(url_for('log_in'))

    @app.route('/')
    def index():
        return 'Index'

    @app.route('/notes')
    @require_login
    def note_index():
        return render_template('note_index.html', notes=g.user.notes)

    @app.route('/notes/new', methods=('GET', 'POST'))
    @require_login
    def note_create():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                note = Note(author=g.user, title=title, body=body)
                db.session.add(note)
                db.session.commit()
                flash(f"Successfully created note: '{title}'", 'success')
                return redirect(url_for('note_index'))

            flash(error, 'error')

        return render_template('note_create.html')

    
    @app.route('/notes/<note_id>/edit', methods=('GET', 'POST','PATCH', 'PUT'))
    @require_login
    def note_update(note_id):
        note = Note.query.filter_by(user_id=g.user.id, id=note_id).first_or_404()
        if request.method in ['POST', 'PATCH', 'PUT']:
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                note.title = title
                note.body = body
                db.session.add(note)
                db.session.commit()
                flash(f"Successfully updated note: '{title}'", 'success')
                return redirect(url_for('note_index'))

            flash(error, 'error')
        
        return render_template('note_update.html', note=note)


    @app.route('/notes/<note_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    def note_delete(note_id):
        note = Note.query.filter_by(user_id=g.user.id, id=note_id).first_or_404()
        db.session.delete(note)
        db.session.commit()
        flash(f"Successfully deleted note: '{note.title}'", 'success')
        return redirect(url_for('note_index'))

    

#last line should be return app
    return app


