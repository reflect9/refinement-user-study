import re, json, os, logging, random, string, collections
import webapp2, jinja2
from google.appengine.ext import db
from google.appengine.api import mail, taskqueue
from datetime import datetime
import pprint
import csv, itertools, operator
# import nltk.stem.snowball as snowball


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

TASK_LIMIT_PER_SETTING = 5

pp = pprint.PrettyPrinter(indent=4)

class Report(db.Model):
    dump = db.TextProperty()

########################################################################################
########################################################################################
########################################################################################
########################################################################################

class RefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        file_topicJSON = open("dataset/nytimes-20-topics.json","r")
        topicJSON = json.loads(file_topicJSON.read())
        topic_ordered_tuples = collections.OrderedDict(sorted(topicJSON.items(), cmp=lambda x,y: cmp(int(x[0]), int(y[0]))))
        # RENDER PAGE

        template_values = {'topics':topic_ordered_tuples}
        template = JINJA_ENVIRONMENT.get_template('refine.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RelatedDocumentsHandler(webapp2.RequestHandler):
    def get(self):
        topicIdx = str(int(self.request.get("topicIdx"))-1)
        file_docJSON = open("dataset/nytimes-20-documents-"+topicIdx+".json","r")
        self.response.out.write(file_docJSON.read())

class SubmitReportHandler(webapp2.RequestHandler):
     def post(self):
        r = Report()
        r.dump = self.request.get("dump")
        r.put()
        self.response.out.write("The refinements are submitted. Thank you for your participation!")



app = webapp2.WSGIApplication([
    ('/', RefineHandler),
    ('/refine', RefineHandler),
    ('/relatedDocuments', RelatedDocumentsHandler),
    ('/submitReport', SubmitReportHandler)
], debug=True)
