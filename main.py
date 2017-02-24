import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class BlogTwo(db.Model):
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

    def render_blog(self, error="", title="", body=""):
        recent_posts = db.GqlQuery("SELECT * FROM BlogTwo ORDER BY created DESC LIMIT 5")

        title = self.request.get("new-title")
        body = self.request.get("new-body")

        t = jinja_env.get_template("blog.html")
        content = t.render(posts = recent_posts, error = error, title = title, body = body)
        self.response.write(content)

    def render_single_post(self, post):
        t = jinja_env.get_template("singlepost.html")
        content = t.render(post = post)
        self.response.write(content)

    def post(self):
        new_post_title = self.request.get("new-title")
        new_post_body = self.request.get("new-body")
        error = ""

        # if the user left empty field, redirect and yell at them
        if not new_post_title:
            self.render_blog(error = "Your post needs a title", body = new_post_body)
            return
        if not new_post_body:
            self.render_blog(error = "Your post needs a body", title = new_post_title)
            return

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_post_title_escaped = cgi.escape(new_post_title, quote=True)
        new_post_body_escaped = cgi.escape(new_post_body, quote=True)

        # construct a blog post object for the new post
        blog_post = BlogTwo(title = new_post_title_escaped, body = new_post_body_escaped)
        blog_post.put()

        new_post = str(blog_post.key().id())

        self.redirect("/blog/" + new_post)
        return

class ShowRecent(Handler):
    """ Handles requests coming in to /blog
        eg www.build-a-blog.com/blog
    """

    def get(self):
        """ Display the 5 most recent blog posts """

        error = self.request.get("error")

        # query for 5 most recent blog posts
        recent_posts = db.GqlQuery("SELECT * FROM BlogTwo ORDER BY created DESC LIMIT 5")

        t = jinja_env.get_template("blog.html")
        content = t.render(posts = recent_posts, error = error)
        self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):

    def get(self, id):
        post = BlogTwo.get_by_id(int(id))

        t = jinja_env.get_template("singlepost.html")
        content = t.render(post = post)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/addpost', AddPost),
    ('/blog', ShowRecent),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
