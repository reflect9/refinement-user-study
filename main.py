import re, json, os, logging, random, string 
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

# class TopicEvaluation(db.Model):
#     nickname = db.StringProperty()
#     answers = db.TextProperty()

# class TaskCounter(db.Model):
#     counter = db.IntegerProperty()

# class Answer(db.Model):
#     usercode = db.StringProperty()
#     topicIdx = db.IntegerProperty()
#     mode = db.StringProperty()
#     wordNum = db.IntegerProperty()
#     randomImage_idx = db.IntegerProperty()
#     version = db.IntegerProperty()
#     short = db.StringProperty()
#     long = db.StringProperty()
#     conf = db.IntegerProperty()
#     duration = db.IntegerProperty()
#     created = db.DateTimeProperty(auto_now_add=True)

# class LabelingHit(db.Model):
#     usercode = db.StringProperty()
#     mode = db.StringProperty()
#     randomImage_idx = db.IntegerProperty()
#     wordNum = db.IntegerProperty()
#     answers = db.TextProperty()
#     timestamp = db.TextProperty()
#     version = db.IntegerProperty()
#     created = db.Da

# class Description(db.Model):
#     usercode = db.StringProperty()
#     topicIdx = db.IntegerProperty()
#     mode = db.StringProperty()
#     wordNum = db.IntegerProperty()
#     randomImage_idx = db.IntegerProperty()
#     shortOrLong = db.StringProperty()
#     conf = db.IntegerProperty()
#     duration = db.IntegerProperty()
#     # now important things
#     label = db.StringProperty()
#     descNumber = db.IntegerProperty()
#     # numberOfEvaluation = db.IntegerProperty()

# class Evaluation(db.Model):
#     topicIdx = db.IntegerProperty()
#     wordNum = db.IntegerProperty()
#     best = db.StringListProperty()
#     worst = db.StringListProperty()
#     players = db.StringListProperty()
#     shortOrLong = db.StringProperty()
#     duration = db.FloatProperty()
#     done = db.BooleanProperty()
#     created = db.DateTimeProperty(auto_now_add=True)
#     updated = db.DateTimeProperty()
#     usercode = db.StringProperty()
#     memo = db.StringProperty()
#     iter_num = db.IntegerProperty()

# class Document(db.Model):
#     topicIdx = db.IntegerProperty()
#     docID = db.StringProperty()
#     probability = db.FloatProperty()
#     title = db.StringProperty()
#     fulltext = db.TextProperty()


# class LazyTurker(db.Model):
#     validation_code = db.StringProperty()
#     evalResults = db.TextProperty()

########################################################################################
########################################################################################
########################################################################################
########################################################################################

class RefineHandler(webapp2.RequestHandler):
    def get(self):
        # PREPARE TOPIC AND DOCUMENTS
        file_topicJSON = open("dataset/nyt-50-topics.json","r")
        topicJSON = json.loads(file_topicJSON.read())
        
        # RENDER PAGE
        template_values = {'topics':topicJSON['topics']}
        template = JINJA_ENVIRONMENT.get_template('refine.html')
        html = template.render(template_values)
        self.response.out.write(html)

class RelatedDocumentsHandler(webapp2.RequestHandler):
    def get(self):
        file_docJSON = open("dataset/nyt-topic-to-document-handpicked-cleaned.json","r")
        docJSON = json.loads(file_docJSON.read())
        topicIdx = str(int(self.request.get("topicIdx"))-1)
        relatedDocument = json.dumps(docJSON[topicIdx])
        self.response.out.write(relatedDocument)

class SubmitReportHandler(webapp2.RequestHandler):
     def post(self):
        r = Report()
        r.dump = self.request.get("dump")
        r.put()
        self.response.out.write("The refinements are submitted. Thank you for your participation!")


# class SubmitHandler(webapp2.RequestHandler):
#     def post(self):
#         #item = self.request.get("item")
#         #nextURL = "task"
#         result = LabelingHit()
#         result.mode = self.request.get('mode')
#         result.randomImage_idx = int(self.request.get('randomImage_idx'))
#         result.wordNum = int(self.request.get('wordNum'))
#         result.usercode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
#         result.answers = self.request.get('answers')
#         result.timestamp = self.request.get('timestamp')
#         result.version = VERSION
#         result.put()

