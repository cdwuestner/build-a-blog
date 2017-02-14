import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    body = db.StringProperty(required = True)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit from this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class Index(Handler):
    def get(self):
        self.response.write('Hello world!')

class ShowRecent(Handler):
    """ Handles requests coming in to /blog
        eg www.build-a-blog.com/blog
    """

    def get(self):
        """ Display the 5 most recent blog posts """

        # query for 5 most recent blog posts
        recent_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        t = jinja_env.get_template("blog.html")
        content = t.render(posts = recent_posts)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', ShowRecent)
], debug=True)
