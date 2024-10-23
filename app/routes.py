from flask import Blueprint, render_template, session, redirect, url_for, request, abort


main = Blueprint('main', __name__)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'psd':  # Remplacez par votre logique
            session['username'] = username
            return redirect(url_for('main.home'))

        return 'Identifiants incorrects', 401  # Message d'erreur en cas d'échec

    if request.method == 'GET':
        if 'username' in session:
            return render_template('search.html')
        return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main.route('/register')
def register():
    return render_template('register.html')

@main.route('/')
def home():
    if 'username' in session:
        return render_template('search.html')
    return redirect(url_for('main.login'))

@main.route('/historic')
def historic():
    if 'username' in session:
        return render_template('historic.html')
    return redirect(url_for('main.login'))

@main.route('/notifs')
def notifs():
    if 'username' in session:
        return render_template('notifs.html')
    return redirect(url_for('main.login'))

@main.route('/chat')
def chat():
    if 'username' in session:
        return render_template('chat.html')
    return redirect(url_for('main.login'))


@main.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('main.login'))

@main.route('/user')
def user():
    if 'username' in session:
        return render_template('user.html')
    return redirect(url_for('main.login'))

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404