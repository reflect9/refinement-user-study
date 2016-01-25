import re, json, os, logging, random, string, collections
import webapp2, jinja2
from google.appengine.ext import db
from google.appengine.api import mail, taskqueue
from datetime import datetime
import pprint
import csv, itertools, operator, copy
# import nltk.stem.snowball as snowball


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

TOPICS_PER_HIT = 3
TOPIC_ID_FOR_PRACTICE = "21"


TUTORIAL_INTRUDER = {'i':9999, "content":{"text":"  Iraqi forces backed by American helicopters and tanks battled hundreds of gunmen hiding in a date palm orchard near the southern city of Najaf on Sunday, exchanging fire for 15 hours in what appeared to be one of Iraq's deadliest battles in years, Iraqi officials said.  An American helicopter was shot down and 250 bodies were found where the clashes occurred near the village of Zarqaa, about 120 miles south of Baghdad, by a river and a large grain silo that is surrounded by orchards, the Iraqi officials said. ","title":"Iraqi Forces in Fierce Battle With Gunmen"},"file":"1822468.txt"}
TUTORIAL_TOPIC = {"words":  ["music", "venue[theater, hall]", "street", "dance", "band", "genre[jazz, opera, rock]", "songs", "ballet", "west", "album", "song", "performance", "musical", "play", "york", "hall", "orchestra", "concert"],"topic_index": 21}
NUM_TASKS_PER_HIT = 10


pp = pprint.PrettyPrinter(indent=4)

class TurkHIT(db.Model):
    result = db.TextProperty()
    userID = db.StringProperty()
    version = db.IntegerProperty()
    done = db.BooleanProperty()
    tid_list = db.StringProperty()   #  "5,2,12"
    updated = db.DateTimeProperty(auto_now=True)

class TurkEvaluationHIT(db.Model):
    refinedTopicID = db.StringProperty()    # 5 refinedTopicID in order "0-0,5-2,12-7,..."# 
    material = db.TextProperty()            # THIS INCLUDES FIVE IMPROVED TOPICS WITH ARTICLES AND INTRUDER 
    done = db.BooleanProperty()             # FALSE --> TRUE
    result = db.TextProperty()              # DUMPED RESULT (including log data, topic quality assessment, and picked document)
    userID = db.StringProperty()            # UNIQUE HIT ID (AMAZON verification code) 
    version = db.IntegerProperty()
    numArticles = db.IntegerProperty()
    isCorrect = db.StringProperty()
    updated = db.DateTimeProperty(auto_now=True)


class Report(db.Model):
    dump = db.TextProperty()