#         answers = json.loads(result.answers)
#         # create answers
#         for ans in answers[1:]:
#             a = Answer()
#             a.usercode = result.usercode
#             a.topicIdx = int(ans['topicIndex'])
#             a.mode = result.mode
#             a.wordNum = result.wordNum
#             a.randomImage_idx = result.randomImage_idx
#             a.version = result.version
#             a.short = ans['short'] 
#             a.long = ans['long'] 
#             a.conf = int(ans['conf']) 
#             a.duration = int(ans['duration']) 
#             a.put()

#         # counter up the configuration
#         for ans in answers[1:]:
#             config = str(ans['topicIndex'])+"_"+result.mode+"_"+str(result.wordNum)
#             tc = TaskCounter.get_or_insert(key_name=config, counter=0)
#             tc.counter += 1
#             tc.put()

#         self.response.out.write("<div class='endMessage'>Thank you for your participation. Your survey code is <b style='color:red;'>"+result.usercode+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");
        
# class TaskHandler(webapp2.RequestHandler):
#     def get(self):
#         # self.response.out.write("All tasks are done.")
#         # return
#         trials = 0
#         while True:
#             mode = random.choice(modes)
#             wordNum = random.choice(wordNums)
#             availableTopics = {}
#             completedTopics = []
#             for i in range(len(topicJSON['topics'])):
#                 config = str(i)+"_"+mode+"_"+str(wordNum)
#                 matchingCounter = TaskCounter.get_by_key_name(config)
#                 if matchingCounter==None:
#                     availableTopics[i]= 0
#                 elif matchingCounter.counter<TASK_LIMIT_PER_SETTING:
#                     availableTopics[i]= matchingCounter.counter
#                 else:
#                     completedTopics.append(i)
#             # now check whether the setting has enough available topics
#             if len(availableTopics.keys())<1:
#                 trials+=1
#                 if trials>100:
#                     print "ALL TASKS DONE"
#                 continue
#             elif len(availableTopics.keys())==1:
#                 logging.debug(availableTopics)
#                 sample_idx = availableTopics.keys()
#                 sample_idx.insert(0, completedTopics[0])
#                 sample_idx.insert(0, completedTopics[1])
#                 sample_idx.insert(0, completedTopics[2])
#                 sample_idx.insert(0, completedTopics[3])
#                 logging.debug(mode + "," + str(wordNum) + " is almost done. Only one topic need more data.")
#                 logging.debug(sample_idx)
#                 break
#             elif len(availableTopics.keys())==2:
#                 logging.debug(availableTopics)
#                 sample_idx = availableTopics.keys()
#                 sample_idx.insert(0, completedTopics[0])
#                 sample_idx.insert(0, completedTopics[1])
#                 sample_idx.insert(0, completedTopics[2])
#                 logging.debug(mode + "," + str(wordNum) + " is almost done. Only two topics need more data.")
#                 logging.debug(sample_idx)
#                 break
#             elif len(availableTopics.keys())==3:
#                 logging.debug(availableTopics)
#                 sample_idx = availableTopics.keys()
#                 sample_idx.insert(0, completedTopics[0])
#                 sample_idx.insert(0, completedTopics[1])
#                 logging.debug(mode + "," + str(wordNum) + " is almost done. Only three topics need more data.")
#                 logging.debug(sample_idx)
#                 break
#             elif len(availableTopics.keys())==4:
#                 logging.debug(availableTopics)
#                 sample_idx = availableTopics.keys()
#                 sample_idx.insert(0, completedTopics[0])
#                 logging.debug(mode + "," + str(wordNum) + " is almost done.")
#                 logging.debug(sample_idx)
#                 break
#             else:
#                 sortedTopics_tuple = sorted(availableTopics.items(), key=operator.itemgetter(1))
#                 logging.debug(sortedTopics_tuple)
#                 sample_idx = []                
#                 for t in sortedTopics_tuple[:5]:
#                     sample_idx.append(t[0])
#                 # sample_idx = random.sample(availableTopics,5)        
#                 logging.debug(sample_idx)
#                 break;
#         randomImage_idx = random.choice([1,2,3,4,5]) 
#         topics = {}
#         for idx in sample_idx:

