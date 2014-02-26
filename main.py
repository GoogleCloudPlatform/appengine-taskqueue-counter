import os

import jinja2
import webapp2

from google.appengine.api import taskqueue
from google.appengine.ext import ndb


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)

class CounterHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {'counters': Counter.query()}
        counter_template = JINJA_ENV.get_template('counter.html')
        self.response.out.write(counter_template.render(template_values))

    def post(self):
        key = self.request.get('key')

        # Add the task to the default queue.
        taskqueue.add(url='/worker', params={'key': key})

        self.redirect('/')

class CounterWorker(webapp2.RequestHandler):
    def post(self): # should run at most 1/s due to entity group limit
        key = self.request.get('key')
        @ndb.transactional
        def update_counter():
            counter = Counter.get_or_insert(key, count=0)
            counter.count += 1
            counter.put()
        update_counter()


APP = webapp2.WSGIApplication(
    [
        ('/', CounterHandler),
        ('/worker', CounterWorker)
    ], debug=True)