########################################################################################
########################################################################################
class TurkRefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        # file_topicJSON = open("dataset/nytimes-31-topics.json","r")
        # topicJSON = json.loads(file_topicJSON.read())
        # topic_ordered_tuples = sorted(topicJSON.items(), cmp=lambda x,y: cmp(int(x[0]), int(y[0])))
        
        # five_random_topics = random.sample(topic_ordered_tuples, 4)
        # random.shuffle(five_random_topics)

        # for tid, topic in five_random_topics:
        #     file_docJSON = open("dataset/nytimes-31-documents-"+tid+".json","r")
        #     topic['documents']=json.loads(file_docJSON.read())
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('turkrefine.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RetrieveThemeDataHandler(webapp2.RequestHandler):
    def get(self):
        ### DRAW TurkHIT which is not DONE yet
        hit = db.GqlQuery("SELECT * FROM TurkHIT WHERE done=False").get()
        if hit==None:
            message = 'No HIT is available. Contact the administrator: reflect9@gmail.com'
            raise endpoints.NotFoundException(message)
            return
        hit.done=True 
        hit.put()

        #### LOAD TOPIC FILES
        file_topicJSON = open("dataset/nytimes-31-topics.json","r")
        topicJSON = json.loads(file_topicJSON.read())
        # SPARE THE FIRST TOPIC FOR PRACTICE
        tutorial_topic = topicJSON[TOPIC_ID_FOR_PRACTICE]
        tutorial_topic['tid']= TOPIC_ID_FOR_PRACTICE
        tutorial_topic['documents'] = json.loads(open("dataset/nytimes-31-documents-"+TOPIC_ID_FOR_PRACTICE+".json","r").read())
        # PREPARE THREE TOPICS FOR TASKS
        tids = hit.tid_list.split(",")
        topics_for_task = []
        for tid in tids:
            topic = topicJSON[tid]
            topic['tid'] = tid
            ## READING DOCUMENTS
            file_docJSON = open("dataset/nytimes-31-documents-"+tid+".json","r")
            topic['documents']=json.loads(file_docJSON.read())
            topics_for_task.append(topic)
        self.response.out.write(json.dumps({
            "tutorial":tutorial_topic,
            "topics":topics_for_task,
            "taskID":hit.key().id(),
            "tid_list":hit.tid_list
        }))

class SubmitTurkerResultHandler(webapp2.RequestHandler):
    def post(self):
        taskID = self.request.get("taskID")
        tid_list = self.request.get("tid_list")
        logging.debug(str(taskID) + "   " + str(tid_list))
        if(taskID==None):
            logging.error("can't retrieve taskID")
            return
        r = TurkHIT.get_by_id(int(taskID))
        r.version=2
        r.result = self.request.get("result")
        r.userID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        r.done=True
        r.put()
        self.response.out.write("Thank you for your participation. Your survey code is <b style='color:red;'>"+r.userID+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");

class ReportTurkerResultHandler(webapp2.RequestHandler):
    def get(self):
        all_data = TurkHIT.all().run(limit=1000)
        for d_raw in all_data:
            d = json.loads(d_raw)
            print d
        
class GenerateTurkerTaskHandler(webapp2.RequestHandler):
    def get(self):
        ##### GENERATE THREE RANDOM TOPIC NUMBERS
        tid_set = range(0,31)
        tid_set.remove(int(TOPIC_ID_FOR_PRACTICE))
        random.shuffle(tid_set)
        all_tid = []
        for i in range(0, len(tid_set), 3):
            a = str(tid_set[i])
            b = str(tid_set[i+1])
            c = str(tid_set[i+2])
            tid_list = a+","+b+","+c
            print tid_list
            all_tid.append(tid_list)
            tid_list = b+","+c+","+a
            print tid_list
            all_tid.append(tid_list)
            tid_list = c+","+a+","+b
            print tid_list
            all_tid.append(tid_list)   
        all_tid = all_tid*3
        ##### LET'S CREATE TurkHIT
        for tid in all_tid:
            r = TurkHIT()
            r.version = 1
            r.done = False
            r.tid_list = tid
            r.put()

class RefreshTurkerTaskHandler(webapp2.RequestHandler):
    def get(self):
        ##### RE-ENABLE TASKS WHOSE DONE==TRUE BUT RESULT==None
        HITS = TurkHIT.all().filter("done =",True).filter("result =",None).run(limit=1000)
        enabled = []
        for HIT in HITS:
            enabled.append(HIT.tid_list)
            HIT.done=False
            HIT.put()
        logging.info("RE-ENABLED TASKS: " + ", ".join(enabled))

        # HITS = TurkHIT.all().filter("done =",None).filter("result !=",None).run(limit=1000)
        # disabled = []
        # for HIT in HITS:
        #     disabled.append(HIT.tid_list)
        #     HIT.done=True
        #     HIT.put()
        # logging.info("DISABLED TASKS: " + ", ".join(disabled))

        self.response.out.write("renabling done for " + ", ".join(enabled))

########################################################################################
########################################################################################
class TurkEvaluationHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('turkevaluation.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RetrieveEvaluationDataHandler(webapp2.RequestHandler):
    def get(self):
        ### DRAW TurkHIT which is not DONE yet
        numArticles = self.request.get("numArticles")
        if numArticles=='5':
            hit = db.GqlQuery("SELECT * FROM TurkEvaluationHIT WHERE done=False AND numArticles=5").get()
        elif numArticles=='8':
            hit = db.GqlQuery("SELECT * FROM TurkEvaluationHIT WHERE done=False AND numArticles=8").get()
        else:
            hit = db.GqlQuery("SELECT * FROM TurkEvaluationHIT WHERE done=False").get()
        if hit==None:
            message = 'No HIT is available. Contact the administrator: reflect9@gmail.com'
            raise endpoints.NotFoundException(message)
            return
        hit.done=True 
        hit.put()
        
        # PREPARE TUTORIAL TOPIC
        tutorial_topic = TUTORIAL_TOPIC
        tutorial_topic['articles'] = json.loads(open("dataset/nytimes-31-documents-"+TOPIC_ID_FOR_PRACTICE+".json","r").read())[:hit.numArticles-1]
        tutorial_topic['intruder'] = TUTORIAL_INTRUDER
        tutorial_topic['tid'] = TOPIC_ID_FOR_PRACTICE
        tutorial_topic['isTutorial'] = True;
        ###
        self.response.out.write(json.dumps({
            "tutorial":tutorial_topic,
            "material":hit.material,
            "taskID":hit.key().id(),
            "refinedTopicID":hit.refinedTopicID
        }))

class SubmitTurkEvaluationHandler(webapp2.RequestHandler):
    def post(self):
        result = self.request.get("result")
        taskID = self.request.get("taskID")
        refinedTopicID = self.request.get("refinedTopicID")
        logging.debug(str(taskID) + " : " + str(refinedTopicID))
        if(taskID==None):
            logging.error("can't retrieve taskID")
            return
        r = TurkEvaluationHIT.get_by_id(int(taskID))
        r.result = self.request.get("result")
        r.userID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        r.done=True
        # CHECKING CORRECTNESS OF THE RESULT
        correctness = []
        result = json.loads(r.result)
        for i, topic_result in enumerate(result["topics"]):
            file_name_chosen_as_unrelated = topic_result["unrelated_article"]
            material = json.loads(r.material)
            # print material
            # print material[i]
            # print material[i]["intruder"]
            # print material[i]["intruder"]["file"]
            correct_answer = material[i]["intruder"]["file"]
            if file_name_chosen_as_unrelated==correct_answer:
                correctness.append("T")
            else: 
                correctness.append("F")
        r.isCorrect = ",".join(correctness) 
        r.put()
        self.response.out.write("Thank you for your participation. Your survey code is <b style='color:red;'>"+r.userID+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");

class GenerateEvaluationTaskHandler(webapp2.RequestHandler):
    def get(self):
        tid_range = range(0,31)
        tid_range.remove(int(TOPIC_ID_FOR_PRACTICE))
        option = self.request.get("option")
        # RESET TurkEvaluationHIT
        if option=="reset":
            q = db.GqlQuery("SELECT * FROM TurkEvaluationHIT")
            while True:
                results = q.fetch(1000)
                if len(results)< 1000:
                    db.delete(results)
                    break;
                else:
                    db.delete(results)
            return
        # CLEAN HITS WITH DONE=True but empty data to DONE=False
        if option=="refresh": 
            HITS = TurkEvaluationHIT.all().filter("done =",True).filter("isCorrect =",None).run(limit=1000)
            enabled = []
            for HIT in HITS:
                enabled.append("["+HIT.refinedTopicID+"]")
                HIT.done=False
                HIT.put()
            logging.info("RE-ENABLED TASKS: " + ", ".join(enabled))
            self.response.out.write("renabling done for " + ", ".join(enabled))
            return
        ##### GENERATE TASKS
        if option=="generate":
            numArticles = 5
            all_refinements = []
            topic_ids_for_HITS = [tid_range[i:i+NUM_TASKS_PER_HIT] for i in range(0,len(tid_range),NUM_TASKS_PER_HIT)]
            ###  THE FOLLOWING LINES DECIDE HOW TO MIX ORIGINAL AND IMPROVED TOPICS
            # ref_list = range(9)+["original"] #0~8: improved topics, 999: original topic
            rid_buckets = {}
            for tid in tid_range:  # FOR EACH TOPIC ID, GENERATE 0-8 and 9 original topics
                rb_temp = range(9) + ["original"]   # 10 refinements ID
                random.shuffle(rb_temp) # SHUFFLE WHEN TO SHOW ORIGINAL
                rid_buckets[tid] = rb_temp 
            # print rid_buckets
            for tid_list in topic_ids_for_HITS: # 0-9, 10-19, 20-30 without 21 
                for repetition in range(10):  # Each topic will be evaluated 18 times 
                    tid_rid_list = []
                    for tid in tid_list:
                        # print tid
                        # print [len(rid_list) for tid, rid_list in rid_buckets.iteritems() ]
                        # print rid_buckets[tid]
                        tid_rid_list.append(str(tid)+"-"+str(rid_buckets[tid].pop()))
                        random.shuffle(tid_rid_list)  # SHUFFLE ORDER OF SHOWING
                    all_refinements.append(",".join(tid_rid_list))
            ##### LET'S CREATE TurkHIT
            all_improved_themes = json.loads(open("dataset/improved_themes.json","r").read())
            all_original_themes = json.loads(open("dataset/nytimes-31-topics.json","r").read())
            for trid_list in all_refinements:
                ### GENERATE TASK MATERIAL
                material = []
                for tid_rid in trid_list.split(","):
                    tid = tid_rid.split("-")[0]
                    rid = tid_rid.split("-")[1]
                    material_single_topic = {}
                    material_single_topic['tid']=tid
                    material_single_topic['rid']=rid
                    material_single_topic['intruder'] = random.sample(all_improved_themes[tid]["intruders"],1)[0]
                    if rid=="original":
                        material_single_topic['theme'] = [w['word'] for w in all_original_themes[str(tid)]["words"]][:20]
                        booleans_valid_articles = [True for i in range(20)]
                    else:
                        material_single_topic['theme'] = all_improved_themes[tid]["themes"][int(rid)]["improved_theme"]
                        booleans_valid_articles = all_improved_themes[tid]["themes"][int(rid)]["improved_articles"]
                    ### PICK SEVEN ARTICLES
                    doc_json = json.loads(open("dataset/nytimes-31-documents-"+tid+".json","r").read())
                    valid_articles = [doc_json[i] for i,b in enumerate(booleans_valid_articles) if b==True]
                    material_single_topic['articles'] = random.sample(valid_articles,numArticles-1)
                    ### 
                    material.append(material_single_topic)
                ###
                HIT = TurkEvaluationHIT()
                HIT.version = 1
                HIT.done = False
                HIT.refinedTopicID = trid_list
                HIT.material = json.dumps(material)
                HIT.numArticles = numArticles
                HIT.put()

            # all_refinements = []
            # for i in range(0, len(tid_set), NUM_TASKS_PER_HIT):  # THREE CASES: 0, 10, 20
            #     for refID in range(9):  # WHICH REF WILL BE USED AMONG 10 REFINEMENTS PER TOPIC
            #         tid_list = [str(tid_set[i+d])+"-"+str(refID) for d in range(NUM_TASKS_PER_HIT)]
            #         for offset in range(0,NUM_TASKS_PER_HIT):  # TO CANCEL THE ORDERING EFFECT, WE ROTATE BY OFFSET
            #             tid_list_rotated = tid_list[offset:] + tid_list[:offset]
            #             all_refinements.append(",".join(tid_list_rotated))
            # ##### LET'S CREATE TurkHIT
            # all_improved_themes = json.loads(open("dataset/improved_themes.json","r").read())
            # for ref_id in all_refinements:
            #     ### GENERATE TASK MATERIAL
            #     material_five = []
            #     for tid_rid in ref_id.split(","):
            #         tid = tid_rid.split("-")[0]
            #         rid = tid_rid.split("-")[1]
            #         material_single_topic = {}
            #         material_single_topic['tid']=tid
            #         material_single_topic['rid']=rid
            #         material_single_topic['intruder'] = random.sample(all_improved_themes[tid]["intruders"],1)[0]
            #         material_single_topic['improved_theme'] = all_improved_themes[tid]["themes"][int(rid)]
            #         ### PICK SEVEN ARTICLES
            #         doc_json = json.loads(open("dataset/nytimes-31-documents-"+tid+".json","r").read())
            #         booleans_valid_articles = all_improved_themes[tid]["themes"][int(rid)]["improved_articles"]
            #         valid_articles = [doc_json[i] for i,b in enumerate(booleans_valid_articles) if b==True]
            #         material_single_topic['articles'] = random.sample(valid_articles,7)
            #         ### 
            #         material_five.append(material_single_topic)
            #     ###
            #     HIT = TurkEvaluationHIT()
            #     HIT.version = 1
            #     HIT.done = False
            #     HIT.refinedTopicID = ref_id
            #     HIT.material = json.dumps(material_five)
            #     HIT.put()

########################################################################################
########################################################################################

class RefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        file_topicJSON = open("dataset/nytimes-20-topics.json","r")
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
        file_docJSON = open("dataset/nytimes-20-documents-"+topicIdx+".json","r")
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
    ('/reportTurkerResult', ReportTurkerResultHandler),
    ('/generateTurkerTask', GenerateTurkerTaskHandler),
    ('/refreshTurkerTask', RefreshTurkerTaskHandler),
    #########
    ('/turkEvaluation', TurkEvaluationHandler),
    ('/retrieveEvaluationData', RetrieveEvaluationDataHandler),
    ('/submitTurkEvaluation', SubmitTurkEvaluationHandler),
    ('/generateEvaluationTask', GenerateEvaluationTaskHandler),
    #########
    ('/refine', RefineHandler),
    ('/relatedDocuments', RelatedDocumentsHandler),
    ('/submitLog', SubmitLogHandler),
], debug=True)
