# Vault Thread Simulator

### Understanding the code
scraper.py goes through all the vault threads and saves the posts/authors to a sqlite db.
You don't need to run it, just use the included simulator.db file.

vaulthreadsimulator.py is the flask app. It's slow to start because it needs to preload all the modules so requests are fast.<br>
Basically it loops through all users generating a markov chain model for each user. When an http request comes in it picks 10 users at 
random and generates a paragraph for each.

The html template is basically a copy paste from the forum with a bunch of stuff stripped out.

### TODO
* Separate quotes. 
  - For best results we need to create a whole new "quote simulator" for each user. This means that each user will have a different pools of users to quote from with different words for users quoted.
* Add images to chain.
  - This doesn't need an "image simulator". Currently images are being striped out. We need to add them to the scraper and replace them with a placeholder text that includes the url.
* CTRL+F FIXME, fix it.

I most likely won't do any of the TODOs unless I get bored again :P