#             topics[str(idx)]=topicJSON['topics'][idx]
#         # topicsJSON = json.dumps(topics)
#         # for topic in topics:
#         #     freq_all = map(lambda x: x['second'], topic['terms'])
#         #     topic['freq_max']= max(freq_all)
#         #     for term in topic['terms']:
#         #         term['freq_normalized'] = term['second']/topic['freq_max']
#         template_values = {'topics':topics, 'mode':mode, 'wordNum':wordNum, 'randomImage_idx':randomImage_idx}
#         template = JINJA_ENVIRONMENT.get_template('task.html')
#         html = template.render(template_values)
#         self.response.out.write(html)

# class UpdateCounter(webapp2.RequestHandler):
#     def get(self):
#         # delete all taskcounter records
#         q = db.GqlQuery("SELECT * FROM TaskCounter")
#         results = q.fetch(1000)
#         db.delete(results)
#         # update new
#         counter = {}
#         for ti in range(0,50):
#             for mode in modes:
#                 for wordNum in wordNums:
#                     counter[str(ti)+"_"+mode+"_"+str(wordNum)]=0
#         logging.debug(counter)
#         query = db.GqlQuery("SELECT * FROM Answer")
#         for r in query.run():
#             config = str(r.topicIdx)+"_"+r.mode+"_"+str(r.wordNum)
#             counter[config] += 1
#         logging.debug(counter)
#         for conf, count in counter.iteritems():
#             tc = TaskCounter.get_or_insert(key_name=conf, counter=0)
#             tc.counter = count
#             tc.put()
#         self.response.out.write(json.dumps(counter))
            


# class ReportHandler(webapp2.RequestHandler):
#     def get(self):
#         file_topicJSON_old = open("dataset/nyt-50-topics-without stopiwords.json","r")
#         topicJSON_old = json.loads(file_topicJSON_old.read())

#         report_mode = self.request.get('mode', default_value='topic') # mode can be either 'hit','topic','configuration'
#         if report_mode == 'topic':
#             topicIndex = self.request.get('topicIndex', default_value=0)
#             # for the selected topic, compare answers across different visualizations
#             query = db.GqlQuery("SELECT * FROM Answer WHERE topicIdx=%s" % str(topicIndex))           
#             answers = {}
#             for wn in wordNums:
#                 answers[wn]={}
#                 for mode in modes: 
#                     answers[wn][mode]=[]
#             for a in query.run():
#                 answers[a.wordNum][a.mode].append(a)
#             template_values = {answers:answers, wordNums:wordNums, modes:modes, topicIndex:topicIndex, 'topicWords':topicJSON['topics'], 'topicWordsOld':topicJSON_old['topics']}
#             template = JINJA_ENVIRONMENT.get_template('report_by_topic.html')
#             html = template.render(template_values)
#             self.response.out.write(html)
#         if report_mode == 'hit':
#             query = db.GqlQuery("SELECT * FROM LabelingHit WHERE version>3")
#             hits = []
#             for r in query.run():
#                 r.ansList = json.loads(r.answers)
#                 #r.timeList = map(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"), json.loads(r.timestamp))
#                 hits.append(r)
#             template_values = {'hits':hits, 'topicWords':topicJSON['topics'], 'topicWordsOld':topicJSON_old['topics']}
#             template = JINJA_ENVIRONMENT.get_template('report.html')
#             html = template.render(template_values)
#             self.response.out.write(html)
#         if report_mode == 'sanityCheck':
#             query = db.GqlQuery("SELECT * FROM Answer WHERE created>DATETIME('"+CREATED_AFTER_VERSION_4+"')")
#             num_answers = query.count()
#             output = "Number of Answers: "+str(num_answers)+"<br>"
#             self.response.out.write(output)
#             usercode_answers = set()
#             for r in query.run():
#                 usercode_answers.add(r.usercode)

#             query = db.GqlQuery("SELECT * FROM LabelingHit WHERE created>DATETIME('"+CREATED_AFTER_VERSION_4+"')")
#             num_hits = query.count()
#             output = "Number of Hits: "+str(num_hits)+"<br>"
#             self.response.out.write(output)
#             usercode_hits = set()
#             for r in query.run():
#                 usercode_hits.add(r.usercode)

