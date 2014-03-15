#  blog-challenge.py
#  
#  Copyright 2012 erpreciso <erpreciso@erpreciso-laptop>
#  
# PROVA A SCRIVERE L'__INIT__ 
# http://en.wikibooks.org/wiki/Python_Programming/Object-oriented_programming#Special_Class_Methods

import os
import webapp2
import jinja2
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True)

def blog_key(bkey = 'default'):
	return db.Key.from_path("Entries", bkey)

class Entries(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	#blog_id = db.IntegerProperty()
	
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def render_main_page(self):
		all_entries = db.GqlQuery("select * from Entries order by created desc limit 10")
		self.render("main_page.html", all_entries = all_entries)

	def get(self):
		self.render_main_page()

class Plink(Handler):
	def render_plink(self, plink_id = "", subject = "", content = ""):
		self.render("plink_page.html",plink_id = plink_id, subject = subject, content = content)
	
	def get(self, product_id):
		
		#e = db.GqlQuery("select * from Entries where ancestor is :1", blog_key(int(product_id)))
		#for t in e:
		#	self.render_plink(plink_id = t.blog_id, subject = t.subject, content = t.content)
		
		key = db.Key.from_path("Entries", int(product_id), parent = blog_key())
		t = db.get(key)
		self.render_plink(plink_id = t.key(), subject = t.subject, content = t.content)
		
class NewPost(Handler):
	def render_new_post(self, message = "", subject = "", content = ""):
		self.render("new_post.html", message = message, subject = subject, content = content)

	def get(self):
		message = "Fill text above with what you prefer"
		self.render_new_post(message)
	
	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		#blog_id = int(time.time())
		if subject and content:
			e = Entries(parent = blog_key(), subject = subject, content = content)
			e.put()
			#message = "success - created ID " + str(blog_id)
			#self.render_new_post(message, subject = "", content = "")
			self.redirect('/blog/%s' % str(e.key().id()))
		else:
			message = "subject and content, please"
			self.render_new_post(message, subject, content)
			
			
		
app = webapp2.WSGIApplication([('/blog', MainPage),
								('/blog/newpost', NewPost),
								('/blog/(\d+)', Plink)], debug = True)
