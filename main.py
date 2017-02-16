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
    """ Handles requests coming into '/'
        eg www.build-a-blog.com/
    """

    def get(self):
        t = jinja_env.get_template("base.html")
        content = t.render()
        self.response.write(content)

class AddPost(Handler):
    """ Handles requests coming into '/addpost'
        eg www.build-a-blog.com/addpost
    """

    def post(self):
        new_post_title = self.request.get("new-title")
        new_post_body = self.request.get("new-body")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_post_title) or (new_post_title.strip() == ""):
            error = "Your post must have a title."
            self.redirect("/?error=" + cgi.escape(error))

        # if the user typed nothing at all, redirect and yell at them
        if (not new_post_body) or (new_post_body.strip() == ""):
            error = "Your post must have a body."
            self.redirect("/?error=" + cgi.escape(error))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_post_title_escaped = cgi.escape(new_post_title, quote=True)
        new_post_body_escaped = cgi.escape(new_post_body, quote=True)

        # construct a blog post object for the new post
        blog_post = BlogPost(title = new_post_title_escaped, body = new_post_body_escaped)
        blog_post.put()

        # render the main blog page
        recent_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        t = jinja_env.get_template("blog.html")
        content = t.render(posts = recent_posts)
        self.response.write(content)

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
    ('/addpost', AddPost),
    ('/blog', ShowRecent)
], debug=True)
