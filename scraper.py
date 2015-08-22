import requests
from bs4 import BeautifulSoup
import models

threads = [27287, # 2.3
           29231, # 2.4
           30045, # 2.5
           31973, # 2.6
           33894, # 2.7
           35755, # 2.8
           36735, # 2.9
           38332, # 2.10
           39115, # 2.11
           39840, # 2.12
           ]

authorids = {}

db = models.session

def issignature(post):
    try:
        return post.contents[1] == '_________________'
    except:
        return False


def insertposts(threadid, page = 1):
    url = "http://www.awesomenauts.com/forum/viewtopic.php?f=6&t=" + str(threadid) + "&start=" + str((page - 1) * 10)
    print("Parsing: ", url)
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    posts, authors = [], []
    for post in soup.find_all('div', class_="postbody"):
        if not issignature(post):
            posts.append(post.get_text(separator=' '))

    for author in soup.find_all('b', class_="postauthor"):
        authors.append(author.text)

        if author.text not in authorids:
            a = models.User()
            a.username = author.text
            db.add(a)
            db.flush()
            authorids[author.text] = a.id

    for i in range(len(authors)):
        post = models.Post()
        post.user_id = authorids[authors[i]]
        post.thread_id = threadid
        post.number = (page * 10) + i + 1
        post.content = posts[i]

        db.add(post)
    db.commit()

    # returns false if there's no next page
    return soup.find('a', text="Next") is not None

for thread in threads:
    page = 1
    while insertposts(thread, page):
        page += 1