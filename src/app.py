#!/usr/bin/env python3

import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, send_from_directory
from database.database import *
from functools import wraps
from dotenv import dotenv_values

app = Flask(__name__)

SECRET_KEY = None
try:
    SECRET_KEY = dotenv_values(".env")["SECRET_KEY"]
except:
    pass

if SECRET_KEY is None:
    SECRET_KEY = os.urandom(32).hex()
    with open(".env", "a") as f:
        f.write(f"\nSECRET_KEY={SECRET_KEY}")

app.config['SECRET_KEY'] = SECRET_KEY

app.static_url_path = 'static'
app.static_folder = 'static'

db_init()
def auth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        id = session.get('id')

        if not id:
            return abort(401, 'Nejsi příhlášen!')
 
        return f(id, *args, **kwargs)

    return decorator



@app.errorhandler(404)
def page_not_found(e):
    user_id = session.get('id')
    data = []
    if user_id:
        data = db_get_user_by_id(user_id)

    error_data = {
        'status': 'Not found',
        'code': 404,
        'msg': f'Ups, stránka {request.url} nenalezena'
    }
    return render_template('error.html', error=error_data, data=data), 404

@app.errorhandler(401)
def Unauthorized(e):
    user_id = session.get('id')
    data = []
    if user_id:
        data = db_get_user_by_id(user_id)
    error_data = {
        'status': 'Unauthorized',
        'code': 401,
        'msg': f'Nemáš přístup ke stránce {request.url}'
    }
    return render_template('error.html', error=error_data, data=data), 401

@app.errorhandler(500)
def InternalServerError(e):
    user_id = session.get('id')
    data = []
    if user_id:
        data = db_get_user_by_id(user_id)
    error_data = {
        'status': 'Internal server error',
        'code': 500,
        'msg': f'Něco se pokazilo na stránce {request.url}'
    }
    return render_template('error.html', error=error_data, data=data), 500

@app.route('/', methods=('GET',))
def index():
    user_id = session.get('id')
    data = []
    if user_id:
        data = db_get_user_by_id(user_id)
    return render_template('index.html', data=data)

@app.route('/signup', methods=('GET',))
def signup():
    user_id = session.get('id')
    if user_id:
        return redirect(url_for('profile_edit'))
    return render_template('signup.html')

@app.route('/signup', methods=('POST',))
def signup_api():
    if not request.is_json:
        return jsonify('JSON is needed'), 400
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    description = data.get('description', '')

    id = db_register(username, password, description)
    if id:
        session['id'] = id
        return redirect(url_for('profile_edit'))
    else:
        return "Username already taken!", 409

@app.route('/login', methods=('GET',))
def login():
    user_id = session.get('id')
    if user_id:
        return redirect(url_for('profile_edit'))
    return render_template('login.html')

@app.route('/login', methods=('POST',))
def login_api():
    if not request.is_json:
        return jsonify('JSON is needed'), 400

    username = request.json['username']
    password = request.json['password']
    if db_login(username, password):
        session['id'] = db_get_user_id(username)
        #Make the session id cookie not httpOnly

        return redirect(url_for('profile_edit'))
    else:
        return "Wrong credentials", 401


@app.route('/logout', methods=('GET',))
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))

@app.route('/profile/note/new', methods=('POST',))
@auth_required
def note_new(id):
    title = request.form['title']
    content = request.form['content']
    note_id = db_new_note(id, title, content)
    # Return created HTTP code
    return f'Note created, has id {note_id}', 201



@app.route('/profile', methods=('GET',))
@auth_required
def profile_edit(id):
    return render_template('profile_edit.html', data=db_get_user_by_id(id))

@app.route('/profile/<int:id>', methods=('GET',))
def profile(id):
    user_data=db_get_user_by_id(id)
    if user_data is None:
        error_data = {
            'status': 'User not found',
            'code': 404,
            'msg': f'User with id {id} not found'
        }
        return render_template('error.html', error=error_data), 404
    return render_template('profile_public.html', data=user_data)

@app.route('/note/<int:id>', methods=('GET',))
def note_view(id):
    note_data=db_get_note_by_id(id)
    if note_data is None:
        error_data = {
            'status': 'Note not found',
            'code': 404,
            'msg': f'Note with id {id} not found'
        }
        return render_template('error.html', error=error_data), 404

    data = db_get_user_by_id(note_data['user_id'])
    data['note'] = note_data
    if note_data['user_id'] == 1 and session.get('id') != 1:
        error_data = {
            'status': 'Unauthorized',
            'code': 401,
            'msg': f'Nemáš přístup ke stránce {request.url}'
        }
        data = db_get_user_by_id(session.get('id'))
        return render_template('error.html', error=error_data, data=data), 401
    data['note']['user'] = db_get_user_by_id(note_data['user_id'])
    return render_template('note_view.html', data=data)

@app.route('/note/<int:note_id>', methods=('DELETE',))
@auth_required
def note_delete(id, note_id):
    if db_remove_note_by_id(note_id, id):
        return 'Note removed', 204
    else:
        return 'Nuh uh', 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/static/<path:path>', methods=('GET',))
def static_files(path):
    return app.send_static_file(path)

app.run(host='0.0.0.0', port=1337)