#             for uc in usercode_answers:
#                 if uc not in usercode_hits:
#                     self.response.out.write("answer["+uc+"] is not in hits")
#                 else:
#                     self.response.out.write(uc+"<br>")

#             for uc in usercode_hits:
#                 if uc not in usercode_answers:
#                     self.response.out.write("hit["+uc+"] is not in answers")
#                 else:
#                     self.response.out.write(uc+"<br>")



#         # elif report_mode == 'topic':
#         #     query = db.GqlQuery("SELECT * FROM LabelingHit")
#         #     summaries = []
#         #     # organize answers by topicIndex
#         #     for r in query.run():
#         #         r.ansList = json.loads(r.answers) 
#         #         for ans in r.ansList:
#         #             summaries.append({'topicIndex':ans.topicIndex, 
#         #                 'mode':r.mode, 
#         #                 'wordNum':r.wordNum,
#         #                 'short':ans.short,
#         #                 'long':ans.long,
#         #                 'conf':ans.conf,
#         #                 'duration':ans.duration'
#         #             })
#         #     #         if ans.topicIndex not in summaryByConfig: 
#         #     #             summaryByConfig[ans.topicIndex]= { 
#         #     #                 'word list':{'5':[], '10':[], '20':[]},
#         #     #                 'histogram':{'5':[], '10':[], '20':[]},
#         #     #                 'wordcloud':{'5':[], '10':[], '20':[]},
#         #     #                 'topic-in-a-box':{'5':[], '10':[], '20':[]},
#         #     #             }
#         #     #         summaryByConfig[r.mode][r.wordNum].append(ans)
#         #     # # now calculate summaries of each topic
#         #     # for topicIdx, topic in summaryByConfig.iteritems():
#         #     #     for visCode, visAnswers in topic.iteritems():
#         #     #         for wordNum, answers in visAnswers.iteritems():
#         #     #             totalDuration=0
#         #     #             for answer in answers[1:]: # ignore the first one which is sample
#         #     #                 totalDuration += answer.duration
#         #     #             avgDuration = totalDuration/(len(answers)-1)
#         #     #             visAnswers['']
#         #     durations = {}
#         #     for mCode in modes:
#         #         ansForMode = [i for i in summaries if i.mode == mCode]
#         #         durations[mCode] = sum(i.duration for i in ansForMode) / len(ansForMode)




#         # elif report_mode == 'configuration':
#         #     pass



        

# class AllTasksHandler(webapp2.RequestHandler):
#     def get(self):
#         # show all tasks in one page
#         topics = topicJSON['topics']
#         for topic in topics:
#             freq_all = map(lambda x: x['second'], topic['terms'])
#             topic['freq_max']= max(freq_all)
#             for term in topic['terms']:
#                 term['freq_normalized'] = term['second']/topic['freq_max']
#         # print topics[0]
#         template_values = {'topics':topics}
#         template = JINJA_ENVIRONMENT.get_template('alltasks.html')
#         html = template.render(template_values)
#         self.response.out.write(html)

# class AllDescriptionsHandler(webapp2.RequestHandler):
#     def get(self):   
#         file_evaluation_dict = open("dataset/evaluation_dict.json","r")
#         evaluation_dict = json.loads(file_evaluation_dict.read())
#         topicIdx = self.request.get("topicIdx")
#         topicIdx = 0 if topicIdx=="" else int(topicIdx)
#         documents = db.GqlQuery("SELECT * FROM Document WHERE topicIdx="+str(topicIdx)+" ORDER BY probability DESC").fetch(10)
#         desc_result =db.GqlQuery("SELECT * FROM Description WHERE topicIdx="+ str(topicIdx)).fetch(1000)
#         desc_dict = {}
#         for wordNum in wordNums:
#             desc_dict[wordNum]={}
#             for shortOrLong in ['short','long']:
#                 desc_dict[wordNum][shortOrLong]={}
#                 for mode in modes:
#                     desc_dict[wordNum][shortOrLong][mode]=[]
#         for desc in desc_result:
#             desc_dict[desc.wordNum][desc.shortOrLong][desc.mode].append(desc)
#         topic_terms = [t['first'] for t in topicJSON['topics'][topicIdx]['terms']]
#         template_values = {'algorithm_label':algorithm_labels[topicIdx][0], 'topic_terms':topic_terms, 'topicIdx':topicIdx, 'descriptions':desc_dict, 'documents':documents, 'modes':modes, 'wordNums':wordNums, 'evaluation_dict':evaluation_dict}
#         template = JINJA_ENVIRONMENT.get_template('alldescriptions.html')
#         html = template.render(template_values)
#         self.response.out.write(html)


