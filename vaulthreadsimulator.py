import models
from flask import Flask, render_template
from vts import Simulator


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simulator.db'
models.db.init_app(app)

with app.app_context():
    models.db.create_all()
    simulator = Simulator(models.db)

@app.route('/')
def index():
    posts = simulator.getparagraphlist(amount=10)
    return render_template('index.html', posts=posts)

@app.route('/<name>')
def user(name):
    posts = []
    user = [user for user in simulator.users if user.username == name]
    if len(user) > 0 :
        userid = user[0].id
        posts = simulator.getparagraphlist(amount=10, userid=userid)
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8010)