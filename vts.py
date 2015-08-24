import markovify
import random
import models
import requests
import re
from bs4 import BeautifulSoup


class Simulator(object):
    """
    Simalutor class to generate random paragraphs from vault threads.
    Example usage:
        simulator = Simulator()

        simulator.inserthreads()
        print(simulator.getparagraph()

    You don't need to call the insert threads method every time. Just once to insert post data into the db.
    """
    # Vault thread ids.
    threads = [27287,  # 2.3
               29231,  # 2.4
               30045,  # 2.5
               31973,  # 2.6
               33894,  # 2.7
               35755,  # 2.8
               36735,  # 2.9
               38332,  # 2.10
               39115,  # 2.11
               39840,  # 2.12
               ]

    quote_ph = "QQQ::"
    html_quoteauthor = "<div class=\"quotetitle\">{}</div>"
    html_quotetext = "<div class=\"quotecontent\">{}</div>"

    def __init__(self, db):
        self.db = db.session
        self.authorids = {}  # used by the insertposts class method
        self.fetchusers()

    def fetchusers(self):
        self.users = self.db.query(models.User).all()

    def insertthreads(self):
        """
        Will loop through all the threads in the class variable and insert each page until it runs out of pages
        """
        for thread in self.threads:
            page = 1
            while self.insertposts(thread, page):
                page += 1
        self.fetchusers()

    def insertposts(self, threadid, page=1):
        """
        Will insert posts from a thread page into the database. It will also insert new authors that it finds.
        Returns True if it's not the last page in the thread.
        """

        # let's start by generating the url from the threadid and page
        start_position = (page - 1) * 10  # post start position for the url
        url = "http://www.awesomenauts.com/forum/viewtopic.php?f=6&t={}&start={}".format(threadid, start_position)
        print("Parsing: ", url)

        # now let's fetch the url and create a soup object from it so we can navigate the html code
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

        # helper function we're going to use in the next loop, the postbody html class can contain the post or the signature
        def issignature(post):
            try:
                return post.contents[1] == '_________________'
            except IndexError:
                return False

        posts, authors = [], []  # will contain posts and users, used to generate the post proper

        # This will loop all posts and signatures, we only care about posts
        for post in soup.find_all('div', class_="postbody"):
            if not issignature(post):
                posts.append(post)

        # Loops authors for each post
        for author in soup.find_all('b', class_="postauthor"):
            authors.append(author.text)

            # insert authors into the db, no duplicates :P
            if author.text not in self.authorids:
                a = models.User()
                a.username = author.text
                self.db.add(a)
                self.db.flush()
                self.authorids[author.text] = a.id

        nr_posts = len(posts)
        for i in range(nr_posts):
            post = models.Post()
            post.user_id = self.authorids[authors[i]]
            post.thread_id = threadid
            post.number = (page * 10) + i + 1
            content = self.parsequote(posts[i])
            post.content = content
            self.db.add(post)
        self.db.commit()

        # check if last page
        return soup.find('a', text="Next") is not None

    def parsequote(self, post):
        """
        Parses and inserts quotes on a post for a specific user.
        """
        quoteauthors = post.find_all('div', class_="quotetitle")
        quotecontent = post.find_all('div', class_="quotecontent")

        nr_quotes = len(quotecontent)
        for i in range(nr_quotes):
            authortext = quoteauthors[i].text
            if authortext.endswith("wrote:"):
                authortext = authortext[:-6]
            else:
                authortext = 'GenericQuote'

            if authortext not in self.authorids:
                a = models.User()
                a.username = authortext
                self.db.add(a)
                self.db.flush()
                self.authorids[authortext] = a.id

            quotetext = models.Post()
            quotetext.user_id = self.authorids[authortext]
            content = quotecontent[i].get_text(separator=' ')
            quotetext.content = content
            self.db.add(quotetext)

            ph_text = self.quote_ph + str(self.authorids[authortext])
            quoteauthors[i].replace_with(ph_text)
            quotecontent[i].replace_with('')

        return post.get_text(separator=' ')

    def generatechain(self, user):
        """
        Will generate a markov chain for the user.
        """

        if user.chain is not None:
            return

        posts = self.db.query(models.Post) \
            .filter(models.Post.user_id == user.id).all()

        userposts = [post.content or '' for post in posts]
        text = " ".join(userposts)
        try:
            user.chain = markovify.Text(text)
        except IndexError:
            # TODO We should validate input, maybe in the list comprehension filter above?
            print("FIXME: validate input {}".format(user.username).encode("UTF-8"))
            user.chain = markovify.Text("")

    def getparagraph(self, userid=0):
        """
        Will generate a paragraph from a user. If userid is zero will grab a user at random.
        Make sure userid exists otherwise you'll get an exception.
        Returns a tuple (username, paragraph)
        """

        randomuser = userid == 0

        if randomuser:
            user = random.choice(self.users)
        else:
            user = [user for user in self.users if user.id == int(userid)][0]

        self.generatechain(user)
        paragraphtext = user.chain.make_sentence(tries=100)

        # Since the make_sentece might fail and return None this loop will ensure we get a paragraph
        while paragraphtext is None:
            if randomuser:
                user = random.choice(self.users)
                self.generatechain(user)
                paragraphtext = user.chain.make_sentence(tries=100)
            else:
                paragraphtext = 'Zork.'
        return user.username, self.insertquoteparagraph(paragraphtext)

    def getparagraphlist(self, amount = 1, userid = 0):
        """
        return a list of paragraphs
        """
        posts = []
        for _ in range(amount):
            post = self.getparagraph(userid=userid)
            posts.append(post)
        return posts

    def insertquoteparagraph(self, paragraphtext):
        """
        Replaces quotes inside the paragraph with quote html.
        """

        def quote_replacer(matchobj):
            quote_paragraph = self.getparagraph(matchobj.group(1))
            quoteauthorhtml = self.html_quoteauthor.format(quote_paragraph[0])
            quotecontenthtml = self.html_quotetext.format(quote_paragraph[1])
            return quoteauthorhtml + quotecontenthtml

        r = r"{}([0-9]*)".format(self.quote_ph)
        paragraphtext = re.sub(r, quote_replacer, paragraphtext)
        return paragraphtext
