from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/historic')
def historic():
    return render_template('historic.html')

@app.route('/notifs')
def notifs():
    return render_template('notifs.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/user')
def user():
    return render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True)
