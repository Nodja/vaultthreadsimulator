from flask import Flask, render_template
import markovify
import random
import re

app = Flask(__name__)

global utextmodels

@app.route('/')
def simulator():
    posts = []
    for r in random.sample(range(100), 10):
        utextmodels[r].text = utextmodels[r].model.make_sentence(tries=100)
        if utextmodels[r].text == None:
            utextmodels[r].text = 'Zork'
        posts.append(utextmodels[r])

    return render_template('index.html', posts=posts)


class UsersModels(object):
    def __init__(self, username, model = None):
        self.username = username
        self.model = model

def preloadtexts():
    import models
    session = models.session
    users = session.query(models.User).all()
    posts = session.query(models.Post).all()

    models_ = []
    for user in users:
        u = UsersModels(user.username)
        text = " ".join(post.content for post in posts if post.user_id == user.id)
        try:
            u.model = markovify.Text(text)
            models_.append(u)
        except IndexError:
            print("FIXME: validate input ", u.username )


    return models_


if __name__ == '__main__':
    global utextmodels
    utextmodels = preloadtexts()
    app.run(host="0.0.0.0", port=8010)