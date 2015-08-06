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

TOPICS_PER_HIT = 3
TOPIC_ID_FOR_PRACTICE = "10"


pp = pprint.PrettyPrinter(indent=4)

class TurkHIT(db.Model):
    result = db.TextProperty()
    userID = db.StringProperty()


class Report(db.Model):
    dump = db.TextProperty()

########################################################################################
########################################################################################
class TurkRefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        # file_topicJSON = open("dataset/nytimes-30-topics.json","r")
        # topicJSON = json.loads(file_topicJSON.read())
        # topic_ordered_tuples = sorted(topicJSON.items(), cmp=lambda x,y: cmp(int(x[0]), int(y[0])))
        
        # five_random_topics = random.sample(topic_ordered_tuples, 4)
        # random.shuffle(five_random_topics)

        # for tid, topic in five_random_topics:
        #     file_docJSON = open("dataset/nytimes-30-documents-"+tid+".json","r")
        #     topic['documents']=json.loads(file_docJSON.read())
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('turkrefine.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RetrieveThemeDataHandler(webapp2.RequestHandler):
    def get(self):
        file_topicJSON = open("dataset/nytimes-30-topics.json","r")
        topicJSON = json.loads(file_topicJSON.read())
        # SPARE THE FIRST TOPIC FOR PRACTICE
        tutorial_topic = topicJSON[TOPIC_ID_FOR_PRACTICE]
        tutorial_topic['tid']= TOPIC_ID_FOR_PRACTICE
        tutorial_topic['documents'] = json.loads(open("dataset/nytimes-30-documents-"+TOPIC_ID_FOR_PRACTICE+".json","r").read())
        del topicJSON[TOPIC_ID_FOR_PRACTICE]
        # PREPARE THREE TOPICS FOR TASKS
        keys = random.sample(topicJSON.keys(),TOPICS_PER_HIT)
        topics_for_task = {k:topicJSON[k] for k in keys}
        for tid, topic in topics_for_task.iteritems():
            file_docJSON = open("dataset/nytimes-30-documents-"+tid+".json","r")
            topic['tid'] = tid
            topic['documents']=json.loads(file_docJSON.read())
        self.response.out.write(json.dumps({
            "tutorial":tutorial_topic,
            "topics":topics_for_task
        }))

class SubmitTurkerResultHandler(webapp2.RequestHandler):
    def post(self):
        r = TurkHIT()
        r.result = self.request.get("result")
        r.userID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        r.put()
        self.response.out.write("Thank you for your participation. Your survey code is <b style='color:red;'>"+r.userID+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");


########################################################################################
########################################################################################

class RefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        file_topicJSON = open("dataset/nytimes-30-topics.json","r")
        topicJSON = json.loads(file_topicJSON.read())
        topic_ordered_tuples = sorted(topicJSON.items(), cmp=lambda x,y: cmp(int(x[0]), int(y[0])))
        # RENDER PAGE

        random.shuffle(topic_ordered_tuples)
        template_values = {'topics':topic_ordered_tuples}
        template = JINJA_ENVIRONMENT.get_template('refine.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RelatedDocumentsHandler(webapp2.RequestHandler):
    def get(self):
        topicIdx = str(int(self.request.get("topicIdx"))-1)
        file_docJSON = open("dataset/nytimes-30-documents-"+topicIdx+".json","r")
        self.response.out.write(file_docJSON.read())

class SubmitLogHandler(webapp2.RequestHandler):
     def post(self):
        r = Report()
        r.dump = self.request.get("data")
        r.put()
        self.response.out.write("Your log data is submitted. Thank you for your participation!")


########################################################################################
########################################################################################



app = webapp2.WSGIApplication([
    ('/', RefineHandler),
    ('/turkRefine', TurkRefineHandler),
    ('/submitTurkerResult', SubmitTurkerResultHandler),
    ('/retrieveThemeData', RetrieveThemeDataHandler),
    ('/refine', RefineHandler),
    ('/relatedDocuments', RelatedDocumentsHandler),
    ('/submitLog', SubmitLogHandler),
], debug=True)