# class InitializeEvaluateHandler(webapp2.RequestHandler):
#     def get(self):
#         req = self.request.get("req")
#         if req=="document":
#             # RESET Documents
#             q = db.GqlQuery("SELECT * FROM Document")
#             while True:
#                 results = q.fetch(1000)
#                 if len(results)< 1000:
#                     db.delete(results)
#                     break;
#                 else:
#                     db.delete(results)
#             file_docJSON = open("dataset/nyt-topic-to-document-handpicked-cleaned.json","r")
#             docJSON = json.loads(file_docJSON.read())
#             for ti, docList in docJSON.iteritems():
#                 for doc in docList:
#                     newDoc = Document()
#                     newDoc.topicIdx = int(ti)
#                     newDoc.docID = doc['id']
#                     newDoc.probability = doc['prob'] 
#                     newDoc.title = doc['title']
#                     newDoc.fulltext = doc['fulltext']
#                     newDoc.put()

#             # RESET EvaluationCounter
#             # q = db.GqlQuery("SELECT * FROM EvaluationCounter")
#             # results = q.fetch(1000)
#             # db.delete(results)
#             # for topicIdx in range(50):
#             #     for wordNum in wordNums:
#             #         EC = EvaluationCounter(topicIdx=topicIdx, wordNum=wordNum, counter=0)
#             #         EC.put()

#         if req=="description_reset":
#             # RESET Description
#             q = db.GqlQuery("SELECT * FROM Description")
#             while True:
#                 results = q.fetch(1000)
#                 if len(results)< 1000:
#                     db.delete(results)
#                     break;
#                 else:
#                     db.delete(results)

#         if req=="description":
#             file_descJSON = open("dataset/Descriptions.json","r")
#             descJSON = json.loads(file_descJSON.read())
#             # for ti, t in descJSON.iteritems():
#             tir = int(self.request.get("ti"))
#             for ti in range(tir,tir+5): 
#                 t = descJSON[str(ti)]
#                 for wN, modeSet in t.iteritems():
#                     # print modeSet
#                     for mode, dlist in modeSet.iteritems():
#                         for i, desc in enumerate(dlist):
#                             # CREATE SHORT DESCRIPTION
#                             key_name = str(ti)+"-"+str(wN)+"-"+mode+"-"+str(i)+"-short"
#                             newDesc = Description(key_name=key_name)
#                             newDesc.usercode = desc['usercode']
#                             newDesc.topicIdx = int(desc['topicIdx'])
#                             newDesc.mode = desc['mode']
#                             newDesc.wordNum = int(desc['wordNum'])
#                             newDesc.randomImage_idx = int(desc['randomImage_idx'])
#                             newDesc.shortOrLong = "short"
#                             newDesc.conf =  int(desc['conf'])
#                             newDesc.duration = int(desc['duration'])
#                             newDesc.label = desc['short']
#                             newDesc.descNumber = i
#                             # newDesc.numberOfEvaluation = 0
#                             newDesc.put()

#                             # CREATE LONG DESCRIPTION
#                             key_name = str(ti)+"-"+str(wN)+"-"+mode+"-"+str(i)+"-long"
#                             newDesc = Description(key_name=key_name)
#                             newDesc.usercode = desc['usercode']
#                             newDesc.topicIdx = int(desc['topicIdx'])
#                             newDesc.mode = desc['mode']
#                             newDesc.wordNum = int(desc['wordNum'])
#                             newDesc.randomImage_idx = int(desc['randomImage_idx'])
#                             newDesc.shortOrLong = "long"
#                             newDesc.conf =  int(desc['conf'])
#                             newDesc.duration = int(desc['duration'])
#                             newDesc.label = desc['long']
#                             newDesc.descNumber = i
#                             # newDesc.numberOfEvaluation = 0
#                             newDesc.put()
        
#         if req=="evaluation_reset":
#             # RESET Evaluation
#             # RESET Evaluation
#             q = db.GqlQuery("SELECT * FROM Evaluation")
#             while True:
#                 results = q.fetch(1000)
#                 if len(results)< 1000:
#                     db.delete(results)
#                     break;
#                 else:
#                     db.delete(results)
#         if req=="evaluation":
#             # POPULATE Evaluation
#             # 50 topic * 3 wordNum * 5 labels * 2 [short or long]  = 1500 tasks
#             # 1500 / 5 tasks per HIT = 300 HIT for one iteration
#             # 300 * $0.5 = $150 total
#             tir = int(self.request.get("ti"))
#             for topicIdx in range(tir,tir+10): 
#                 for wordNum in wordNums:
#                     for descNumber in range(5):
#                         for shortOrLong in ['short','long']:
#                             newEval = Evaluation()
#                             newEval.topicIdx = topicIdx
#                             newEval.wordNum = wordNum
#                             newEval.shortOrLong = shortOrLong
#                             newEval.done = False 
#                             players = []
#                             offset_per_mode = 1 # when adding players, use different descNumbers with this offset 
#                             for mi, mode in enumerate(modes):
#                                 key_name = str(topicIdx)+"-"+str(wordNum)+"-"+mode+"-"+str((descNumber+(mi*offset_per_mode))%5)+"-"+shortOrLong
#                                 players.append(key_name)
#                             newEval.players = players
#                             newEval.iter_num=2
#                             newEval.put()

# class SingleEvaluationHandler(webapp2.RequestHandler):
#     def get(self):
#         key = self.request.get("key")
#         ev = Evaluation.get_by_id(int(key)) 
#         ev.descriptions = [Description.get_by_key_name(player) for player in ev.players]
#         template_values = {'ev':ev, 'algorithm':algorithm_labels[ev.topicIdx][0]}
#         template = JINJA_ENVIRONMENT.get_template('showSingleEvaluation.html')
#         html = template.render(template_values)
#         self.response.out.write(html)

# class SubmitSingleEvaluationHandler(webapp2.RequestHandler):
#     def post(self):
#         logging.debug(self.request.get("result"))
#         result = json.loads(self.request.get("result"))
#         validation_code = "singlesubmission"
#         # FIND AND MODIFY EVALUATION DATAOBJECT
#         logging.debug(result)
#         eval_object = Evaluation.get_by_id(int(result['eID']))
#         eval_object.best = result['best'].split(",")
#         eval_object.worst = result['worst'].split(",")
#         eval_object.done = True
#         eval_object.updated = datetime.now()
#         eval_object.usercode = validation_code
#         eval_object.put()
#         self.response.out.write("submitted");


# class EvaluateHandler(webapp2.RequestHandler):
#     def get(self):
#         logging.debug("REMAINING EVALS: "+ str(db.GqlQuery("SELECT * FROM Evaluation WHERE done=False").count()))
#         # DRAW FIVE EVALUATIONS
#         count=0
#         avail_topic_idx = {}
#         eval_samples = db.GqlQuery("SELECT * FROM Evaluation WHERE done=False").fetch(100)
#         for es in eval_samples:
#             avail_topic_idx[int(es.topicIdx)] = 1
#         logging.info("Available Evalutions' topicidx: "+str(avail_topic_idx.keys()))
#         # GET 5 EVALUATIONS OF DICTINCT TOPICS
#         while True:
#             evaluations = []
#             random_ti = random.sample(avail_topic_idx.keys(),5)
#             while True:
#                 shortOrLong_list =[random.choice(["short","long"]) for i in range(5)]
#                 if "short" in shortOrLong_list: break
#             for ti in random_ti:
#                 shortOrLong = shortOrLong_list.pop()
#                 q = db.GqlQuery("SELECT * FROM Evaluation WHERE done=False AND shortOrLong='%s' AND topicIdx=%d" % (shortOrLong,ti)) 
#                 ev = q.get()
#                 if ev!=None:
#                     evaluations.append(ev)

#             # CHECK WHETHER WE FOUND 5 EVALUATIONS (OF DISTINCT TOPICS) THAT HAVE AT LEAST 1 SHORT         
#             if len(evaluations)==5:
#                 logging.debug([ev.topicIdx for ev in evaluations])
#                 logging.debug("GOT 5 EVALUATIONS WITH DISCINCT TOPICS")
#                 break
#             else:
#                 count += 1
#                 if count==100:
#                     logging.error("EXCEED 10 trial limit when getting 5 distinct evaluations")
#                     return
#                 else:
#                     logging.debug([ev.topicIdx for ev in evaluations])
#                     # logging.debug("PICKED "+ str(len(ev_dict.keys())) + " EVALAUTIONS. TRYING AGAIN.")
#                     continue
#         # NOW PREPARE DESCRIPTIONS FOR EACH EVALUATION TASK
#         bad_label_used = False
#         for evaluation in evaluations:
#             evaluation.documents = db.GqlQuery("SELECT * FROM Document WHERE topicIdx=%d ORDER BY probability DESC" % evaluation.topicIdx).fetch(10)
#             evaluation.descriptions = [Description.get_by_key_name(player) for player in evaluation.players]
#             desc_dict = {}
#             for desc in evaluation.descriptions:
#                 cleanedLabel = re.sub(r"\W+",r"",desc.label.lower())
#                 # cleanedLabel = [stemmer.stem(label) for label in desc.label.lower().split('[ ,.]+')].join(" ")
#                 if cleanedLabel not in desc_dict:
#                     desc_dict[cleanedLabel] = []
#                 desc_dict[cleanedLabel].append(desc)
#             # FOR SHORT, ADD ALGORITHM GENERATED DESCRIPTION 
#             if evaluation.shortOrLong=="short":
#                 # ADD BAD LABEL FOR THE FIRST SHORT TASK
#                 if bad_label_used==False:
#                     bad_label_used=True
#                     bad_label = random.choice(bad_labels)
#                     bad_desc = {
#                         'usercode': "bad",
#                         'bad_label_idx': bad_labels.index(bad_label),
#                         'topic': evaluation.topicIdx,
#                         'label': bad_label,
#                         'cleaned_label': re.sub(r"\W+",r"",bad_label.lower())  
#                     }
#                     if bad_desc['cleaned_label'] not in desc_dict: desc_dict[bad_desc['cleaned_label']]=[] 
#                     desc_dict[bad_desc['cleaned_label']].append(bad_desc)
#                     # ALSO MARK THE EVALUATION AS DUMMY EVAL
#                     evaluation.memo = "dummy"
#                 else:  # ADD ALGO LABEL FOR THE REST Of SHORT TASKS
#                     algo_desc = {
#                         'usercode': "algorithm",
#                         'topic': evaluation.topicIdx,
#                         'label': algorithm_labels[evaluation.topicIdx][0],
#                         'cleaned_label': re.sub(r"\W+",r"",algorithm_labels[evaluation.topicIdx][0].lower())  
#                     }
#                     if algo_desc['cleaned_label'] not in desc_dict: desc_dict[algo_desc['cleaned_label']]=[] 
#                     desc_dict[algo_desc['cleaned_label']].append(algo_desc)
#             logging.debug("TOPIC:%d, WORDNUM:%d, SHORTORLONG:%s" % (evaluation.topicIdx, evaluation.wordNum, evaluation.shortOrLong))

#             # for cl, dlist in desc_dict.iteritems():
#                 # for d in dlist:
#                     # print isinstance(d, Description)
#                     # if isinstance(d, Description):
#                     #     print d.label + ", " + d.usercode
#                     # else:
#                     #     print d['label'] + ", " + d['usercode']
#             # pp.pprint(desc_dict)
#             # print [[(desc[label, desc.usercode) for desc in desc_l] for cleaned_label, desc_l in desc_dict.iteritems()]
#             # END ADDING ALGORITHM GENERATED DESC
#             evaluation.desc_dict = desc_dict.items()
#             random.shuffle(evaluation.desc_dict)

#         # if len(documents)!=10:
#         #     raise RuntimeError(str(len(documents))+" documents found for topic "+ str(topicIdx))

#         template_values = {'evaluations':evaluations}
#         template = JINJA_ENVIRONMENT.get_template('evaluation.html')
#         html = template.render(template_values)
#         self.response.out.write(html)

     

# class EvaluationSubmitHandler(webapp2.RequestHandler):
#     def post(self):
#         logging.debug(self.request.get("evalResults"))
#         evalResults = json.loads(self.request.get("evalResults"))
#         validation_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
#         # CHECK WHETHER THE TURKER IDENTIFIED BAD LABELS AS WORST
#         def check(x):  return "bad" in str(x['worst']) 
#         if any(map(check, evalResults))==False:
#             logging.error("THe turker ("+validation_code+") did not identify the bad label.")
#             lt = LazyTurker()
#             lt.validation_code = validation_code
#             lt.evalResults = self.request.get("evalResults")
#             lt.put()
#             self.response.out.write("<div class='endMessage'>Thank you for your participation. Your survey code is <b style='color:red;'>"+validation_code+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");
#             return
#         # FIND AND MODIFY EVALUATION DATAOBJECT
#         for evaluation in evalResults:
#             logging.debug(evaluation)
#             if 'memo' in evaluation:
#                 if evaluation['memo']=="dummy": 
#                     logging.error("SKIPPING DUMMY TASK")
#                     continue
#             eval_object = Evaluation.get_by_id(int(evaluation['eID']))
#             eval_object.best = evaluation['best']
#             eval_object.worst = evaluation['worst']
#             eval_object.duration = evaluation['duration']
#             eval_object.done = True
#             eval_object.updated = datetime.now()
#             eval_object.usercode = validation_code
#             eval_object.put()
#         self.response.out.write("<div class='endMessage'>Thank you for your participation. Your survey code is <b style='color:red;'>"+validation_code+"</b><br> Do not forget to copy and paste the code in the Amazon Mechanical Turk page.</div>");
        
# class ReportEvaluationHandler(webapp2.RequestHandler):
#     def get(self):
#         for topicIdx in range(50):
#             q = db.GqlQuery("SELECT * FROM Evaluation WHERE done=True AND topicIdx=%d" % topicIdx) 
#             evaluations = q.fetch(1000)
#             winners = []
#             for ev in evaluations:
#                 for winner in ev.winners:
#                     winner_desc = db.Description.get_by_key_name(winner)
#                     winners.append(winner_desc)
            
# class ResetEvaluationHandler(webapp2.RequestHandler):
#     def get(self):
#         keys_to_reset = self.request.get("keys").split("_")
#         for k in keys_to_reset:
#             ev = Evaluation.get_by_id(int(k))
#             ev.best = []
#             ev.worst = []
#             ev.duration = None
#             ev.done = False 
#             ev.updated = None
#             ev.usercode = None
#             ev.put()
#         self.response.out.write(str(len(keys_to_reset)) + " evaluations were resetted.")



# class TempFixHandler(webapp2.RequestHandler):
#     def get(self):
#         q = db.GqlQuery("SELECT * FROM Answer WHERE topicIdx=0 AND mode='topic-in-a-box'")
#         results = q.fetch(100)
#         db.delete(results)


    # usercode = db.StringProperty()
    # mode = db.StringProperty()
    # answers = db.TextProperty()

    # timestamp = db.TextProperty()
# class SubmitAllTasksHandler(webapp2.RequestHandler):
#     def get(self):
#         eval = TopicEvaluation()
#         eval.nickname = self.request.get('nickname')
#         eval.answers = self.request.get("answers")
#         eval.put()
#         self.response.out.write("<p>Thanks! Your evaluation is submitted.</p>");


# class SendReminderHandler(webapp2.RequestHandler):
#     def get(self):
#         _id = int(self.request.get("id"))
#         todo = Log.get_by_id(_id)
#         if todo is not None and todo.completed is False:
#             html = "You have a uncompleted Log : "+todo.txt+" ["+str(_id)+"] "+str(todo.due_date)
#             msg = mail.EmailMessage()
#             msg.sender = owner_email
#             msg.subject = "Log: " + todo.txt
#             msg.to = owner_email
#             msg.html = html
#             msg.send()


app = webapp2.WSGIApplication([
    ('/', RefineHandler),
    ('/refine', RefineHandler),
    ('/relatedDocuments', RelatedDocumentsHandler),
    ('/submitReport', SubmitReportHandler)
], debug=True)
