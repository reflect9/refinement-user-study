import numpy as np
from numpy import arange,array,ones,linalg
import scipy.stats as stats
import scipy.special as special
import matplotlib.pyplot as plt
from matplotlib import cm
import pprint as pp
import json, math, re, csv, itertools, operator
import nltk.stem.snowball as snowball
from sets import Set
from bs4 import BeautifulSoup
import random, os
from os import path

tid_list = range(0,31)
tid_list.remove(21)
tools = ["add_words", "remove_words","merge_words", "change_word_order","remove_articles", "split_theme"]
def shorten_event(eventFullname):
	return EVENTS[eventFullname]
def rand_jitter(arr,strength=0.03,direction='both',delta=0):
    stdev = strength*(max(arr)-min(arr))
    if direction=="both":
    	return arr + (np.random.randn(len(arr)) * stdev + delta)
    if direction=="plus":
    	# print "plus",stdev
    	return arr + (np.absolute(stdev * np.random.randn(len(arr))) + delta)
    if direction=="minus":
    	# print "minus",stdev
    	# print arr + (stdev * np.random.randn(len(arr)) - stdev)
    	return arr + ((np.absolute(stdev * np.random.randn(len(arr))) * -1) + delta)
def arr_join(arr):
	return list(itertools.chain(*arr))
def log_odds(evals):
	sum = 0
	for ev in evals:
		sum += np.log(ev['intruder_file_prob']) - np.log(ev['picked_file_prob'])
	DLO = sum / float(len(evals))
	return DLO
def accuracy(evals):
	return float(len([ev for ev in evals if ev['correctness']==True])) / len(evals)


def tokenize_corpus():
	## READ ALL CORPUS DOCUMENTS AND SAVE TOKENIZED WORDS (WITHOUT DUPLICATES) 
	directory_to_corpus = "dataset/txt"
	documents={}
	for filename in os.listdir(os.getcwd()+"/"+directory_to_corpus):
		with open(directory_to_corpus+"/"+filename, mode='r') as infile:
			text = infile.read()
			tokens = re.split(r'[^a-z]+',text)
			tokens.remove("")
			# print text
			# print tokens
			documents[filename] = list(set(tokens))
			# print documents
	with open('dataset/document_tokens.json','w') as fp:
		json.dump(documents, fp, sort_keys=True, indent=4)



def co_document_frequency(v1, v2, dict_tokenized_documents):
	freq_co_occurence=0
	freq_v2_occurence=0
	# print v1, v2
	w1 = v1.lower().split(" ")
	w2 = v2.lower().split(" ")
	for fn, tokens in dict_tokenized_documents.iteritems():
		#### USING REGEX AND RAW TEXT
		# reg1 = re.compile(r"(^|[^a-z])"+v1.lower()+"($|[^a-z])",re.IGNORECASE)
		# reg2 = re.compile(r"(^|[^a-z])"+v2.lower()+"($|[^a-z])",re.IGNORECASE)
		# if re.search(reg2, txt)!=None:
		# 	freq_v2_occurence+=1
		# 	if re.search(reg1, txt)!=None:
		# 		freq_co_occurence+=1
		#### USING TOKENS
		if any(i in tokens for i in w2):
			freq_v2_occurence+=1
			if any(i in tokens for i in w1):
				freq_co_occurence+=1
				# print tokens
	# print (freq_co_occurence,freq_v2_occurence)
	# print "TOTAL : "+str(count)
	return (freq_co_occurence,freq_v2_occurence)

def topic_coherence(topic_words,dict_tokenized_documents):
	## USING MIMNO's algorithm (http://dirichlet.net/pdf/mimno11optimizing.pdf)
	print topic_words
	total_coherence = 0
	for i in range(1,len(topic_words)):
		for j in range(0,i):
			# print i,j
			# print topic_words[i],topic_words[j]
			# continue
			(D_co, D_j) = co_document_frequency(topic_words[i],topic_words[j],dict_tokenized_documents)
			# print D_co, D_j 
			if D_j==0: continue
			word_pair_coherence = np.log(float(D_co+1)/float(D_j)) 
			total_coherence+=word_pair_coherence
			# print word_pair_coherence
	print total_coherence
	# exit()
 	return total_coherence

with open('dataset/document_tokens.json','r') as fp:
	dict_tokenized_documents = json.loads(fp.read())

tid_range = range(0,31)
TOPIC_ID_FOR_PRACTICE = "21"
tid_range.remove(int(TOPIC_ID_FOR_PRACTICE))
rid_range = range(0,9)





 
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##### FINDING BEST TURKERS' ID
##########################################################################
# directory_path = 'dataset/batch_result_for_reward'
# files = [x for x in os.listdir(directory_path) if path.isfile(directory_path+os.sep+x)]
# best_code = ['CT213KI2', 'P2ZX3GWH', 'N9H1BRYG']
# turker_info = []
# for fn in files:
# 	with open(directory_path+"/"+fn, mode='r') as infile:
# 	    reader = csv.DictReader(infile)
# 	    turker_info += [row for row in reader]
# # print turker_info
# pp.pprint([ti for ti in turker_info if ti['Answer.surveycode'] in best_code])
# exit()

##########################################################################
##### # of PARTICIPANTS FOR THE REFINEMENT STUDY
##########################################################################
directory_path = 'dataset/batch_result_for_reward'
files = [x for x in os.listdir(directory_path) if path.isfile(directory_path+os.sep+x)]
num_turkers = 0
for fn in files:
	with open(directory_path+"/"+fn, mode='r') as infile:
	    reader = csv.DictReader(infile)
	    for row in reader:
	    	num_turkers += 1
print num_turkers
# pp.pprint([ti for ti in turker_info if ti['Answer.surveycode'] in best_code])
exit()



##########################################################################
##########################################################################
##########################################################################
##########################################################################



#### PREPROCESSING DATA: UNPACK HITS INTO TOPICS AND REFINED INSTANCES OF TOPICS  

ORIGINAL_TOPICS = json.loads(open("dataset/nytimes-31-topics.json","r").read())


csv.field_size_limit(2147483647)
with open('dataset/backup_real_3/TurkEvaluationHIT.csv', mode='r') as infile:
    reader = csv.DictReader(infile)
    EVAL_HITS = [row for row in reader]
    for ev_hit in EVAL_HITS:
    	ev_hit.update({"material":json.loads(ev_hit['material'])})
    	ev_hit.update({"result":json.loads(ev_hit['result'])})
EVALUATIONS = {str(tid):{} for tid in tid_range}
for EH in EVAL_HITS:
	material = EH['material']
	result = EH['result']
	for mi, mat in enumerate(material):
		tid = mat['tid']
		rid = mat['rid']
		single_eval = {}
		single_eval['tid'] = tid
		single_eval['rid'] = rid
		single_eval['isOriginal'] = True if single_eval['rid']=="original" else False
		single_eval['position'] = mi
		single_eval['material'] = mat
		single_eval['result'] = result["topics"][mi]
		single_eval['picked_file'] = single_eval['result']["unrelated_article"] 
		single_eval['intruder_file'] = mat["intruder"]["file"]
		single_eval['intruder_file_prob'] = mat["intruder"]["other_topics"][tid] 
		if single_eval['picked_file'] == single_eval['intruder_file']:
			single_eval['correctness'] = True
			single_eval['picked_file_prob'] = single_eval['intruder_file_prob']
		else:
			single_eval['correctness'] = False
			for article in mat["articles"]:
				if article["file"]==single_eval['picked_file']:
					single_eval['picked_file_prob'] = article["weight"]		
					break
			if single_eval['picked_file_prob']==None:
				print "couldn't find picked file in the material", single_eval['picked_file_prob'], single_mat
				exit()
		if rid not in EVALUATIONS[tid].keys(): EVALUATIONS[tid][rid]=[]
		# print np.log(single_eval['intruder_file_prob']) - np.log(single_eval['picked_file_prob'])
		EVALUATIONS[tid][rid].append(single_eval)
with open('dataset/backup_real_1/TurkHIT.csv', mode='r') as infile:
    reader = csv.DictReader(infile)
    results = [rows for rows in reader if rows['result']!=""]
TURK_HITS = [{'userID':r["userID"], 'data':json.loads(r['result'])} for r in results]
TOPICS = {str(tid):{} for tid in tid_range}
current_topic_nums = {str(tid):0 for tid in tid_range}
for HIT in TURK_HITS:
	printThis = False
	log = HIT["data"]["topics"][2]["log"]
	idx_improvement_begin = [i for i,v in enumerate(log) if v["message"]=="theme_improvements"]
	idx_improvement_end = [i for i,v in enumerate(log) if v["message"]=="questionnaire"]
	for i, topic in enumerate(HIT["data"]["topics"]):
		tid = topic["tid"]
		rid = current_topic_nums[str(tid)]
		userID = HIT["userID"]
		log_data = log[idx_improvement_begin[i]:idx_improvement_end[i]]
		duration = log_data[-1]["timestamp"] - log_data[0]["timestamp"]
		str_topic = " ".join(topic["improved_theme"])
		words = re.sub(r"[^a-zA-Z]+",",",str_topic).lower().strip(",").split(",")
		words_no_duplicate = " ".join(list(set(words)))
		topic.update({"log_data":log_data,
					"duration": duration,
					"topic_for_coherence_score": words_no_duplicate,
					"rid":rid,
					"userID":userID
			})
		TOPICS[str(tid)][str(rid)]=topic
		current_topic_nums[str(tid)]+=1
		if duration<50: 
			printThis = True
	if printThis:
		pass
		# pp.pprint(HIT)

# print TOPICS.keys()
# for tid in tid_range:
# 	print TOPICS[str(tid)].keys()
# 	for rid in rid_range:
# 		print " ".join(TOPICS[str(tid)][str(rid)]["improved_theme"])
# exit()
for tid in tid_range:
	five_evals= EVALUATIONS[str(tid)]["original"]
	ORIGINAL_TOPICS[str(tid)]["log_odds"]= log_odds(five_evals)
	ORIGINAL_TOPICS[str(tid)]["accuracy"]= accuracy(five_evals)
	# ORIGINAL_TOPICS[str(tid)]["clarity"] = [five_evals]
	# print ORIGINAL_TOPICS[str(tid)]["log_odds"]


### ADDING FEATURES TO EACH TOPIC
for tid in tid_range:
	for rid in rid_range:
		topic = TOPICS[str(tid)][str(rid)]
		## GENERATING FEATURES
		five_evals = EVALUATIONS[str(tid)][str(rid)]
		features = {}
		topic["accuracy"] = len([e["correctness"] for e in five_evals if e["correctness"]==True])/ 5.0
		features["log_odds"] = log_odds(five_evals)
		features["log_odds_diff"] = features["log_odds"] - ORIGINAL_TOPICS[str(tid)]["log_odds"]
		str_topic = " ".join(topic["improved_theme"])
		features["topic_words"] = re.sub(r"[^a-z]+",",",str_topic).strip(",").split(",")
		features["num_topic_words"] = len(features["topic_words"])
		features["num_articles"] = len([b for b in topic['improved_articles'] if b==True])
		features["self_rating_before"] = np.average([int(r) for r in topic["evaluation_before"]])
		features["self_rating_after"] = np.average([int(r) for r in topic["evaluation_after"]])
		features["self_rating_diff"] = features["self_rating_after"] - features["self_rating_before"] 
		for tn in tools+["toggle_document","undo"]:
			features["freq_event_"+tn] = len([ldata for ldata in topic["log_data"] if ldata["event"].lower()==tn])
		features["freq_refinements"] = len([ldata for ldata in topic["log_data"] if ldata["event"].lower() in tools])
		# features["topic_coherence"] = coherence["improved"][str(tid)][str(rid)]["coherence"]
		# features["topic_coherence_original"] = coherence["original"][str(tid)]["coherence"]
		# features["topic_coherence_diff"] = features["topic_coherence"]-features["topic_coherence_original"]

### ADDING NPMI SCORE
# coherence={}
# with open('dataset/npmi_original.txt','r') as fp:
# 	coherence["original"]={}
# 	lines = fp.readlines()
# 	for ti,line in enumerate(lines):
# 		score = line.split(" ")[0].replace("[","").replace("]","")
# 		text = line.split(" ")[1]
# 		coherence["original"][ti]=float(score)
# 		ORIGINAL_TOPICS[str(ti)]["npmi"]=float(score)

# npmi_improved_dict = {}
# with open('dataset/npmi_improved.txt','r') as fp:
# 	lines = fp.readlines()
# 	for ti,line in enumerate(lines):
# 		idx_break = line.index("]")+1
# 		score = float(line[0:idx_break].replace("[","").replace("]",""))
# 		text = line[idx_break+1:]
# 		npmi_improved_dict[text]=float(score)

# ### JOINING NPMI SCORE WITH TOPICS DATA
# numSuccessfulMatch=0
# for ti,data in TOPICS.iteritems():
# 	for ri,refinedTopic in data.iteritems():
# 		tkey = refinedTopic["topic_for_coherence_score"]
# 		numMatchingScores = 0
# 		for key,coh_score in npmi_improved_dict.iteritems():
# 			if key[:len(key)-1] == tkey[:len(key)-1]:
# 				score = coh_score
# 				numMatchingScores +=1
# 		if numMatchingScores==1:
# 			refinedTopic["npmi_normalized"]=score * (20 / float(len(tkey.split(" "))))
# 			refinedTopic["npmi"]=score
# 			refinedTopic["features"]["npmi"]=score
# 			refinedTopic["features"]["npmi_original"]=ORIGINAL_TOPICS[str(ti)]["npmi"]
# 			numSuccessfulMatch+=1
# if numSuccessfulMatch!=270:
# 	print "FAILED"
# 	exit()


### LET'S CHECK THE SANITY
# for ti,data in TOPICS.iteritems():
# 	for ri,refinedTopic in data.iteritems():
# 		print refinedTopic["npmi"], refinedTopic["npmi_before_normalized"], refinedTopic["topic_for_coherence_score"]

### END OF PREPARATION
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################




####################################################################################
### EXPORTING REFINED TOPIC FOR QUALITATIVE ANALYSIS
####################################################################################
# rows = [["tid","rid","words","meaning","clarity","consistency","correlation","npmi","npmi_diff","npmi_normalized","#words","#articles","FreqRefinements", "FreqAddWords","FreqRemoveWords","FreqRemoveArticles","FreqMergeWords",
# 		"FreqSplitTheme","FreqChangeWordOrder", "Duration", "userID"]]

# for tid in tid_range:
# 	## ORIGINAL TOPIC 
# 	OT = ORIGINAL_TOPICS[str(tid)]
# 	OT_clarity = np.average([int(rt["evaluation_before"][0]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	OT_consistency = np.average([int(rt["evaluation_before"][1]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	OT_correlation = np.average([int(rt["evaluation_before"][2]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	OT_topic_words_str = " ".join([w["word"] for w in OT["words"]])
# 	rows.append([tid, "original", OT_topic_words_str, "", OT_clarity, OT_consistency, OT_correlation, OT["npmi"], 0, OT["npmi"], 20, 40, 0])
# 	# REFINED TOPICS
# 	for rid in rid_range:
# 		T = TOPICS[str(tid)][str(rid)]
# 		TopicID = tid
# 		RefinedTopicID = rid
		
# 		FreqAddWords = T["features"]["freq_event_add_words"]
# 		FreqRemoveWords = T["features"]["freq_event_remove_words"]
# 		FreqRemoveDocs = T["features"]["freq_event_remove_articles"]
# 		FreqMergeWords = T["features"]["freq_event_merge_words"]
# 		FreqSplitTopic = T["features"]["freq_event_split_theme"]
# 		FreqChangeWordOrder = T["features"]["freq_event_change_word_order"]

# 		clarity = int(T["evaluation_after"][0])
# 		consistency = int(T["evaluation_after"][1])
# 		correlation = int(T["evaluation_after"][2])
		
# 		Duration = T["duration"]

# 		rows.append([tid, rid, " ".join(T["improved_theme"]), T["theme_meaning"], clarity, consistency, correlation, T["npmi"], T["npmi"] - OT["npmi"], T["npmi_normalized"], 
# 			T["features"]["num_topic_words"], T["features"]["num_articles"], T["features"]["freq_refinements"],
# 			FreqAddWords, FreqRemoveWords, FreqRemoveDocs, FreqMergeWords, FreqSplitTopic, FreqChangeWordOrder, Duration, T["userID"]])
# with open("dataset/topics_and_features.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(rows)
# exit()


####################################################################################
### EXTRACTING TOPIC WORDS OF THE 20 INTERVIEW STUDY TOPIC
####################################################################################

# with open("dataset/nytimes-20-topics.json","r") as fp:
# 	interview_topics = json.loads(fp.read())

# with open("dataset/interview_topic_words.txt","w") as fp:
# 	for int_tid,int_topic in interview_topics.iteritems():
# 		words = [wr["word"]  for wr in int_topic["words"]]
# 		fp.write(" ".join(words)+"\n")
# exit()




# ####################################################################################
# ### EXPORTING REFINED TOPICS FOR REGRESSION TEST
# ####################################################################################
# rows = [["tid","rid","words","meaning","clarity","consistency","correlation","npmi","accuracy","DLO","#words","#articles","#refinements"]]
# rows = [["TopicID","RefinedTopicID","OriginalAutoCoherence","OriginalSubjClarity","OriginalSubjConsistency","OriginalSubjCorrelation",
# 		"OriginalDocIntrDLO","OriginalDocIntrPercent","FreqAddWords","FreqRemoveWords","FreqRemoveArticles","FreqMergeWords",
# 		"FreqSplitTheme","FreqChangeWordOrder","RefinedWordLength","RefinedDocumentLength","RefinedAutoCoherence","RefindSubjClarity","RefinedSubjConsistency","RefinedSubjCorrelation",
# 		"RefinedDocIntrDLO","RefinedDocIntrPercent","Duration"]]
# for tid in tid_range:
# 	## ORIGINAL TOPIC 
# 	OT = ORIGINAL_TOPICS[str(tid)]
# 	# OT_clarity = np.average([int(rt["evaluation_before"][0]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	# OT_consistency = np.average([int(rt["evaluation_before"][1]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	# OT_correlation = np.average([int(rt["evaluation_before"][2]) for rid,rt in TOPICS[str(tid)].iteritems()])
# 	# OT_topic_words_str = " ".join([w["word"] for w in OT["words"]])
# 	# rows.append([tid, "original", topic_words_str, "", clarity, consistency, correlation, OT["npmi"], OT["accuracy"],
# 			# OT["log_odds"], 20, 40, 0])
# 	## REFINED TOPICS
# 	for rid in rid_range:
# 		T = TOPICS[str(tid)][str(rid)]
# 		TopicID = tid
# 		RefinedTopicID = rid
# 		OriginalAutoCoherence = OT["npmi"]
# 		OriginalSubjClarity = int(T["evaluation_before"][0])
# 		OriginalSubjConsistency = int(T["evaluation_before"][1])
# 		OriginalSubjCorrelation = int(T["evaluation_before"][2])
# 		OriginalDocIntrDLO = OT["log_odds"]
# 		OriginalDocIntrPercent = OT["accuracy"]
# 		FreqAddWords = T["features"]["freq_event_add_words"]
# 		FreqRemoveWords = T["features"]["freq_event_add_words"]
# 		FreqRemoveDocs = T["features"]["freq_event_remove_articles"]
# 		FreqMergeWords = T["features"]["freq_event_merge_words"]
# 		FreqSplitTopic = T["features"]["freq_event_split_theme"]
# 		FreqChangeWordOrder = T["features"]["freq_event_change_word_order"]
# 		RefinedWordLength = T["features"]["num_topic_words"]
# 		RefinedDocumentLength = T["features"]["num_articles"]
# 		RefinedAutoCoherence = T["npmi_normalized"]
# 		RefindSubjClarity = int(T["evaluation_after"][0])
# 		RefinedSubjConsistency = int(T["evaluation_after"][1])
# 		RefinedSubjCorrelation = int(T["evaluation_after"][2])
# 		RefinedDocIntrDLO = T["features"]["log_odds"]
# 		RefinedDocIntrPercent = T["accuracy"]
# 		Duration = T["duration"]
# 		rows.append([TopicID,RefinedTopicID,OriginalAutoCoherence,OriginalSubjClarity,OriginalSubjConsistency,OriginalSubjCorrelation,
# 		OriginalDocIntrDLO,OriginalDocIntrPercent,FreqAddWords,FreqRemoveWords,FreqRemoveDocs,FreqMergeWords,
# 		FreqSplitTopic,FreqChangeWordOrder,RefinedWordLength,RefinedDocumentLength,RefinedAutoCoherence,RefindSubjClarity,RefinedSubjConsistency,RefinedSubjCorrelation,
# 		RefinedDocIntrDLO,RefinedDocIntrPercent, Duration])
# 		# rows.append([tid, rid, " ".join(T["improved_theme"]), T["theme_meaning"], clarity, consistency, correlation, T["npmi"], T["accuracy"], 
# 		# 	T["features"]["log_odds"], T["features"]["num_topic_words"], T["features"]["num_articles"],
# 		# 	T["features"]["freq_refinements"]  ])
# with open("dataset/topic_regression.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(rows)
# 	print "haha"
# exit()


####################################################################################
### STATS FOR EVALUATION  of TOOL USEFULNESS
####################################################################################


## EXPORTING TO CSV ################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################

####################################################################################
### OTHER IDEAS
####################################################################################
# for HIT in TURK_HITS:
# 	print HIT["data"]["general"]
# 	print HIT["data"]["general"]["other_idea"]
# exit()


####################################################################################
### STATS FOR EVALUATION  of TOOL USEFULNESS
####################################################################################
# for ti,data in TOPICS.iteritems():
# 	for ri,refinedTopic in data.iteritems():
# 		print refinedTopic["npmi"], refinedTopic["npmi_before_normalized"], refinedTopic["topic_for_coherence_score"]





####################################################################################
### PART OF SPEECH ANALYSIS ON WORDS
####################################################################################
# word_groups = ["original topic","refined topic","add words", "remove words","merge words: from","merge words: to", "change word order","split theme"]
# pos_tag_list = ["NOUN","PROP","VERB","ADJ","ADV","PHRASE","ETC"]
# pos_dict = {n:{} for n in word_groups}

# def dict_counter(dict, word_list):
# 	for w in word_list:
# 		if w not in dict.keys(): dict[w]=0
# 		dict[w]+=1
# 		##
# 		# if w not in all_words.keys(): all_words[w]=0
# 		# all_words[w]+=1

# ## LOAD PRE-CODED WORDS
# coded_words = {}
# with open("dataset/linguistic_analysis_of_words/coded_words_1st.txt","r") as fp:
# 	for line in fp:
# 		if "//" in line: continue
# 		w, count, pos, tag = line.strip("\n").split("\t")
# 		coded_words[w.strip()]=tag

# ## CREATE WORD DICTIONARY OF 
# for tid in tid_range:
# 	word_original = [word["word"] for word in ORIGINAL_TOPICS[str(tid)]['words']]
# 	dict_counter(pos_dict["original topic"], word_original)
# 	for rid in rid_range: 
# 		topic = TOPICS[str(tid)][str(rid)]
# 		# pp.pprint(topic["log_ddata"])
# 		dict_counter(pos_dict["refined topic"], [re.sub(r'\[.+\]','',w) for w in topic["improved_theme"]])
# 		dict_counter(pos_dict["add words"], [l["message"] for l in topic["log_data"] if l["event"]=="ADD_WORDS"])
# 		dict_counter(pos_dict["remove words"], [l["message"] for l in topic["log_data"] if l["event"]=="REMOVE_WORDS"])
# 		dict_counter(pos_dict["merge words: from"], arr_join([re.sub(r'\[.+\]','',l["message"].split("->")[0]).split(",") for l in topic["log_data"] if l["event"]=="MERGE_WORDS"]))
# 		dict_counter(pos_dict["merge words: to"], arr_join([[l["message"].split("->")[1]] for l in topic["log_data"] if l["event"]=="MERGE_WORDS"]))
# 		dict_counter(pos_dict["change word order"], [l["message"] for l in topic["log_data"] if l["event"]=="CHANGE_WORD_ORDER"])
# 		dict_counter(pos_dict["split theme"], [l["message"] for l in topic["log_data"] if l["event"]=="SPLIT_THEME"])


# def calc_pos_dist(data):
# 	## CALCULATE DISTRIBUTION OF PART OF SPEECH TAGGING FOR DIFFERENT WORD GROUPS
# 	freq_dist = {tag:0 for tag in pos_tag_list}
# 	for term,freq in data.iteritems():
# 		# print term
# 		term_stripped = term.strip()
# 		if term_stripped not in coded_words:
# 			print "oops", term_stripped
# 		else :
# 			matching_tag = coded_words[term_stripped]
# 			if matching_tag=="ETC":
# 				print term_stripped
# 			freq_dist[matching_tag]+=freq
# 	return freq_dist

# # print "ORIGINAL TOPIC: ", calc_pos_dist(original_topic)
# # print "ADDED WORDS: ", calc_pos_dist(added_words)
# # print "REMOVED WORDS: ", calc_pos_dist(removed_words)
# # print "MERGED WORDS _ FROM: ", calc_pos_dist(merge_words_source)
# # print "MERGED WORDS _ TO: ", calc_pos_dist(pos_dict["merge words: to"])
# # print "CHANGE WORD ORDER: ", calc_pos_dist(change_word_order_words)
# # print "SPLIT THEME: ", calc_pos_dist(split_theme_words)
# # print "REFINED TOPIC: ", calc_pos_dist(refined_topic)

# # exit()

# freq_all = {group:calc_pos_dist(pos_dict[group])  for group in word_groups}
# perc_all = {group:{} for group in word_groups}
# for group in word_groups:
# 	freq_list = freq_all[group]
# 	all_freq = sum(freq_list.values())
# 	print group, freq_list, all_freq
# 	for tag in pos_tag_list:
# 		perc_all[group][tag]="{:.1f}%".format(100*(freq_all[group][tag]/ float(all_freq)))
# # perc_all = {group:{tag:freq_all[group][tag]/float(sum(freq_all[group].values())) for tag in pos_tag_list}  for group in word_groups}
# pp.pprint (perc_all)
# # for group in word_groups:
# # 	print group, perc_all[group]
# exit()

### DRAWING STACKED BAR CHART Of POS
# colors = "bgrcmykw"
# plt.figure(facecolor="white")
# fig = plt.subplot(1,1,1)
# row = np.arange(1,len(word_groups)+1,1)+0.5
# prev_values = (0 for group in word_groups)
# width=0.35
# for i, tag in enumerate(pos_tag_list):
# 	print tag
# 	values = [freq_all[group][tag] for group in word_groups]
# 	print values
# 	fig.barh(row, values, color=colors[i])
# 	prev_values = values
# 	# plt.axis([0, 60, 1, 6])
# 	# plt.xticks(range(0,80,20), fontsize="10")
# 	# plt.title(tn.replace("_"," "), fontsize="10")
# fig = plt.gcf()
# # fig.subplots_adjust(bottom=0.2)
# # fig.subplots_adjust(top=0.8)
# fig.set_size_inches(10, 1.7)
# fig.savefig('eval_tools.png', dpi=150)
# # fig.savefig('eval_tools.eps', format='eps')



# with open("dataset/dict_original_topic.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in original_topic.iteritems()]))



# with open("dataset/dict_original_topic.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in original_topic.iteritems()]))
# with open("dataset/dict_refined_topic.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in refined_topic.iteritems()]))
# with open("dataset/dict_added_words.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in added_words.iteritems()]))
# with open("dataset/dict_merge_words_source.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in merge_words_source.iteritems()]))
# with open("dataset/dict_merge_words_target.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in merge_words_target.iteritems()]))
# with open("dataset/dict_change_word_order_words.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in change_word_order_words.iteritems()]))
# with open("dataset/dict_split_theme_words.json","w") as fp:
# 	fp.write(str([(w,freq) for w,freq in split_theme_words.iteritems()]))

# exit()


####################################################################################
### IF THE ORIGINAL TOPIC WAS GOOD, THEN WHAT? 
####################################################################################
### IS NPMI BETTEr ON REFINED TOPICS?
# original_npmi = []
# refined_npmi = []
# diff_npmi = []
# for tid in tid_range:
# 	original_npmi.append(ORIGINAL_TOPICS[str(tid)]["npmi"])
# 	for rid in rid_range:
# 		refined_npmi.append(TOPICS[str(tid)][str(rid)]["npmi_normalized"])
# 		diff_npmi.append(TOPICS[str(tid)][str(rid)]["npmi_normalized"]-ORIGINAL_TOPICS[str(tid)]["npmi"])

# data= original_npmi
# print "NPMI [original]: Avg.:%f, STD:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.max(data), np.min(data))
# data =  refined_npmi
# print "NPMI [refined]: Avg.:%f, STD:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.max(data), np.min(data))
# # data =  diff_npmi
# # print "NPMI [diff]: Avg.:%f, STD:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.max(data), np.min(data))
# print len([sc for sc in diff_npmi if sc<0]), len(refined_npmi), len([sc for sc in diff_npmi if sc<0])/float(len(refined_npmi))

# exit()



### SCATTER PLOT (X:ORIGINAL NPMI, Y:IMPROVED NPMI)
# x=[];  y=[]
# for tid in tid_range:
# 	for rid in rid_range:
# 		x.append(ORIGINAL_TOPICS[str(tid)]["npmi"])
# 		y.append(TOPICS[str(tid)][str(rid)]["npmi"]-ORIGINAL_TOPICS[str(tid)]["npmi"])
# plt.figure(facecolor="white")
# fig = plt.subplot(1,1,1)
# plt.title("Difference of NPMI score(x:original, y:difference)")
# fig.scatter(rand_jitter(x,strength=0.01),y,marker='x')
# # PEARSON CORRELATION
# print stats.pearsonr(x, y)
# (slope, intercept, r,p,stderr) = stats.linregress(x, y)
# print "r-squared: ", r**2
# r_square = "{:.2f}".format(r**2)
# x_list = [min(x),max(x)]
# y_list = [slope*x + intercept for x in x_list]
# plt.plot(x_list, y_list, '-r', linewidth=1)
# # fig.text(0.3,0.3, "Slope = "+"{:.2f}".format(slope)+"\n"+r'$R^2=$'+r_square, fontsize=21, color='b') 
# # PEARSON ENDS
# fig = plt.gcf()
# fig.set_size_inches(7,7)
# fig.savefig('images/npmi_difference.png', dpi=150)
# exit()

### SCATTER PLOT (X:ORIGINAL NPMI, Y:DLO)
# x=[];  y=[]
# for tid in tid_range:
# 	for rid in rid_range:
# 		x.append(ORIGINAL_TOPICS[str(tid)]["npmi"])
# 		y.append(TOPICS[str(tid)][str(rid)]['features']["log_odds"])
# print y
# plt.figure(facecolor="white")
# fig = plt.subplot(1,1,1)
# plt.title("Document Log Odds for NPMI of original topic\n(x:original topic NPMI, y:DLO)")
# fig.scatter(rand_jitter(x,strength=0.01),y,marker='x')
# fig = plt.gcf()
# fig.set_size_inches(7,7)
# fig.savefig('images/DLO_NPMI.png', dpi=150)
# exit()

### SCATTER PLOT (X:ORIGINAL NPMI, Y:DLO DIFF)
# x=[];  y=[]
# for tid in tid_range:
# 	for rid in rid_range:
# 		x.append(ORIGINAL_TOPICS[str(tid)]["npmi"])
# 		y.append(TOPICS[str(tid)][str(rid)]['features']["log_odds"]-ORIGINAL_TOPICS[str(tid)]["log_odds"])
# print y
# plt.figure(facecolor="white")
# fig = plt.subplot(1,1,1)
# plt.title("Document Log Odds diff for NPMI of original topic\n(x:original topic NPMI, y:DLO diff)")
# fig.scatter(rand_jitter(x,strength=0.01),y,marker='x')
# fig = plt.gcf()
# fig.set_size_inches(7,7)
# fig.savefig('images/DLO_DIFF_NPMI.png', dpi=150)
# exit()


### SCATTER PLOT (X:ORIGINAL DLO, Y:diff DLO)
# x=[];  y=[]
# for tid in tid_range:
# 	for rid in rid_range:
# 		x.append(ORIGINAL_TOPICS[str(tid)]["log_odds"])
# 		y.append(TOPICS[str(tid)][str(rid)]['features']["log_odds"]-ORIGINAL_TOPICS[str(tid)]["log_odds"])
# # print y
# plt.figure(facecolor="white")
# fig = plt.subplot(1,1,1)
# # plt.title("Document Log Odds change")
# plt.plot([-6,0.5], [0,0], color="#aaaaaa", linewidth=1, linestyle="--")
# fig.scatter(rand_jitter(x,strength=0.01),y,marker='x')
# # PEARSON CORRELATION
# print stats.pearsonr(x, y)
# (slope, intercept, r,p,stderr) = stats.linregress(x, y)
# print "r-squared: ", r**2
# r_square = "{:.2f}".format(r**2)
# x_list = [min(x),max(x)]
# y_list = [slope*x + intercept for x in x_list]
# plt.axis([-6, 0.5, -5, 6])
# plt.plot(x_list, y_list, '-r', linewidth=1)
# fig.set_xlabel("DLO of original topics");
# fig.set_ylabel("DLO of refined topics - DLO of original topic");
# # fig.text(0.3,0.3, "Slope = "+"{:.2f}".format(slope)+"\n"+r'$R^2=$'+r_square, fontsize=21, color='b') 
# # PEARSON ENDS

# fig = plt.gcf()
# fig.set_size_inches(7.5,5)
# fig.savefig('images/DLO_DIFF.png', dpi=180)
# exit()


### BOXPLOT (X: DLO,   Y: original vs refined)
# box_data = 	[	[ORIGINAL_TOPICS[str(tid)]["log_odds"] for tid in tid_range], 
# 				arr_join([[topic["features"]["log_odds"] for rid,topic in tlist.iteritems()] for tid,tlist in TOPICS.iteritems()])
# 			]
# # print box_data
# data = box_data[0]
# print "DLO [ORIGINAL TOPICS]: Avg.:%f, STD:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.max(data), np.min(data))
# data = box_data[1]
# print "DLO [REFINED TOPICS]: Avg.:%f, STD:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.max(data), np.min(data))


# plt.figure(facecolor="white")
# plt.boxplot(box_data, vert=False, sym='')
# means = [np.mean(data) for data in box_data]
# row = np.arange(1,3,1)
# plt.plot(means, row, 'rs')
# plt.axis([-5, 0, 0, 3])
# plt.yticks(row, [t.replace("_"," ") for t in ["original topics","refined topics"]], fontsize="16")
# ax = plt.gca()
# ax.invert_yaxis()

# fig = plt.gcf()
# fig.subplots_adjust(left=0.4)
# fig.subplots_adjust(top=0.9)
# fig.set_size_inches(8, 3)
# fig.savefig('images/DLO_box_plot_original_vs_refined.png', dpi=150)

# exit()


####################################################################################
### REFINEMENT FEATURES vs DLO
####################################################################################

## DRAWING SCATTER PLOTS
# features = arr_join([[rt["features"] for rt in tlist] for ti, tlist in TOPICS.iteritems()])
# plt.figure(facecolor="white")
# y = rand_jitter([feat["log_odds"] for feat in features],strength=0.01, direction="minus")

# fkey = features[0].keys()
# fkey.remove("topic_words")
# fkey.remove("log_odds")
# for i, key in enumerate(fkey):
# 	fig = plt.subplot(5,4,i+1)
# 	x = rand_jitter([feat[key] for feat in features],strength=0.01)
# 	fig.text(0.95, 0.05,key,horizontalalignment='right',verticalalignment='bottom',transform = fig.transAxes)
# 	if key=="num_topic_words": plt.axis([0,50,-7,1])
# 	fig.scatter(x,y,marker='x',alpha=0.25)
# fig = plt.gcf()
# fig.set_size_inches(20, 12)
# fig.savefig('scatter_features.png', dpi=150)
# exit()

# ###DRAWING SCATTER PLOTS OF DIFFERENT OF DLO
# features = arr_join([[rt["features"] for ri, rt in tlist.iteritems()] for ti, tlist in TOPICS.iteritems()])
# plt.figure(facecolor="white")
# y = rand_jitter([feat["log_odds_diff"] for feat in features],strength=0.01, direction="minus")

# fkey = features[0].keys()
# fkey.remove("topic_words")
# fkey.remove("log_odds")
# for i, key in enumerate(fkey):
# 	fig = plt.subplot(5,4,i+1)
# 	x = rand_jitter([feat[key] for feat in features],strength=0.01)
# 	fig.text(0.95, 0.05,key,horizontalalignment='right',verticalalignment='bottom',transform = fig.transAxes)
# 	fig.scatter(x,y,marker='x',alpha=0.25)
# fig = plt.gcf()
# fig.set_size_inches(20, 12)
# fig.savefig('images/scatter_features_DLO_diff.png', dpi=150)

# ###DRAWING SCATTER PLOTS OF ACCURACY
# features = arr_join([[rt["features"] for ri, rt in tlist.iteritems()] for ti, tlist in TOPICS.iteritems()])
# y = arr_join([[rt["accuracy"] for ri, rt in tlist.iteritems()] for ti, tlist in TOPICS.iteritems()])
# plt.figure(facecolor="white")

# fkey = features[0].keys()
# fkey.remove("topic_words")
# fkey.remove("log_odds")
# for i, key in enumerate(fkey):
# 	fig = plt.subplot(5,4,i+1)
# 	x = rand_jitter([feat[key] for feat in features],strength=0.01)
# 	fig.text(0.95, 0.05,key,horizontalalignment='right',verticalalignment='bottom',transform = fig.transAxes)
# 	fig.scatter(x,y,marker='x',alpha=0.25)
# fig = plt.gcf()
# fig.set_size_inches(20, 12)
# fig.savefig('images/scatter_features_accuracy.png', dpi=150)
# exit()

####################################################################################
### COMPARE GROUPS (AGGREGATED BY ORIGINAL TOPIC)
####################################################################################

# improved_topics = arr_join([[rt for ri, rt in tlist.iteritems() if rt["features"]["log_odds_diff"]>0] for ti, tlist in TOPICS.iteritems()])
# same_topics = arr_join([[rt for ri, rt in tlist.iteritems() if rt["features"]["log_odds_diff"]==0] for ti, tlist in TOPICS.iteritems()])
# unimproved_topics = arr_join([[rt for ri, rt in tlist.iteritems() if rt["features"]["log_odds_diff"]<0] for ti, tlist in TOPICS.iteritems()])

# # print len(improved_topics)
# # print len(same_topics)
# # print len(unimproved_topics)

# # ### COMPARING DISTRIBUTIONS OF REFINEMENT FEATURES PER GROUP
# features_im = [topic["features"] for topic in improved_topics]
# features_un = [topic["features"] for topic in unimproved_topics]

# plt.figure(facecolor="white")

# steps = {
# 	'freq_refinements':4, 'freq_event_change_word_order':1, 'freq_event_undo':2, 'freq_event_remove_articles':3,
# 	'self_rating_before':0.5, 'freq_event_split_theme':2, 'log_odds_diff':0.5, 'num_articles':1,
# 	'self_rating_diff':0.5, 'self_rating_after':0.5, 'freq_event_merge_words':1, 'num_topic_words':3,				
# 	'freq_event_toggle_document':4, 'freq_event_add_words':2, 'freq_event_remove_words':2,
# 	'npmi':0.015, 'npmi_original':0.015
# }
# fkey = sorted(features_im[0].keys())
# fkey.remove("topic_words")
# fkey.remove("log_odds")
# for i, key in enumerate(fkey):
# 	fig = plt.subplot(6,3,i+1)
# 	values_im = [feat[key] for feat in features_im]
# 	values_un = [feat[key] for feat in features_un]
# 	values = values_im + values_un
# 	bins = np.arange(min(values),max(values),steps[key])
# 	print key, min(values), max(values), bins
# 	fig.hist(values_im, bins=bins, alpha=0.5, color='b', label='better')  # histtype='stepfilled', fill=False, 
# 	fig.hist(values_un, bins=bins, alpha=0.5, color='r', label='worse')
# 	fig.text(0.95, 0.95, key,horizontalalignment='right',verticalalignment='top',transform = fig.transAxes)
# fig = plt.gcf()
# fig.set_size_inches(15, 15)
# fig.savefig('images/comparison_im_un.png', dpi=150)
# exit()








####################################################################################
### EXPORT ORIGINAL TOPICS
####################################################################################
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())

# with open("dataset/mturk_original_topics.txt","w") as fp:
# 	for ti in range(31):
# 		fp.write(" ".join(t["word"] for t in topicJSON[str(ti)]['words'][:20]) + "\n")
# exit()

####################################################################################
### EXPORT IMPROVED TOPICS
####################################################################################
# improved_topics = {}
# for HIT in TURK_HITS:
# 	for topic in HIT["data"]['topics']:
# 		if topic["tid"] not in improved_topics.keys(): improved_topics[topic["tid"]]=[]
# 		improved_topics[topic["tid"]].append(topic["improved_theme"])
# with open("dataset/mturk_improved_topics.txt","w") as fp:
# 	for ti in tid_range:  #0-30 without 21 (for training)
# 		new_themes = improved_topics[str(ti)]
# 		for i, theme in enumerate(new_themes):
# 			str_topic = " ".join(theme)
# 			words = re.sub(r"[^a-zA-Z]+",",",str_topic).lower().strip(",").split(",")
# 			words_no_duplicate = list(set(words))
# 			# fp.write(str(ti)+"|"+str(i)+"|"+" ".join(words_no_duplicate)+"\n")
# 			fp.write(" ".join(words_no_duplicate)+"\n")
# with open("dataset/mturk_improved_topics_with_format.txt","w") as fp:
# 	for ti in tid_range:  #0-30 without 21 (for training)
# 		fp.write(str(ti)+"\n")
# 		new_themes = improved_topics[str(ti)]
# 		for i, theme in enumerate(new_themes):
# 			str_topic = " ".join(theme)
# 			fp.write(str_topic+"\n")
# exit()

# rows = ["topic_id","ref_id","refined_words","coherence","freq_refinement",
# 		"DLO","DLO_diff","accuracy","accuracy_diff"]
# for tid,refinedTopicList in TOPICS.iteritems(): 
# 	for rid, rt in enumerate(refinedTopicList):
# 		words_no_duplicate = " ".join(list(set(re.sub(r"[^a-z]+",","," ".join(rt["improved_theme"])).strip(",").split(","))))
# 		row = [int(tid),rid, rt["improved_theme"],      ]




####################################################################################
### PRECALCULATING TOPIC COHERENCE : LCP, Log Conditional Probability by Mimno
####################################################################################

### INTERVIEW TOPICS - 20 TOPICS FROM NYTIMES CORPUS
# with open("dataset/nytimes-20-topics.json","r") as fp:
# 	interview_topics = json.loads(fp.read())
# csv_result = ["topicNum","LCP"]
# for tn in sorted(interview_topics.keys(), key=lambda x: int(x)):
# 	words = [w["word"] for w in interview_topics[tn]["words"]]
# 	print tn, " ".join(words)

# with open("dataset/LCP_interview.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	for tn in sorted(interview_topics.keys(), key=lambda x: int(x)):
# 		words = [w["word"] for w in interview_topics[tn]["words"]]
# 		coh = topic_coherence(words, dict_tokenized_documents)
# 		writer.writerow([tn, coh])
# exit()



### ORIGINAL TOPICS
# tempdata = {"original":{}}
# for tid in tid_range:
# 	original_topic = EVALUATIONS[str(tid)]["original"][0]['material']["theme"]
# 	coherence = topic_coherence(original_topic,dict_tokenized_documents)
# 	tempdata["original"][str(tid)]={
# 		"words": original_topic,
# 		"coherence": coherence
# 	}
# with open('dataset/LCP_original.json','w') as fp:
# 	json.dump(tempdata, fp, sort_keys=True, indent=4)
# exit()

### IMPROVED TOPICS
# tempdata = {"improved":{}}
# for tid in tid_range:
# 	tempdata["improved"][str(tid)]={}
# 	for rid in rid_range:
# 		topic = TOPICS[str(tid)][str(rid)]
# 		str_topic = " ".join(topic["improved_theme"])
# 		words = re.sub(r"[^a-z]+",",",str_topic).strip(",").split(",")
# 		words_top20 = words[:20]
# 		coherence = topic_coherence(words_top20,dict_tokenized_documents)
# 		tempdata["improved"][str(tid)][str(rid)]={
# 			"words": words,
# 			"coherence": coherence
# 		}
# with open('dataset/LCP_improved.json','w') as fp:
# 	json.dump(tempdata, fp, sort_keys=True, indent=4)
# exit()

### EXPORTING LCP SCORES for Wilcoxon Signed Ranked Sum test
# with open('dataset/LCP_original.json','r') as fp:
# 	lcp_original_dict = json.loads(fp.read())["original"]
# 	# for tn in range(0,30):
# 	# 	print lcp_original_dict[str(tn)]["coherence"], lcp_original_dict[str(tn)]["words"][:2]
# with open('dataset/LCP_improved.json','r') as fp:
# 	lcp_improved_dict = json.loads(fp.read())["improved"]
# csv_result = ["topicNum", "refinementNum", "original_LCP", "improved_LCP"]
# with open("dataset/LCP_diff.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	for tn in sorted(lcp_original_dict.keys(), key=lambda x: int(x)):
# 		for rn in sorted(lcp_improved_dict[tn].keys(), key=lambda x: int(x)):
# 			writer.writerow([tn, rn, lcp_original_dict[tn]["coherence"], lcp_improved_dict[tn][rn]["coherence"]])
# exit()

### GET STATISTICS OF LCP SCORES

# with open('dataset/LCP_original.json','r') as fp:
# 	lcp_original = json.loads(fp.read())
# data = []
# for tid, tdata in lcp_original["original"].iteritems():
# 	data.append(tdata["coherence"])
# print "LCP_ORIGINAL:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# data = []

# with open('dataset/LCP_improved.json','r') as fp:
# 	lcp_improved = json.loads(fp.read())
# data = []
# for tid, tdata in lcp_improved["improved"].iteritems():
# 	for rid, rdata in tdata.iteritems():
# 		data.append(rdata["coherence"])
# print "LCP_IMPROVED:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# data = []

# exit()


## DRAWING DISTRIBUTION GRAPH





# print results

		
### TOPIC SCHEMA
# {u'evaluation_after': [u'4', u'4', u'4'],
#  u'evaluation_before': [u'4', u'4', u'4'],
#  u'extra_information': u'',
#  u'improved_articles': [True, ...],
#  u'improved_theme': [u'neediest',,...],
#  u'log': [{u'event': u'OPEN_PAGE',
#            u'message': u'intro',
#            u'timestamp': 1440032265},...],
#  u'theme_meaning': u'Homelessness in America',
#  u'tid': u'3'}

### EVALUATION SCHEMA
# {'done': 'True',
#  'isCorrect': 'T,F,T,T,T,T,T,T,T,T',
#  'material': [{u'articles': [{u'content': {u'text': u"  ... ",
#                                            u'title': u'Head of MTV Networks Leaving'},
#                               u'file': u'1818236.txt',
#                               u'i': 31,
#                               u'other_topics': {u'0': 0.000274033335954887,...},
#                               u'weight': 0.6092518523875573},AND 4 MORE ARTICLES],
#                u'intruder': {u'content': {u'text': u"...",
#                                           u'title': u"TODAY'S MATCHUPS"},
#                              u'file': u'1820501.txt',
#                              u'i': 6,
#                              u'other_topics': {u'0': 0.0004505021252755011,...},
#                              u'weight': 0.8256494320762147}, // END OF ENTRUDER
#                u'rid': u'1', 
#                u'theme': [u'company',...],
#                u'tid': u'4'}, AND 9 MORE TOPICS TO Be EVALUATED...],
#  'numArticles': '5',
#  'refinedTopicID': '4-1,0-3,3-7,6-2,7-0,8-original,9-3,2-5,1-3,5-3',
#  'result': {u'topics': [{u'file_list': [u'1819071.txt',
#                                         u'1818236.txt',
#                                         u'1820501.txt',
#                                         u'1818348.txt',
#                                         u'1817404.txt'],
#                          u'log': [{u'event': u'OPEN_PAGE',
#                                    u'message': u'intro',
#                                    u'timestamp': 1441777308},...],
#                          u'tid': u'4',
#                          u'unrelated_article': u'1820501.txt'},...]},
#  'updated': '2015-09-09 05:47:25.820010',
#  'userID': 'RU1Z1UVW',
#  'version': '1'}






####################################################################################
####################################################################################
### GENERATING IMPROVED THEMES FILE FOR TURK EVALUATION. EXTRACTING 30 * 9 = 270 REFINED TOPICS 
# improved_themes = {}
# for HIT in TURK_HITS:
# 	for topic in HIT["data"]['topics']:
# 		if topic["tid"] not in improved_themes.keys(): improved_themes[topic["tid"]]={"themes":[]}
# 		theme_data = {
# 			'tid':topic['tid'],
# 			'userID':HIT["userID"],
# 			'improved_theme':topic["improved_theme"],
# 			'improved_articles':topic["improved_articles"],
# 			'evaluation_before':topic["evaluation_before"],
# 			'evaluation_after':topic["evaluation_after"],
# 			'improved_articles':topic["improved_articles"]
# 		}
# 		improved_themes[topic["tid"]]["themes"].append(theme_data)
# # pp.pprint(improved_themes)
# ### FINDING INTRUDER ARTICLES.  INTRUDERS ARE AMONG TOP5 ARTICLES OF OTHER TOPICS THAT HAD THIS TOPIC AT ITS BOTTOM 5
# docs_for_all_topics = {tid:json.loads(open("../refinement/dataset/nytimes-31-documents-"+str(tid)+".json","r").read()) for tid in range(31)}
# intruders_all = [] 
# for tid, data in improved_themes.iteritems(): # ITERATE EACH TOPIC TO ADD INTRUDER ARTICLES
# 	print tid
# 	top_articles_for_other_topics = arr_join([docs_for_all_topics[i][:20] for i in range(31) if str(i)!=str(tid)])
# 	top_articles_sorted = sorted(top_articles_for_other_topics, key=lambda art: art["other_topics"][str(tid)])
# 	intruders = top_articles_sorted[:len(top_articles_sorted)-100]
# 	data["intruders"]=random.sample(intruders,20)
# 	pp.pprint([(a["content"]["title"], a["other_topics"][str(tid)]) for a in data["intruders"]])
# ##### EXPORT IT AS JSON FILE
# with open('improved_themes.json','w') as fp:
# 	json.dump(improved_themes, fp, sort_keys=True, indent=4)

# exit()
####################################################################################
####################################################################################



####################################################################################
####################################################################################
### # REFINEMENTS AND DURATION PER TOPIC
# num_refinement = []
# duration = []
# for tid, tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():
# 		num_refinement.append(len(topic["log_data"]))
# 		duration.append(topic["duration"])
# data = num_refinement
# print "# REFINEMENTS:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# data = duration
# print "DURATION:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# exit()


####################################################################################
####################################################################################
### LIKELIHOOD OF REFINEMENTS USED PER TOPIC

# num_topics_for_ref = {tn:0 for tn in tools}
# total_topics = 0
# for tid, tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():
# 		total_topics+=1
# 		for tn in tools:
# 			if topic["features"]["freq_event_"+tn]>0:
# 				num_topics_for_ref[tn]+=1
# # print num_topics_for_ref
# # print total_topics
# print [(tn,float(num)/total_topics)  for tn,num in num_topics_for_ref.iteritems()]
# exit()






####################################################################################
####################################################################################
### EVAL_TOOLS 

### EXPORTING TO CSV
# eval_tools = [d['data']['general']['eval_tools'] for d in TURK_HITS]
# with open("dataset/eval_tools.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerow([tn for tn in tools])	
# 	for evt in eval_tools:
# 		writer.writerow([evt[tn] for tn in tools])	
# exit()


# eval_tools = [d['data']['general']['eval_tools'] for d in TURK_HITS]
# eval_per_tool = {t:{ 
# 			"raw_value":[int(e[t]) for e in eval_tools],
# 			"average":np.average([int(e[t]) for e in eval_tools]),
# 			"std":np.std([int(e[t]) for e in eval_tools])
# 		} for t in tools}
# print "*********************************************************"
# print "************************************   EVALUTION OF TOOLS"
# for s in ["{:20s}".format(tool_name) + "\t: Avg:"+"{:.2f}".format(data["average"])+ ",\t Std:"+"{:.2f}".format(data["std"])  for tool_name, data in eval_per_tool.iteritems()]:
# 	print s
# print "*********************************************************"

# plt.figure(facecolor="white")
# for i, tn in enumerate(tools):
# 	fig = plt.subplot(1,6,i+1)
# 	row = np.arange(1,6,1)+0.5
# 	raw_data = eval_per_tool[tn]["raw_value"]
# 	hist_data = [len([d for d in raw_data if d==n]) for n in [1,2,3,4,5]]
# 	fig.barh(row, hist_data, align='center', color="gray")
# 	plt.axis([0, 60, 1, 6])
# 	plt.xticks(range(0,80,20), fontsize="10")
# 	plt.title(tn.replace("_"," "), fontsize="10")
# 	if i==0:
# 		plt.yticks(row, ('very useless','useless','neutral','useful','very useful'), fontsize="10")
# 	else:
# 		plt.yticks(row, ("","","","","",""))
# fig = plt.gcf()
# fig.subplots_adjust(bottom=0.2)
# fig.subplots_adjust(top=0.8)
# fig.set_size_inches(10, 1.7)
# fig.savefig('eval_tools.png', dpi=150)
# # fig.savefig('eval_tools.eps', format='eps')

# exit() 


####################################################################################
####################################################################################
### EVALUATION BEFORE AND AFTER
# eval_clarity = [[],[]]
# eval_consistency = [[],[]]
# eval_correlation = [[],[]]
# for HIT in TURK_HITS:
# 	for topic in HIT["data"]['topics']:
# 		eval_clarity[0].append(float(topic["evaluation_before"][0]))
# 		eval_clarity[1].append(float(topic["evaluation_after"][0]))
# 		eval_consistency[0].append(float(topic["evaluation_before"][1]))
# 		eval_consistency[1].append(float(topic["evaluation_after"][1]))
# 		eval_correlation[0].append(float(topic["evaluation_before"][2]))
# 		eval_correlation[1].append(float(topic["evaluation_after"][2]))
# print "*********************************************************"
# print "************************************   EVALUTION OF THEMES"
# print "{:20s}".format("THEME CLARITY: BEFORE") + "\t: Avg:"+"{:.2f}".format(np.average(eval_clarity[0]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_clarity[0]))
# print "{:20s}".format("THEME CLARITY: AFTER") + "\t: Avg:"+"{:.2f}".format(np.average(eval_clarity[1]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_clarity[1]))
# print "{:20s}".format("ARTICLE CONSISTENCY: BEFORE") + "\t: Avg:"+"{:.2f}".format(np.average(eval_consistency[0]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_consistency[0]))
# print "{:20s}".format("ARTICLE CONSISTENCY: AFTER") + "\t: Avg:"+"{:.2f}".format(np.average(eval_consistency[1]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_consistency[1]))
# print "{:20s}".format("THEME-ARTICLE CORRELATION: BEFORE") + "\t: Avg:"+"{:.2f}".format(np.average(eval_correlation[0]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_correlation[0]))
# print "{:20s}".format("THEME-ARTICLE CORRELATION: AFTER") + "\t: Avg:"+"{:.2f}".format(np.average(eval_correlation[1]))+ ",\t Std:"+"{:.2f}".format(np.std(eval_correlation[1]))
# print "*********************************************************"



# eval_all = [eval_clarity[0],eval_clarity[1], 
# 			eval_consistency[0],eval_consistency[1],
# 			eval_correlation[0],eval_correlation[1]]
# ##### BOXPLOT OF EVALUATIONS
# plt.figure(facecolor="white")
# plt.boxplot(eval_all, vert=False, sym='')
# means = [np.mean(data) for data in eval_all]
# row = np.arange(1,7,1)
# plt.plot(means, row, 'rs')
# plt.axis([1, 5, 0,7])
# plt.yticks(row, [t.replace("_"," ") for t in ["Clarity [original]","Clarity [refined]", "Consistency [original]","Consistency [refined]", "Correlation [original]","Correlation [refined]"]], fontsize="16")
# ax = plt.gca()
# ax.invert_yaxis()

# fig = plt.gcf()
# fig.subplots_adjust(left=0.4)
# fig.subplots_adjust(top=0.9)
# fig.set_size_inches(8, 3)
# fig.savefig('images/evaluation_box_plot.png', dpi=150)

# # exit()


# exit()



# ### # OF TOPICS IMPROVED 
# count = 0
# for i in range(len(eval_clarity[0])):
# 	if eval_clarity[0][i]<eval_clarity[1][i] or eval_consistency[0][i]<eval_consistency[1][i] or eval_correlation[0][i]<eval_correlation[1][i]:
# 		count+=1
# print str(count) + "out of " + str(len(eval_clarity[0]))
# ### SCATTERPLOT
# plt.figure(facecolor="white")
# ax = plt.subplot(2,3,1)
# plt.axis([0, 6, 0, 6])
# ax.set_ylabel("consistency");
# rx = rand_jitter(eval_clarity[0]) 
# ry = rand_jitter(eval_consistency[0])
# plt.scatter(rx, ry, c='r', marker='+', alpha=0.6, s=35)

# ax = plt.subplot(2,3,2)
# plt.axis([0, 6, 0, 6])
# ax.set_ylabel("correlation");
# rx = rand_jitter(eval_consistency[0]) 
# ry = rand_jitter(eval_correlation[0])
# plt.scatter(rx, ry, c='r', marker='+', alpha=0.6, s=35)

# ax = plt.subplot(2,3,3)
# plt.axis([0, 6, 0, 6])
# ax.set_ylabel("clarity");
# rx = rand_jitter(eval_correlation[0]) 
# ry = rand_jitter(eval_clarity[0])
# plt.scatter(rx, ry, c='r', marker='+', alpha=0.6, s=35)


# ax = plt.subplot(2,3,4)
# plt.axis([0, 6, 0, 6])
# ax.set_xlabel("clarity");	ax.set_ylabel("consistency");
# rxi = rand_jitter(eval_clarity[1]) 
# ryi = rand_jitter(eval_consistency[1])
# plt.scatter(rxi, ryi, c='g', marker='x', alpha=0.6, s=35)

# ax = plt.subplot(2,3,5)
# plt.axis([0, 6, 0, 6])
# ax.set_xlabel("consistency");	ax.set_ylabel("correlation");
# rxi = rand_jitter(eval_consistency[1]) 
# ryi = rand_jitter(eval_correlation[1])
# plt.scatter(rxi, ryi, c='g', marker='x', alpha=0.6, s=35)

# ax = plt.subplot(2,3,6)
# plt.axis([0, 6, 0, 6])
# ax.set_xlabel("correlation");	ax.set_ylabel("clarity");
# rxi = rand_jitter(eval_correlation[1]) 
# ryi = rand_jitter(eval_clarity[1])
# plt.scatter(rxi, ryi, c='g', marker='x', alpha=0.6, s=35)

# fig = plt.gcf()
# fig.suptitle("Change of self-rated topic quality", fontsize=14)
# plt.show()
#### STACKED BAR CHART
# plt.figure(facecolor="white")
# plt.subplot(1,3,1)
# bottom=[0,0,0,0,0,0]
# all_data = []
# cmap=['b','g','r','y','k']
# for v in [1,2,3,4,5]:   # DRAW FROM BOTTOM OF STACK:  v=1 means least useful
# 	data = []
# 	data.append(len([d for d in eval_clarity[0] if d==float(v)]))
# 	data.append(len([d for d in eval_clarity[1] if d==float(v)]))
# 	data.append(len([d for d in eval_consistency[0] if d==float(v)]))
# 	data.append(len([d for d in eval_consistency[1] if d==float(v)]))
# 	data.append(len([d for d in eval_correlation[0] if d==float(v)]))
# 	data.append(len([d for d in eval_correlation[1] if d==float(v)]))
# 	plt.bar(range(6), data, bottom = bottom, alpha=0.5, color=cmap[v-1])
# 	print data
# 	all_data.append(data)
# 	bottom=[bottom[i]+data[i] for i in range(len(bottom))]
# plt.show()
# print [sum([data[i] for data in all_data]) for i in range(1,6)]
# exit()


##########################################################################
##########################################################################
##### LENGTH OF TOPIC WORDS AFTER IMP.
##########################################################################
##########################################################################
# len_words = []
# for tid, tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():		
# 		len_words.append(len(topic["improved_theme"]))

# data = len_words
# print "# WORDS:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# #### HISTOGRAM OF # WORDS AFTER IMP
# fig = plt.figure(facecolor="white")
# plt.hist(len_words, 25, color='gray')
# plt.axis([0,28,0,35])
# plt.title("# TOPICS WORDS AFTER IMPROVEMENT", fontsize="14")
# plt.xlabel("# WORDS",fontsize="13");	plt.ylabel("FREQUENCY",fontsize="13");
# # fig = plt.gcf()
# fig.subplots_adjust(bottom=0.2)
# fig.subplots_adjust(top=0.8)
# fig.set_size_inches(10, 5)
# fig.savefig('images/num_words.png', dpi=150)
# exit()

##########################################################################
##########################################################################
##### LENGTH OF REMAINING ARTICLES
##########################################################################
##########################################################################
# all_articles = []
# for hit in HITS:
# 	for topic in hit["data"]["topics"]:
# 		all_articles.append(topic["improved_articles"])
# len_articles = [len([b for b in t if b==True]) for t in all_articles]
# data = len_articles
# print len_articles
# print float(len([l for l in len_articles if l==40]))/ float(len(len_articles))
# print "# ARTICLES:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# #### HISTOGRAM OF # ARTICLES AFTER IMP
# fig = plt.figure(facecolor="white")
# plt.hist(len_articles, 25, color='gray')
# plt.axis([0,40,0,140])
# plt.title("# ARTICLES AFTER IMPROVEMENT", fontsize="14")
# plt.xlabel("# ARTICLES",fontsize="13");	plt.ylabel("FREQUENCY",fontsize="13");
# # fig = plt.gcf()
# fig.subplots_adjust(bottom=0.2)
# fig.subplots_adjust(top=0.8)
# fig.set_size_inches(10, 5)
# fig.savefig('num_articles.png', dpi=150)
# exit()

##########################################################################
##########################################################################
##### TIME SPENT FOR REFINEMENT
##########################################################################
##########################################################################

# durations = []
# for tid,tlist in TOPICS.iteritems():
# 	for topic in tlist:
# 		first_event = topic["log_data"][0]
# 		last_event = topic["log_data"][len(topic["log_data"])-1]
# 		# print first_event
# 		duration = last_event["timestamp"] - first_event["timestamp"]
# 		durations.append(duration)
# print np.average(durations)
# print np.std(durations), max(durations), min(durations)
# ##### HISTOGRAM OF DURATION
# plt.figure(facecolor="white")
# plt.hist(durations, 50, color='gray')
# plt.show()
# #####
# exit()

##########################################################################
##########################################################################
##### FREQUENCY OF TOOL USAGE
##########################################################################
##########################################################################

# all_logs = []
# freq_all = [[tn for tn in tools]]
# for tid,tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():
# 		all_logs.append(topic["log_data"])
# 		log_list = topic["log_data"]
# 		freq_one_topic = [len([log for log in log_list if log["event"].lower()==tn]) for tn in tools]
# 		freq_all.append(freq_one_topic)
# with open("dataset/freq_tool_usage.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(freq_all)

# num_usage_list = []

# for tn in tools:
# 	num_usage = [len([event for event in log if event["event"].lower()==tn]) for log in all_logs]
# 	num_usage = [num for num in num_usage if num!=0]
# 	data = num_usage
# 	print "%s:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(tn, np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# 	print stats.normaltest(data)
# 	num_usage_list.append(num_usage)


# exit()
# ##### BOXPLOT OF # USAGE PER REFINEMENT TYPE
# plt.figure(facecolor="white")
# row = np.arange(1,7,1)
# plt.boxplot(num_usage_list, vert=False, sym='')
# means = [np.mean(data) for data in num_usage_list]
# plt.plot(means, row, 'rs')
# plt.axis([0, 24, 0,7])
# plt.yticks(row, [t.replace("_"," ") for t in tools], fontsize="16")
# ax = plt.gca()
# ax.invert_yaxis()

# fig = plt.gcf()
# fig.subplots_adjust(left=0.3)
# fig.subplots_adjust(top=0.8)
# fig.set_size_inches(10, 3)
# fig.savefig('images/freq_tool_usage_when_used.png', dpi=150)

# exit()

##### HISTOGRAM OF # REFINEMENTS
# plt.figure(facecolor="white")
# plt.hist(len_refinements, 50, color='gray')
# plt.show()
#####




##########################################################################
##########################################################################
##### ADDING WORDS : DETAIL
##########################################################################
##########################################################################
# print  [(event["event"],event["message"]) for event in HITS[0]["data"]["topics"][2]["log"]]
# exit()
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())
# all_logs_per_topic = {str(i):[] for i in tid_range}
# all_logs_dict = {str(i):{} for i in tid_range}
# for tid, tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():
# 		logs = topic["log_data"]
# 		aw_logs = [e["message"] for e in logs if e["event"]=="ADD_WORDS"]
# 		all_logs_per_topic[tid].append(aw_logs)
# 		for aw in aw_logs:
# 			all_logs_dict[tid][aw]=0
# pp.pprint(all_logs_per_topic)
# # exit()

# # ### WHERE THE ADDED WORDS ARE FROM?  ARE THEY FROM TITLES? TEXT? 20-40 WORDS? HYPERNYMS?
# all_words_from = {'all':[], 'title':[], 'text':[], "2040":[], "nowhere":[]}
# for tid,addedWords in all_logs_per_topic.iteritems():
# 	docs = json.loads(open("dataset/nytimes-31-documents-"+str(tid)+".json","r").read())
# 	print "WORDS \t", [w['word'] for w in topicJSON[str(tid)]['words']]
# 	# print "TITLES \t", pp.pprint([doc['content']['title'] for doc in docs])
# 	print "ADDED \t", addedWords
# 	words2040 = " ".join([w['word'] for w in topicJSON[str(tid)]['words'][20:]])
# 	titles = " ".join([doc['content']['title'] for doc in docs])
# 	texts = " ".join([doc['content']['text'] for doc in docs])
# 	text_list = [doc['content']['text'] for doc in docs]
# 	set_addedWords = [y for x in addedWords for y in x]
# 	words_from_titles = []
# 	words_from_text = []
# 	words_from_2040 = []
# 	words_from_nowhere = []
# 	for aw in all_logs_dict[tid].keys():
# 		regex = re.compile(r'%s' % aw, re.IGNORECASE)
# 		num_documents_containing_aw = len([1 for text in text_list if len(regex.findall(text))>0])
# 		all_logs_dict[tid][aw]= num_documents_containing_aw
# 		print aw, num_documents_containing_aw
# 	for w in set_addedWords:
# 		regex = re.compile(r'%s' % w, re.IGNORECASE)
# 		if len(regex.findall(words2040))>0: 
# 			# print w + " is found in words 20-40."
# 			words_from_2040.append(w)
# 		if len(regex.findall(titles))>0: 
# 			# print w + " is found in titles."
# 			words_from_titles.append(w)
# 		if len(regex.findall(texts))>0: 
# 			# print w + " is found in text."
# 			words_from_text.append(w)
# 		if len(regex.findall(words2040))==0 and len(regex.findall(titles))==0 and len(regex.findall(texts))==0:
# 			words_from_nowhere.append(w)
# 	all_words_from["all"] += list(set_addedWords)
# 	all_words_from["title"] += words_from_titles
# 	all_words_from["text"] += words_from_text
# 	all_words_from["2040"] += words_from_2040
# 	all_words_from["nowhere"] += words_from_nowhere
# 	print "ADDED WORDS \t", set_addedWords
# 	print "FROM TITLES\t", words_from_titles
# 	print "FROM TEXT\t", words_from_text
# 	print "FROM WORDS2040\t", words_from_2040
# 	print "FROM NOWHERE\t", words_from_nowhere
# 	print "\n"
# print all_words_from
# print "ALL::: ", len(all_words_from["all"]) ,  float(len(all_words_from["all"])) /len(all_words_from["all"])
# print "TITLE::: ", len(all_words_from["title"]),  float(len(all_words_from["title"]))/len(all_words_from["all"])
# print ", ".join(all_words_from["title"])
# print "TEXT::: ", len(all_words_from["text"]),  float(len(all_words_from["text"]))/len(all_words_from["all"])
# print ", ".join(all_words_from["text"])
# print "2040::: ", len(all_words_from["2040"]),  float(len(all_words_from["2040"]))/len(all_words_from["all"])
# print ", ".join(all_words_from["2040"])
# print "nowhere::: ", len(all_words_from["nowhere"]),  float(len(all_words_from["nowhere"]))/len(all_words_from["all"])
# print ", ".join(all_words_from["nowhere"])
# print all_logs_dict
# exit()

### PART-OF-SPEECH ANALYSIS
# pos = [[u'ESPN', 1], [u'global', 1, u's'], [u'dish', 1, u'n'], [u'religious', 1, u'a'], [u'children', 1, u'n'], [u'issues', 1, u'n'], [u'Honda', 1], [u'environment', 1, u'n'], [u'supplies', 1, u'v'], [u'fatal', 1, u's'], [u'smartphone', 1], [u'Jeep', 1, u'n'], [u'Life tips', 1], [u'cook', 1, u'v'], [u'pbs', 1, u'n'], [u'companies', 1, u'n'], [u'democrat', 1, u'n'], [u'grandfather', 1, u'n'], [u'trench', 1, u'v'], [u'race', 2, u'n'], [u'drawings', 1, u'v'], [u'non-fiction', 1], [u'charter', 1, u'v'], [u'young adult', 1], [u'leaders', 1, u'n'], [u'Grandmother', 1, u'n'], [u'rate', 1, u'n'], [u'cost', 1, u'n'], [u'design', 1, u'v'], [u'plead', 2, u'v'], [u'patient', 1, u'n'], [u'abc', 1, u'n'], [u'saved', 1, u'v'], [u'asia', 1, u'n'], [u'Ford', 1, u'n'], [u'new', 2, u's'], [u'America', 1, u'n'], [u'real estate profiles', 1], [u'Peyton', 1], [u'Accomodation', 1], [u'hero', 1, u'n'], [u'NFL', 1], [u'french', 1, u'n'], [u'rangel', 1], [u'baseball', 5, u'n'], [u'ethanol', 1, u'n'], [u'tragedy', 1, u'n'], [u'voice', 1, u'n'], [u'square feet', 1], [u'alternative fuel', 1], [u'guilty', 1, u'a'], [u'CBS', 1], [u'social', 1, u'a'], [u'residents', 1, u'n'], [u'Audi', 1], [u'Peyton Manning', 1], [u'campaign', 2, u'n'], [u'transit', 1, u'v'], [u'africa', 1, u'n'], [u'mexican', 1, u'a'], [u'Health', 1, u'n'], [u'names', 1, u'v'], [u'congolese', 1, u'a'], [u'jurors', 1, u'n'], [u'auto industry', 1], [u'illegal', 1, u'a'], [u'destination', 1, u'n'], [u'sports', 3, u'n'], [u'best sellers', 1], [u'call', 1, u'v'], [u'candidates', 1, u'n'], [u'prep', 1, u'n'], [u'defendant', 1, u'n'], [u'green ', 1], [u'teen', 1, u's'], [u'club', 1, u'n'], [u'share', 1, u'v'], [u'freedom', 1, u'n'], [u'testified', 1, u'v'], [u'Grandfather', 1, u'n'], [u'train', 1, u'v'], [u'adult', 1, u's'], [u'baby', 1, u'n'], [u'charity', 1, u'n'], [u'room', 1, u'n'], [u'Family', 1, u'n'], [u'science', 1, u'n'], [u'cat', 1, u'n'], [u'reviews', 2, u'n'], [u'learn', 1, u'v'], [u'fla', 1], [u'trump', 1, u'v'], [u'tax', 2, u'v'], [u'agent', 2, u'n'], [u'the editor', 1], [u'ceremony', 1, u'n'], [u'information', 1, u'n'], [u'winter', 1, u'v'], [u'NHL', 1], [u'amazing', 1, u's'], [u'earnings', 1, u'v'], [u'free will', 1], [u'no-trump', 2, u'n'], [u'economy', 3, u'n'], [u'fare', 1, u'n'], [u'criminal', 2, u's'], [u'poker', 1, u'n'], [u'ABC', 2, u'n'], [u'beauty', 1, u'n'], [u'List', 1, u'v'], [u'president', 2, u'n'], [u'pleaded', 1, u'v'], [u'man', 1, u'n'], [u'coat', 1, u'v'], [u'Romney', 1], [u'lost', 1, u'v'], [u'uninsured', 1, u'a'], [u'Politics', 3, u'n'], [u'preventive ', 1], [u'mutual funds', 1], [u'wine', 1, u'v'], [u'ethnic food', 1], [u'rabbi', 1, u'n'], [u'wedding', 2, u'n'], [u'Misc.', 1], [u'cuts', 1, u'v'], [u'White', 1, u'n'], [u'Accord', 1, u'n'], [u'police', 1, u'v'], [u'minor league', 1], [u'listing', 1, u'v'], [u'policy', 1, u'n'], [u'holiday', 1, u'n'], [u'finance', 1, u'n'], [u'civilian', 1, u'a'], [u'prime minister', 1], [u'Mother', 1, u'n'], [u'republican', 1, u'n'], [u'presidential', 2, u'a'], [u'Flavor', 1, u'n'], [u'meal', 1, u'n'], [u'financial', 1, u'a'], [u'suspended', 1, u'v'], [u'city service', 1], [u'science and nature', 1], [u'Sports', 1, u'n'], [u'year', 1, u'n'], [u'hostel', 1, u'n'], [u'prewar', 1, u'a'], [u'profit', 2, u'v'], [u'winter escape', 1], [u'motel', 1, u'n'], [u'testify', 2, u'v'], [u'BMW', 1], [u'architecture', 1, u'n'], [u'Theater', 1, u'n'], [u'contract terms', 1], [u'struggle', 1, u'v'], [u'plea', 1, u'n'], [u'Corrections', 2, u'n'], [u'Opinion', 1, u'n'], [u'care', 1, u'n'], [u'listings', 1, u'v'], [u'trump no-trump', 1], [u'american', 2, u'n'], [u'residential sales', 1], [u'homelessness', 1, u'n'], [u'corrections', 2, u'n'], [u'Obituary', 1, u'n'], [u'major', 1, u'a'], [u'superbowl', 1], [u'pork', 2, u'n'], [u'delicious', 1, u's'], [u'spanish', 1, u'n'], [u'fiction', 1, u'n'], [u'gourmet', 1, u'n'], [u'Sorrow', 1, u'n'], [u'system', 1, u'n'], [u'relations', 2, u'n'], [u'Sorror', 1], [u'attack', 1, u'n'], [u'new york', 1], [u'convention', 1, u'n'], [u'palestine', 2, u'n'], [u'finances', 1, u'n'], [u'murder', 1, u'v'], [u'obama', 1], [u'Love', 1, u'n'], [u'warfare', 1, u'n'], [u'players contracts', 1], [u'stock market', 1], [u'New York', 3], [u'Local News', 1], [u'cards', 1, u'n'], [u'sculpture', 2, u'v'], [u'russia', 1, u'n'], [u'exhibit', 1, u'v'], [u'bridge', 1, u'n'], [u'fashion', 1, u'n'], [u'Chicago', 1, u'n'], [u'correction', 1, u'n'], [u'Father', 1, u'n'], [u'style', 1, u'n'], [u'rent', 2, u'v'], [u'Announcements', 1, u'n'], [u'ratings', 1, u'v'], [u'Christian', 1, u'a'], [u'veteran', 1, u'n'], [u'stuggle', 1], [u'online', 1, u'a'], [u'interior', 2, u's'], [u'performance', 1, u'n'], [u'MLB', 1], [u'mileage', 1, u'n'], [u'price', 1, u'n'], [u'banks', 1, u'n'], [u'middle east', 2], [u'letter', 1, u'n'], [u'GOP', 1, u'n'], [u'cellphone', 1, u'n'], [u'mobile', 1, u's'], [u'sale', 1, u'n'], [u'national league', 2], [u'federal', 1, u'a'], [u'points', 1, u'n'], [u'Election', 1, u'n'], [u'golf', 1, u'v'], [u'show', 2, u'v'], [u'queen', 1, u'n'], [u'recipe', 1, u'n'], [u'democrats', 1, u'n'], [u'bedroom', 1, u'n'], [u'earth', 1, u'n'], [u'chicken', 1, u'n'], [u'bail', 1, u'v'], [u'decade', 1, u'n'], [u'winner', 1, u'n'], [u'crime', 2, u'n'], [u'black', 1, u's'], [u'hockey', 2, u'n'], [u'The Neediest Cases', 1], [u'photographs', 1, u'v'], [u'ranking', 1, u'v'], [u'hungarian', 1, u'n'], [u'Wife', 1, u'n'], [u'photography', 1, u'n'], [u'F.A.A>', 1], [u'Bridegroom', 1, u'n'], [u'international', 1, u'a'], [u'buyer', 1, u'n'], [u'F.A.A.', 2], [u'furnishings', 1, u'n'], [u'shopping', 3, u'v'], [u'married', 2, u'a'], [u'amputation', 1, u'n'], [u'taxes', 1, u'v'], [u"children's", 1], [u'juror', 1, u'n'], [u'Broadway', 1, u'n'], [u'freedin', 1], [u'oarty', 1], [u'Ratings', 1, u'v'], [u'art news', 1], [u'fair', 1, u's'], [u'climate change', 1], [u'accused', 1, u'v'], [u'college', 1, u'n'], [u'sea', 1, u'n'], [u'jobs', 2, u'n'], [u'calendar', 1, u'n'], [u'best', 1, u's'], [u'trump ', 1], [u'Critics', 1, u'n'], [u'nuclear', 1, u'a'], [u'grandmother', 1, u'n'], [u'PC', 1, u'n'], [u'Q & A', 1], [u'pets', 2, u'n'], [u'diamonds', 3, u'n'], [u'spade club hearts', 1], [u'paster', 1, u'n'], [u'europe', 1, u'n'], [u'notice', 1, u'n'], [u'terms', 1, u'n'], [u'parent', 1, u'n'], [u'vitamin', 1, u'n'], [u'efficiency', 1, u'n'], [u'awards', 2, u'n'], [u'news', 2, u'n'], [u'lawsuit', 1, u'n'], [u'Eli Manning', 1], [u'climate', 1, u'n'], [u'accident', 1, u'n'], [u'country', 1, u'n'], [u'drug', 1, u'v'], [u'briefing', 1, u'v'], [u'Playoff', 1, u'n'], [u'games', 1, u'n'], [u'china', 1, u'n'], [u'grooming', 1, u'v'], [u'traded', 1, u'v'], [u'Advice', 1, u'n'], [u'negotiation', 1, u'n'], [u'non green', 1], [u'Death', 1, u'n'], [u'community', 1, u'n'], [u'medication', 1, u'n'], [u'church', 4, u'n'], [u'Disney', 1, u'n'], [u'speak', 1, u'v'], [u'best seller', 1], [u'elected officials', 1], [u'vacation', 1, u'n'], [u'strategy', 2, u'n'], [u'convicted', 1, u'v'], [u'Cathollic', 1], [u'Obituaries', 1, u'n'], [u'interest', 1, u'n'], [u'transportation', 2, u'n'], [u'gay', 1, u's'], [u'Poland', 1, u'n'], [u'gas', 1, u'n'], [u'Nations', 1, u'n'], [u'child', 1, u'n'], [u'CW', 1], [u'case', 1, u'n'], [u'novel', 1, u's'], [u'politician', 1, u'n'], [u'health care', 1], [u'value', 1, u'n'], [u'Obituary ', 1], [u'newspaper', 1, u'n'], [u'cats', 1, u'n'], [u'property', 2, u'n'], [u'player', 2, u'n'], [u'stock prices', 1], [u'technology', 1, u'n'], [u'obituary', 1, u'n'], [u'memorial', 1, u'n'], [u'death penalty', 1], [u'home sales', 1], [u'Fiesta', 1, u'n'], [u'party', 1, u'n'], [u'events', 1, u'n'], [u'closings', 1, u'v'], [u'mutual', 1, u'a'], [u'global warming', 1], [u'hand', 1, u'n'], [u'cleaning', 1, u'v'], [u'textile art', 1], [u'major league baseball', 1], [u'President', 2, u'n'], [u'transaction', 1, u'n'], [u'ocean', 1, u'n'], [u'costs', 1, u'n'], [u'american league', 2], [u'mother', 3, u'n'], [u'hearts', 2, u'n'], [u'audio', 1, u'n'], [u'summer', 1, u'n'], [u'United', 1, u'v'], [u'sentence', 1, u'n'], [u'money', 2, u'n'], [u'laptop', 1, u'n'], [u'domestic', 1, u'a'], [u'victim', 1, u'n'], [u'apple', 1, u'n'], [u'death', 2, u'n'], [u'family', 1, u'n'], [u'diagramed deal', 1], [u'residential', 2, u'a'], [u'workers', 1, u'n'], [u'demographic', 1, u'a'], [u'Holidays', 1, u'n'], [u'parents', 1, u'n'], [u'exhibition', 1, u'n'], [u'municipal', 1, u'a'], [u'government', 3, u'n'], [u'couple', 1, u'n'], [u'game', 1, u'n'], [u'Chrysler', 1], [u'jobs ', 1], [u'Martin Luther King', 1], [u'offices', 1, u'n'], [u'Operation', 1, u'n'], [u'antique', 1, u's'], [u'old', 1, u's'], [u'deal', 2, u'v'], [u'people', 1, u'n'], [u'Social Policy', 1], [u'dead', 5, u's'], [u'Neediest Cases', 1], [u'economic', 2, u's'], [u'election', 1, u'n'], [u'home', 1, u'n'], [u'sentenced', 1, u'v'], [u'caribbean', 1, u'n'], [u'folk art', 1], [u'decision', 1, u'n'], [u'seller', 2, u'n'], [u'religion', 1, u'n'], [u'temple', 1, u'n'], [u'School', 1, u'n'], [u'Interaction', 1, u'n'], [u'Lifestyle', 1, u'n'], [u'business', 1, u'n'], [u'schedule', 1, u'v'], [u'Groom', 1, u'v'], [u'Bride ', 1], [u'faith', 1, u'n'], [u'island', 1, u'n'], [u'postwar', 1, u'a'], [u'violence', 1, u'n'], [u'drama', 1, u'n'], [u'eastern europe', 1], [u'militia', 1, u'n'], [u'testimony', 1, u'n'], [u'Best', 1, u's'], [u'Eli', 1], [u'clinton', 1, u'n'], [u'civil', 1, u'a'], [u'son', 1, u'n'], [u'united states', 1], [u'homeless', 1, u's'], [u'dean', 1, u'n'], [u'development league', 2], [u'alleged', 1, u's'], [u'Birthday', 1, u'n'], [u'editor', 2, u'n'], [u'Baseball', 1, u'n'], [u'NBA', 1], [u'war', 1, u'n'], [u'Obama', 1], [u'jury', 2, u'n'], [u'dummy', 1, u'n'], [u'Civil Rights', 1], [u'American people', 1], [u'gain', 1, u'v'], [u'holiday office closings', 1], [u'Coughlin', 1], [u'House', 1, u'n'], [u'clubs', 3, u'n'], [u'signed', 1, u'v'], [u'prosecutor', 1, u'n'], [u'display', 1, u'n'], [u'real estate transactions', 1], [u"ABC's", 1, u'n'], [u'tournament', 1, u'n'], [u'sales', 3, u'n'], [u'evidence', 1, u'v'], [u'cbs', 2], [u'health insurance', 1], [u'politics', 5, u'n'], [u'shooting', 1, u'v'], [u'casualty', 1, u'n'], [u'nj', 1, u'n'], [u'lemon', 1, u'n'], [u'card game', 1], [u'Poker', 1, u'n'], [u'diet', 1, u'n'], [u'stocks', 2, u'n'], [u'spades', 3, u'n'], [u'dog', 1, u'n'], [u'2008', 1], [u'Shooting', 1, u'v'], [u'prizes', 1, u'v']]
# with open("dataset/linguistic_analysis_of_words/add_words_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)
# pos_codes = {'a':"ADJ", 's':"ADJ_SAT", 'r':"ADV", 'n':"NOUN", 'v':"VERB"}
# missing_pos = [p for p in pos if len(p)==2]
# print missing_pos
# freq_pos = {pos_codes[tag]:sum([p[1] for p in pos if len(p)==3 and p[2]==tag]) for tag in [u'a', u's', u'r', u'n', u'v']}
# print freq_pos
# exit()

# pos = [(u'chinese', 1, u'a'), (u'issues', 1, u'n'), (u'fatal', 1, u's'), (u'risk', 1, u'n'), (u'Life tips', 1), (u'cook', 1, u'v'), (u'Q & A', 1), (u'school', 1, u'n'), (u'democrat', 1, u'n'), (u'trench', 1, u'v'), (u'charter', 1, u'v'), (u'chef', 1, u'n'), (u'governor', 1, u'n'), (u'plead', 1, u'v'), (u'international', 1, u'a'), (u'public', 1, u'n'), (u'rangel', 1), (u'water', 1, u'n'), (u'employees', 1, u'n'), (u'advertising', 1, u'v'), (u'published', 1, u'v'), (u'apple', 1, u'n'), (u'county', 1, u'n'), (u'Football Teams', 1), (u'palestinian', 1, u'a'), (u'music', 1, u'n'), (u'teen', 1, u's'), (u'chocolate', 1, u'n'), (u'adult', 1, u's'), (u'estate', 1, u'n'), (u'tax', 1, u'v'), (u'amazing', 1, u's'), (u'stock', 1, u'n'), (u'plant', 1, u'v'), (u'building', 1, u'v'), (u'F.A.A>', 1), (u'nets', 1, u'n'), (u'sauce', 1, u'v'), (u'Flavor', 1, u'n'), (u'economy', 1, u'n'), (u'meal', 1, u'n'), (u'fish', 1, u'n'), (u'Sports', 1, u'n'), (u'books', 1, u'n'), (u'event', 1, u'n'), (u'beauty', 1, u'n'), (u'profit', 1, u'v'), (u'god', 1, u'n'), (u'testify', 1, u'v'), (u'shows', 1, u'v'), (u'cars', 1, u'n'), (u'Corrections', 1, u'n'), (u'Opinion', 1, u'n'), (u'listings', 1, u'v'), (u'trump no-trump', 1), (u'origin', 1, u'n'), (u'cheese', 1, u'v'), (u'superbowl', 1), (u'story', 1, u'n'), (u'gourmet', 1, u'n'), (u'Sorror', 1), (u'listed', 1, u'v'), (u'convention', 1, u'n'), (u'finances', 1, u'n'), (u'season', 1, u'v'), (u'television', 1, u'n'), (u'warfare', 1, u'n'), (u'project', 1, u'v'), (u'fashion', 1, u'n'), (u'Announcements', 1, u'n'), (u'Christian', 1, u'a'), (u'snow', 1, u'n'), (u'dining', 1, u'v'), (u'chairman', 1, u'v'), (u'forces', 1, u'n'), (u'performance', 1, u'n'), (u'price', 1, u'n'), (u'Cathollic', 1), (u'brooklyn', 1, u'n'), (u'Critics', 1, u'n'), (u'points', 1, u'n'), (u'painting', 1, u'v'), (u'golf', 1, u'v'), (u'show', 1, u'v'), (u'knicks', 1), (u'crime', 1, u'n'), (u'fuel', 1, u'v'), (u'communist', 1, u'n'), (u'local', 1, u'a'), (u'giants', 1, u'n'), (u'sunni', 1, u'n'), (u'bar', 1, u'n'), (u'married', 1, u'a'), (u'juror', 1, u'n'), (u'freedin', 1), (u'husband', 1, u'v'), (u'national', 1, u'a'), (u'college', 1, u'n'), (u'israeli', 1, u'a'), (u'sites', 1, u'v'), (u'spade club hearts', 1), (u'parent', 1, u'n'), (u'vitamin', 1, u'n'), (u'league', 1, u'n'), (u'restaurant', 1, u'n'), (u'contract', 1, u'v'), (u'foreign', 1, u'a'), (u'bronx', 1, u'n'), (u'senator', 1, u'n'), (u'Disney', 1, u'n'), (u'airlines', 1, u'n'), (u'shopping', 1, u'v'), (u'drugs', 1, u'v'), (u'minister', 1, u'n'), (u'politician', 1, u'n'), (u'property types', 1), (u'air', 1, u'n'), (u'Obituary ', 1), (u'technology', 1, u'n'), (u'european', 1, u'a'), (u'development', 1, u'n'), (u'lawyers', 1, u'n'), (u'costs', 1, u'n'), (u'researchers', 1, u'n'), (u'stores', 1, u'n'), (u'money', 1, u'n'), (u'municipal', 1, u'a'), (u'government', 1, u'n'), (u'judge', 1, u'v'), (u'dean', 1, u'n'), (u'hair', 1, u'n'), (u'Neediest Cases', 1), (u'growth', 1, u'n'), (u'election', 1, u'n'), (u'home', 1, u'n'), (u'legal', 1, u'a'), (u'business', 1, u'n'), (u'quarter', 1, u'n'), (u'dinner', 1, u'n'), (u'travelers', 1, u'n'), (u'attorney', 1, u'n'), (u'son', 1, u'n'), (u'weather', 1, u'v'), (u'old', 1, u's'), (u'alleged', 1, u's'), (u'sales', 1, u'n'), (u'health insurance', 1), (u'cream', 1, u'v'), (u'book', 1, u'n'), (u'congress', 1, u'n'), (u'students', 1, u'n'), (u'stocks', 1, u'n'), (u'friends', 1, u'n'), (u'ice', 2, u'n'), (u'holocaust', 2, u'n'), (u'lawyer', 2, u'n'), (u'nbc', 2), (u'change', 2, u'v'), (u'daughter', 2, u'n'), (u'patriots', 2, u'n'), (u'glass', 2, u'n'), (u'history', 2, u'n'), (u'winter', 2, u'v'), (u'comedy', 2, u'n'), (u'man', 2, u'n'), (u'democratic', 2, u'a'), (u'wine', 2, u'v'), (u'committee', 2, u'n'), (u'mayor', 2, u'n'), (u'writing', 2, u'v'), (u'mail', 2, u'n'), (u'financial', 2, u'a'), (u'red', 2, u'n'), (u'doctors', 2, u'n'), (u'marriage', 2, u'n'), (u'quarterback', 2, u'n'), (u'nuclear', 2, u'a'), (u'agreed', 2, u'v'), (u'black', 2, u's'), (u'restaurants', 2, u'n'), (u'movie', 2, u'n'), (u'won', 2, u'v'), (u'notice', 2, u'n'), (u'terms', 2, u'n'), (u'jets', 2, u'n'), (u'players', 2, u'n'), (u'jersey', 2, u'n'), (u'arts', 2, u'n'), (u'firm', 2, u's'), (u'plants', 2, u'v'), (u'budget', 2, u'n'), (u'middle', 2, u'n'), (u'pay', 2, u'v'), (u'administration', 2, u'n'), (u'student', 2, u'n'), (u'colts', 2, u'n'), (u'recent', 2, u's'), (u'iraqis', 2, u'n'), (u'mother', 2, u'n'), (u'soviet', 2, u'a'), (u'schools', 2, u'n'), (u'workers', 2, u'n'), (u'viewers', 2, u'n'), (u'ski', 2, u'v'), (u'test', 2, u'v'), (u'jews', 2, u'n'), (u'deal', 2, u'v'), (u'fox', 2, u'n'), (u'island', 2, u'n'), (u'executives', 2, u'n'), (u'editor', 2, u'n'), (u'jewish', 2, u'a'), (u'funds', 2, u'v'), (u'pastor', 2, u'n'), (u'line', 2, u'n'), (u'campus', 2, u'n'), (u'died', 2, u'v'), (u'apartment', 3, u'n'), (u'father', 3, u'n'), (u'program', 3, u'n'), (u'blue', 3, u's'), (u'paintings', 3, u'v'), (u'french', 3, u'n'), (u'kids', 3, u'n'), (u'residents', 3, u'n'), (u'named', 3, u'v'), (u'market', 3, u'n'), (u'hospital', 3, u'n'), (u'loving', 3, u'v'), (u'israel', 3, u'n'), (u'room', 3, u'n'), (u'movies', 3, u'n'), (u'january', 3, u'n'), (u'law', 3, u'n'), (u'green', 3, u'n'), (u'bowl', 3, u'n'), (u'bank', 3, u'n'), (u'meat', 3, u'n'), (u'square', 3, u'v'), (u'research', 3, u'v'), (u'free', 3, u'v'), (u'corrections', 3, u'n'), (u'number', 3, u'n'), (u'service', 3, u'n'), (u'system', 3, u'n'), (u'hollywood', 3, u'n'), (u'park', 3, u'n'), (u'bears', 3, u'v'), (u'correction', 3, u'n'), (u'mountain', 3, u'n'), (u'america', 3, u'n'), (u'professor', 3, u'n'), (u'democrats', 3, u'n'), (u'earth', 3, u'n'), (u'office', 3, u'n'), (u'writes', 3, u'v'), (u'trees', 3, u'v'), (u'federal', 3, u'a'), (u'church', 3, u'n'), (u'left', 3, u'v'), (u'parents', 3, u'n'), (u'beloved', 3, u's'), (u'game', 3, u'n'), (u'works', 3, u'v'), (u'clinton', 3, u'n'), (u'survived', 3, u'v'), (u'film', 3, u'n'), (u'department', 3, u'n'), (u'billion', 3, u'n'), (u'wife', 3, u'n'), (u'coach', 4, u'n'), (u'children', 4, u'n'), (u'brown', 4, u'n'), (u'louis', 4, u'n'), (u'team', 4, u'n'), (u'small', 4, u's'), (u'told', 4, u'v'), (u'men', 4, u'n'), (u'family', 4, u'n'), (u'played', 4, u'v'), (u'films', 4, u'n'), (u'baby', 4, u'n'), (u'town', 4, u'n'), (u'player', 4, u'n'), (u'write', 4, u'v'), (u'light', 4, u's'), (u'things', 4, u'n'), (u'playing', 4, u'v'), (u'brain', 4, u'n'), (u'food', 4, u'n'), (u'foot', 4, u'n'), (u'day', 4, u'n'), (u'wines', 4, u'v'), (u'american', 4, u'n'), (u'wrote', 4, u'v'), (u'secretary', 4, u'n'), (u'city', 4, u'n'), (u'cost', 4, u'n'), (u'paid', 4, u'v'), (u'plan', 4, u'v'), (u'radio', 4, u'n'), (u'written', 4, u'v'), (u'teams', 4, u'n'), (u'miles', 4, u'n'), (u'article', 4, u'n'), (u'secret', 4, u's'), (u'republicans', 4, u'n'), (u'fund', 4, u'v'), (u'child', 4, u'n'), (u'prices', 4, u'n'), (u'field', 4, u'n'), (u'maliki', 4), (u'super', 4, u's'), (u'woman', 5, u'n'), (u'great', 5, u's'), (u'united', 5, u'v'), (u'end', 5, u'n'), (u'spitzer', 5), (u'johnson', 5, u'n'), (u'producer', 5, u'n'), (u'late', 5, u's'), (u'weeks', 5, u'n'), (u'james', 5, u'n'), (u'care', 5, u'n'), (u'david', 5, u'n'), (u'thing', 5, u'n'), (u'king', 5, u'n'), (u'countries', 5, u'n'), (u'sex', 5, u'n'), (u'harvard', 5, u'n'), (u'country', 5, u'n'), (u'anti', 5, u'a'), (u'gay', 5, u's'), (u'director', 5, u'n'), (u'artists', 5, u'n'), (u'war', 5, u'n'), (u'misstated', 5, u'v'), (u'carter', 6, u'n'), (u'makes', 6, u'v'), (u'club', 6, u'n'), (u'company', 6, u'n'), (u'making', 6, u'v'), (u'states', 6, u'n'), (u'times', 6, u'n'), (u'found', 6, u'v'), (u'williams', 6, u'n'), (u'san', 6), (u'thomas', 6, u'n'), (u'kind', 6, u's'), (u'bad', 6, u's'), (u'ohio', 6, u'n'), (u'manning', 6, u'v'), (u'jr', 6, u'n'), (u'political', 6, u'a'), (u'ago', 6, u's'), (u'tex', 7), (u'women', 7, u'n'), (u'high', 7, u'n'), (u'half', 7, u's'), (u'house', 7, u'n'), (u'calif', 7, u'n'), (u'major', 7, u'a'), (u'tonight', 7, u'r'), (u'wilson', 7, u'n'), (u'foxman', 7), (u'added', 7, u'v'), (u'officials', 7, u'n'), (u'games', 7, u'n'), (u'al', 7, u'n'), (u'yesterday', 7, u'r'), (u'east', 7, u'n'), (u'www', 7, u'n'), (u'called', 7, u'v'), (u'ny', 7, u'n'), (u'simon', 8, u'n'), (u'baseball', 8, u'n'), (u'work', 8, u'v'), (u'abortion', 8, u'n'), (u'good', 8, u's'), (u'university', 8, u'n'), (u'white', 8, u'n'), (u'play', 8, u'v'), (u'state', 8, u'n'), (u'asked', 8, u'v'), (u'life', 8, u'n'), (u'death', 8, u'n'), (u'real', 8, u's'), (u'long', 8, u'a'), (u'mailer', 8, u'n'), (u'minutes', 8, u'n'), (u'companies', 9, u'n'), (u'vez', 9), (u'put', 9, u'v'), (u'including', 9, u'v'), (u'space', 9, u'n'), (u'avenue', 9, u'n'), (u'ch', 9), (u'century', 9, u'n'), (u'party', 9, u'n'), (u'doesn', 9), (u'president', 10, u'n'), (u'make', 10, u'v'), (u'made', 10, u'v'), (u'part', 11, u'n'), (u'west', 11, u'n'), (u'center', 11, u'n'), (u'world', 12, u'n'), (u'back', 12, u'v'), (u'percent', 12, u'n'), (u'time', 12, u'n'), (u'st', 13), (u'john', 14, u'n'), (u'night', 14, u'n'), (u'years', 16, u'n'), (u'people', 17, u'n'), (u'jan', 19, u'n'), (u'street', 22, u'n'), (u'million', 22, u'n'), (u'york', 32, u'n'), (u'year', 42, u'n')]
# with open("dataset/linguistic_analysis_of_words/remove_words_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)
# exit()

# pos = [(u'', 5), (u' travel[travel', 3), (u'chinese', 2, u'a'), (u'global', 1, u's'), (u' hotel]', 15), (u'ice', 6, u'n'), (u'event[show', 1), (u'children', 3, u'n'), (u'apartment', 2, u'n'), (u'father', 9, u'n'), (u'iraqi', 2, u'a'), (u'brown', 3, u'n'), (u'risk', 2, u'n'), (u' father', 1), (u' building]', 1), (u' movies', 1), (u'school', 2, u'n'), (u'pbs', 1, u'n'), (u'louis', 2, u'n'), (u'companies', 4, u'n'), (u'democrat', 2, u'n'), (u' service', 1), (u'pork', 2, u'n'), (u'country[country', 1), (u'holocaust', 3, u'n'), (u'tex', 2), (u' bathrooms]', 1), (u'cost', 1, u'n'), (u'video', 1, u'n'), (u'lawyer', 6, u'n'), (u'plead', 1, u'v'), (u'nbc', 3), (u'investment', 1, u'n'), (u'blue', 4, u's'), (u'abc', 1, u'n'), (u'paintings', 3, u'v'), (u'new', 1, u's'), (u'Peyton', 1), (u'transportation', 1, u'n'), (u'funeral', 1, u'n'), (u'men', 1, u'n'), (u'french', 5, u'n'), (u'water', 2, u'n'), (u'baseball', 2, u'n'), (u'ethanol', 2, u'n'), (u'iraq', 2, u'n'), (u'tragedy', 1, u'n'), (u'change', 1, u'v'), (u' calif', 1), (u'great', 1, u's'), (u'kids', 2, u'n'), (u'daughter', 3, u'n'), (u'employees', 1, u'n'), (u'trial', 3, u'n'), (u'airport', 1, u'n'), (u'military', 6, u'a'), (u'residents', 3, u'n'), (u'apple', 7, u'n'), (u'family', 8, u'n'), (u'county', 1, u'n'), (u' husband', 1), (u'patriots', 6, u'n'), (u'congolese', 1, u'a'), (u'market', 2, u'n'), (u'troops', 7, u'n'), (u'army', 2, u'n'), (u'music', 1, u'n'), (u'films', 4, u'n'), (u' beach[airlines', 1), (u'green ', 1), (u'israel', 3, u'n'), (u'company', 6, u'n'), (u'chocolate', 2, u'n'), (u'entertainment[film', 1), (u'train', 1, u'v'), (u'baby', 2, u'n'), (u'cases', 2, u'n'), (u'earth', 2, u'n'), (u'women', 1, u'n'), (u'room', 2, u'n'), (u'car', 1, u'n'), (u'movies', 4, u'n'), (u'making', 1, u'v'), (u'history', 4, u'n'), (u'giants', 7, u'n'), (u'president', 9, u'n'), (u'trump', 3, u'v'), (u'estate', 5, u'n'), (u'tax', 1, u'v'), (u' contract', 3), (u'states', 5, u'n'), (u'travel[airlines', 1), (u'the editor', 1), (u'united', 4, u'v'), (u'end', 2, u'n'), (u'winter', 6, u'v'), (u'january', 2, u'n'), (u'NHL', 1), (u'travel', 6, u'v'), (u'write', 2, u'v'), (u'travel[travelers', 1), (u'comedy', 2, u'n'), (u'beach', 2, u'v'), (u' insurance', 1), (u'stock', 1, u'n'), (u'plant', 1, u'v'), (u'ABC', 2, u'n'), (u'spitzer', 1), (u' movie', 1), (u'court', 4, u'n'), (u'pleaded', 1, u'v'), (u'law', 2, u'n'), (u'man', 1, u'n'), (u'johnson', 3, u'n'), (u'st', 2), (u'chief', 5, u'n'), (u'green', 4, u'n'), (u'democratic', 1, u'a'), (u'wine', 1, u'v'), (u' building', 1), (u'mexican', 1, u'a'), (u'producer', 1, u'n'), (u'cheese', 2, u'v'), (u'years', 5, u'n'), (u'New YOrk[york', 1), (u' king]', 1), (u' marriage', 1), (u'White', 1, u'n'), (u'nets', 1, u'n'), (u'mayor', 1, u'n'), (u'Health Care[health', 1), (u'police', 1, u'v'), (u' pork]', 1), (u'minor league', 1), (u'writing', 3, u'v'), (u'late', 2, u's'), (u'resort', 2, u'n'), (u'production', 1, u'n'), (u'listing', 1, u'v'), (u'mail', 1, u'n'), (u'film[film', 2), (u'sauce', 1, u'v'), (u'phone', 1, u'n'), (u'postwar', 1, u'a'), (u'prime minister', 1), (u'half', 1, u's'), (u'schools', 2, u'n'), (u'republican', 2, u'n'), (u' comedy', 1), (u'day', 1, u'n'), (u'viewers', 2, u'n'), (u'meat', 1, u'n'), (u'james', 3, u'n'), (u'university', 1, u'n'), (u'countries', 4, u'n'), (u'found', 1, u'v'), (u'quarter', 1, u'n'), (u' countries]', 1), (u'square', 4, u'v'), (u'billion', 1, u'n'), (u' phone]', 1), (u'house', 6, u'n'), (u'fish', 2, u'n'), (u'science and nature', 1), (u' st', 1), (u'books', 1, u'n'), (u'year', 6, u'n'), (u'property types[house', 1), (u'insurance', 3, u'n'), (u'prewar', 1, u'a'), (u'space', 2, u'n'), (u'god', 1, u'n'), (u' fox', 1), (u'testify', 1, u'v'), (u'research', 1, u'v'), (u'health', 4, u'n'), (u'internet', 4, u'n'), (u'calif', 3, u'n'), (u'red', 4, u'n'), (u'shows', 2, u'v'), (u'wines', 1, u'v'), (u'million', 5, u'n'), (u'york', 5, u'n'), (u'plea', 1, u'n'), (u'care', 3, u'n'), (u'david', 3, u'n'), (u'american', 6, u'n'), (u'husband', 4, u'v'), (u'corrections', 1, u'n'), (u'hussein', 1, u'n'), (u'secretary', 1, u'n'), (u'Editor[editor', 2), (u'Obituary', 1, u'n'), (u'major', 2, u'a'), (u' country', 1), (u'number', 2, u'n'), (u'spanish', 1, u'n'), (u'city', 3, u'n'), (u'management', 4, u'n'), (u'service', 1, u'n'), (u'bears', 4, u'v'), (u'system', 2, u'n'), (u'designer', 1, u'n'), (u' family]', 1), (u'palestine', 1, u'n'), (u'hollywood', 1, u'n'), (u'john', 2, u'n'), (u'williams', 2, u'n'), (u'listed', 2, u'v'), (u'software', 2, u'n'), (u'season', 1, u'v'), (u'hotel', 4, u'n'), (u'park', 2, u'n'), (u'environmental', 1, u'a'), (u'white', 4, u'n'), (u'obama', 1), (u'king', 3, u'n'), (u'television', 1, u'n'), (u'nations', 5, u'n'), (u'project', 1, u'v'), (u'street', 5, u'n'), (u'marriage', 3, u'n'), (u'store', 1, u'n'), (u'design', 1, u'v'), (u'sculpture', 1, u'v'), (u'russia', 3, u'n'), (u'san', 2), (u'investors', 1, u'n'), (u'correction', 1, u'n'), (u'glass', 1, u'n'), (u' ago]', 3), (u'mountain', 2, u'n'), (u'landmarks[street', 1), (u'snow', 7, u'n'), (u'chairman', 5, u'v'), (u'forces', 2, u'n'), (u'online', 4, u'a'), (u'quarterback', 1, u'n'), (u'added', 1, u'v'), (u'price', 3, u'n'), (u'paid', 4, u'v'), (u'pastor', 2, u'n'), (u'brooklyn', 3, u'n'), (u'location[ohio', 1), (u'plan', 1, u'v'), (u' mail', 1), (u'america', 1, u'n'), (u'gallery', 3, u'n'), (u'medical', 1, u'a'), (u'national league', 2), (u'neediest', 2, u's'), (u' fox]', 1), (u'movie', 5, u'n'), (u'painting', 2, u'v'), (u'microsoft', 7), (u'thomas', 2, u'n'), (u'show', 5, u'v'), (u'agreed', 2, u'v'), (u'radio', 1, u'n'), (u'democrats', 2, u'n'), (u'bedroom', 4, u'n'), (u'soldiers', 2, u'n'), (u'chicken', 3, u'n'), (u'time[time', 1), (u'networks[abc', 1), (u'knicks', 1), (u'justice', 2, u'n'), (u'writes', 3, u'v'), (u'Marriages[mother', 1), (u'state', 1, u'n'), (u'bush', 1, u'n'), (u'black', 4, u's'), (u'hockey', 1, u'n'), (u'communist', 1, u'n'), (u'local', 2, u'a'), (u'photographs', 1, u'v'), (u'hungarian', 1, u'n'), (u'no-trump', 1, u'n'), (u'trees', 2, u'v'), (u' resort', 15), (u' shows]', 1), (u'sunni', 3, u'n'), (u'bar', 1, u'n'), (u'artist', 2, u'n'), (u'married', 4, u'a'), (u' park', 1), (u'taxes', 1, u'v'), (u'miles', 1, u'n'), (u'ohio', 3, u'n'), (u'told', 1, u'v'), (u'wrote', 2, u'v'), (u'restaurants', 1, u'n'), (u' television', 1), (u'art', 3, u'n'), (u'fair', 2, u's'), (u'national', 1, u'a'), (u' films]', 2), (u'manning', 1, u'v'), (u'officials', 2, u'n'), (u'college', 1, u'n'), (u'jury', 1, u'n'), (u'israeli', 3, u'a'), (u'computer', 2, u'n'), (u' airport[travelers', 7), (u'federal', 1, u'a'), (u'nuclear', 1, u'a'), (u'sites', 2, u'v'), (u'case', 3, u'n'), (u'written', 3, u'v'), (u' cbs', 1), (u'diamonds', 2, u'n'), (u'shiite', 2, u'n'), (u'notice', 7, u'n'), (u'terms', 3, u'n'), (u'jr', 3, u'n'), (u' sites', 1), (u'jets', 8, u'n'), (u'league', 3, u'n'), (u'climate', 1, u'n'), (u'restaurant', 1, u'n'), (u'country', 4, u'n'), (u' estate', 1), (u'contract', 2, u'v'), (u'foreign', 3, u'a'), (u'players', 1, u'n'), (u'games', 4, u'n'), (u'bronx', 3, u'n'), (u'senator', 3, u'n'), (u' san]', 1), (u' pbs', 1), (u'community', 2, u'n'), (u'anti', 1, u'a'), (u'vacation[ski', 1), (u'speak', 1, u'v'), (u'arts', 1, u'n'), (u'political', 3, u'a'), (u'airlines', 2, u'n'), (u' nbc', 2), (u'secret', 1, u's'), (u'Obituaries', 1, u'n'), (u'exhibition', 4, u'n'), (u'wine[wine', 1), (u' web', 1), (u' plan]', 1), (u'meat[chicken', 1), (u'family[wife', 1), (u'gas', 2, u'n'), (u'palestinian', 3, u'a'), (u'Nations', 1, u'n'), (u'fund', 1, u'v'), (u'minister', 4, u'n'), (u'child', 2, u'n'), (u'prices', 2, u'n'), (u'CW', 1), (u'weeks', 1, u'n'), (u'plants', 1, u'v'), (u' community]', 1), (u'budget', 2, u'n'), (u'air', 2, u'n'), (u'phone and other services[radio', 1), (u'voice', 1, u'n'), (u'study', 3, u'n'), (u'bathrooms', 4, u'n'), (u'century', 2, u'n'), (u'site', 2, u'n'), (u'player', 1, u'n'), (u'drug', 1, u'v'), (u'property', 1, u'n'), (u'technology', 1, u'n'), (u'memorial', 4, u'n'), (u'CBS', 1), (u'pay', 1, u'v'), (u'make', 2, u'v'), (u'bowl', 1, u'n'), (u'economy', 1, u'n'), (u'party', 1, u'n'), (u'european', 2, u'a'), (u'development', 1, u'n'), (u'lawyers', 6, u'n'), (u'director', 6, u'n'), (u'people[people', 1), (u'student', 4, u'n'), (u' hollywood', 1), (u'colts', 5, u'n'), (u'recent', 1, u's'), (u'center', 1, u'n'), (u'iraqis', 2, u'n'), (u' director', 1), (u'www[online', 1), (u'china', 4, u'n'), (u'american league', 2), (u'mother', 3, u'n'), (u'hearts', 2, u'n'), (u'researchers', 2, u'n'), (u'United', 1, u'v'), (u'stores', 1, u'n'), (u'money', 3, u'n'), (u' louis', 1), (u'executive', 7, u'n'), (u' exhibition]', 1), (u'foot', 3, u'n'), (u' time', 3), (u'Transactions[terms', 1), (u'web', 4, u'n'), (u'death', 2, u'n'), (u'travel[travel', 1), (u' producer', 1), (u' series', 1), (u'workers', 1, u'n'), (u'parents', 2, u'n'), (u'board', 2, u'n'), (u'beloved', 2, u's'), (u'ski', 1, u'v'), (u'real', 4, u's'), (u'government', 1, u'n'), (u'board[board', 1), (u'game', 4, u'n'), (u' chairman', 1), (u' music', 1), (u'judge', 4, u'v'), (u'world', 4, u'n'), (u' the editor]', 2), (u'Sports[league', 1), (u'toyota', 5, u'n'), (u'night', 1, u'n'), (u'www', 1, u'n'), (u'jews', 2, u'n'), (u'deal', 1, u'v'), (u'people', 6, u'n'), (u'senate', 3, u'n'), (u' internet]', 1), (u'church', 4, u'n'), (u'back', 1, u'v'), (u'dead', 2, u's'), (u'clubs', 2, u'n'), (u'growth', 1, u'n'), (u'election', 1, u'n'), (u'home', 3, u'n'), (u'Nations[countries', 1), (u'fox', 3, u'n'), (u'legal', 2, u'a'), (u'maliki', 2), (u' Transactions[terms', 1), (u' travel', 16), (u'super', 1, u's'), (u'jurors', 1, u'n'), (u'island', 2, u'n'), (u' family', 1), (u'drama', 1, u'n'), (u'testimony', 1, u'n'), (u'executives', 5, u'n'), (u'Eli', 1), (u'clinton', 1, u'n'), (u'al', 1, u'n'), (u'travelers', 8, u'n'), (u'attorney', 6, u'n'), (u'son', 2, u'n'), (u'united states', 1), (u'weather', 3, u'v'), (u'artists', 2, u'n'), (u' films', 1), (u'development league', 2), (u'Cards[trump', 1), (u'museum', 3, u'n'), (u'long', 2, u'a'), (u'editor', 2, u'n'), (u' year', 3), (u'series', 2, u'n'), (u'war', 4, u'n'), (u'ago', 3, u's'), (u'jewish', 2, u'a'), (u' nations]', 1), (u' bronx]', 1), (u'ford', 5, u'n'), (u'survived', 3, u'v'), (u' digital', 1), (u'time[years', 1), (u'made', 2, u'v'), (u'House', 1, u'n'), (u'wife', 6, u'n'), (u'economic', 1, u's'), (u'loving', 2, u'v'), (u' wines]', 1), (u"ABC's", 1, u'n'), (u'deaths', 8, u'n'), (u'sales', 2, u'n'), (u'cbs', 1), (u'politics', 1, u'n'), (u'campus', 1, u'n'), (u'film', 3, u'n'), (u'cream', 2, u'v'), (u'misstated', 1, u'v'), (u'lemon', 1, u'n'), (u'gay', 1, u's'), (u' show', 1), (u'percent', 1, u'n'), (u'drugs', 1, u'v'), (u'book', 1, u'n'), (u'digital', 1, u'a'), (u'department', 1, u'n'), (u' end[years', 1), (u' director]', 1), (u'republicans', 1, u'n'), (u'congress', 1, u'n'), (u'students', 2, u'n'), (u' parents', 1), (u'friends', 1, u'n'), (u'died', 5, u'v'), (u'building', 3, u'v'), (u'spades', 3, u'n'), (u' agreed]', 3), (u' season', 1), (u' married]', 1), (u' viewers', 1), (u' brooklyn', 1), (u'time', 3, u'n')]
# with open("dataset/linguistic_analysis_of_words/merge_words_source.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# pos = [(u'', 9), (u'United', 1, u'v'), (u'Winter', 1, u'v'), (u'Service', 1, u'n'), (u'money', 1, u'n'), (u'executive', 1, u'n'), (u'country', 1, u'n'), (u'foot', 1, u'n'), (u'fighters', 1, u'n'), (u'books', 1, u'n'), (u'rooms', 2, u'n'), (u'Internet', 2, u'n'), (u'soldiers', 1, u'n'), (u'flavor', 1, u'n'), (u'systems,', 1), (u'networks', 2, u'n'), (u'secret', 1, u's'), (u'Notice', 1, u'n'), (u'death', 2, u'n'), (u'police', 1, u'v'), (u'Transactions', 1, u'n'), (u'partnerships', 1, u'n'), (u'Football', 1, u'n'), (u'environment', 1, u'n'), (u'palestine', 2, u'n'), (u'offers', 1, u'v'), (u'parents', 1, u'n'), (u'York', 4, u'n'), (u'listing', 1, u'v'), (u'fuel', 2, u'v'), (u'communist', 1, u'n'), (u'local', 1, u'a'), (u'friendly', 1, u'a'), (u'economic', 1, u's'), (u'real', 5, u's'), (u'prime', 1, u's'), (u'vendor', 1, u'n'), (u'finance', 1, u'n'), (u'government', 2, u'n'), (u'Island', 1, u'n'), (u'nation', 1, u'n'), (u'medicine', 1, u'n'), (u'game', 1, u'n'), (u'party', 1, u'n'), (u'schools', 1, u'n'), (u'world', 1, u'n'), (u'republican', 1, u'n'), (u'day', 1, u'n'), (u'viewers', 1, u'n'), (u'Online', 1, u'a'), (u'school', 1, u'n'), (u'meat', 3, u'n'), (u'artist', 1, u'n'), (u'Cards', 4, u'n'), (u'The', 1), (u'countries', 3, u'n'), (u'companies', 2, u'n'), (u'democrat', 2, u'n'), (u'teams', 5, u'n'), (u'Editor', 3, u'n'), (u'Manning', 1, u'v'), (u'landmarks', 2, u'n'), (u'science', 1, u'n'), (u'found', 1, u'v'), (u'security', 1, u'n'), (u'restaurants', 1, u'n'), (u'available', 1, u's'), (u'www', 2, u'n'), (u'square', 1, u'v'), (u'art', 1, u'n'), (u'people', 4, u'n'), (u'senate', 1, u'n'), (u'artists', 1, u'n'), (u'Judiaism', 1), (u'Long', 1, u'a'), (u'Locations', 1, u'n'), (u'culture', 1, u'n'), (u'officials', 1, u'n'), (u'design', 1, u'v'), (u'Location', 1, u'n'), (u'lawyer', 1, u'n'), (u'New', 5, u's'), (u'nations', 2, u'n'), (u'insurance', 1, u'n'), (u'senat', 1), (u'living', 1, u'v'), (u'Church', 2, u'n'), (u'theatre', 1, u'n'), (u'paintings', 1, u'v'), (u'showcase', 1, u'n'), (u'away', 1, u'r'), (u'representatives', 1, u'n'), (u'legal', 2, u'a'), (u'children', 1, u'n'), (u'entertainment', 2, u'n'), (u'written', 1, u'v'), (u'branch', 1, u'n'), (u'health', 1, u'n'), (u'game/s', 2), (u'events', 1, u'n'), (u'Drinking', 1, u'v'), (u'Super', 1, u's'), (u'tech', 1, u'n'), (u'shows', 1, u'v'), (u'scenery', 1, u'n'), (u'jury', 1, u'n'), (u'Places', 2, u'v'), (u'nature', 1, u'n'), (u'University', 1, u'n'), (u'team', 2, u'n'), (u'boss', 2, u'n'), (u'leadership', 1, u'n'), (u'baseball', 2, u'n'), (u'phone,', 1), (u'genre', 7, u'n'), (u'group', 1, u'n'), (u'iraq', 1, u'n'), (u'by', 1, u'r'), (u'change', 2, u'v'), (u'manufacturer', 1, u'n'), (u'league', 2, u'n'), (u'property', 2, u'n'), (u'Religion', 1, u'n'), (u'Deaths', 4, u'n'), (u'Computer', 1, u'n'), (u'Money', 1, u'n'), (u'citizens', 1, u'n'), (u'location', 5, u'n'), (u'contract', 1, u'v'), (u'foreign', 1, u'a'), (u'players', 1, u'n'), (u'Associates', 1, u'n'), (u'games', 1, u'n'), (u'Lawyer', 1, u'n'), (u'testimony', 1, u'n'), (u'corrections', 2, u'n'), (u'military', 2, u'a'), (u'history', 2, u'n'), (u'software', 1, u'n'), (u'origin', 3, u'n'), (u'Obituary', 3, u'n'), (u'anti', 1, u'a'), (u'groups', 1, u'n'), (u'family', 9, u'n'), (u'color', 1, u'n'), (u'Travel', 1, u'v'), (u'litigators', 1, u'n'), (u'channels', 1, u'n'), (u'brands', 1, u'n'), (u'weather', 2, u'v'), (u'Health', 2, u'n'), (u'YOrk', 1, u'n'), (u'parties', 1, u'n'), (u'armed', 1, u'a'), (u'Residents', 1, u'n'), (u'size', 2, u'n'), (u'city', 1, u'n'), (u'properties', 1, u'n'), (u'management', 2, u'n'), (u'estate', 5, u'n'), (u'area', 1, u'n'), (u'spending', 1, u'v'), (u'govenor', 1), (u'political', 3, u'a'), (u'vacation', 3, u'n'), (u'sports', 2, u'n'), (u'convicted', 1, u'v'), (u'NY', 1, u'n'), (u'attack', 1, u'n'), (u'Obituaries', 2, u'n'), (u'passed', 1, u'v'), (u'Date', 2, u'n'), (u'cultures', 1, u'n'), (u'NBA', 1), (u'Iraq', 1, u'n'), (u'finances', 1, u'n'), (u'Courtroom', 2, u'n'), (u'israel', 1, u'n'), (u'medium', 1, u'n'), (u'names', 1, u'v'), (u'manufacturers', 1, u'n'), (u'brand', 1, u'n'), (u'Politicians', 2, u'n'), (u'Nations', 4, u'n'), (u'Brands', 3, u'n'), (u'American', 1, u'n'), (u'part', 1, u'n'), (u'minister', 1, u'n'), (u'Healthcare', 1, u'n'), (u'cases', 1, u'n'), (u'Sports', 2, u'n'), (u'he', 1, u'n'), (u'plants', 1, u'v'), (u'Family', 1, u'n'), (u'To', 2), (u'car', 1, u'n'), (u'board', 2, u'n'), (u'war', 2, u'n'), (u'politics', 1, u'n'), (u'movies', 1, u'n'), (u'Colors', 2, u'n'), (u'cost', 2, u'n'), (u'marriage', 1, u'n'), (u'historical', 1, u'a'), (u'of', 3), (u'cosmos', 1, u'n'), (u'Care', 2, u'n'), (u'Children', 1, u'n'), (u'Hockey', 1, u'n'), (u'and', 4), (u'City', 2, u'n'), (u'USA', 1, u'n'), (u'process', 1, u'v'), (u'household', 1, u'n'), (u'in', 1, u's'), (u'tax', 1, u'v'), (u'locations', 1, u'n'), (u'states', 3, u'n'), (u'player', 4, u'n'), (u'Relatives', 1, u'n'), (u'numbers', 1, u'n'), (u'research', 3, u'v'), (u'home', 1, u'n'), (u'shopping', 1, u'v'), (u'film', 2, u'n'), (u'information', 1, u'n'), (u'united', 3, u'v'), (u'court', 2, u'n'), (u'winter', 2, u'v'), (u'ingredients', 1, u'n'), (u'media', 1, u'n'), (u'Price', 1, u'n'), (u'event', 3, u'n'), (u'politicians', 2, u'n'), (u'other', 1, u's'), (u'forces', 1, u'n'), (u'Building', 1, u'v'), (u'President', 1, u'n'), (u'company', 3, u'n'), (u'economy', 2, u'n'), (u'development', 1, u'n'), (u'congress', 1, u'n'), (u'students', 3, u'n'), (u'healthcare', 1, u'n'), (u'space', 1, u'n'), (u'Movies', 1, u'n'), (u'opinion', 1, u'n'), (u'services', 2, u'n'), (u'pleaded', 1, u'v'), (u'Teams', 2, u'n'), (u'types', 2, u'n'), (u'building', 1, u'v'), (u'Exhibitions', 1, u'n'), (u'Bowl', 1, u'n'), (u'phone', 1, u'n'), (u'author', 1, u'n'), (u'Marriages', 3, u'n'), (u'Player', 1, u'n'), (u'directors', 1, u'n'), (u'Weather', 1, u'v'), (u'green', 1, u'n'), (u'time', 7, u'n'), (u'Islam', 1, u'n'), (u'painting', 1, u'v'), (u'travel', 3, u'v'), (u'wine', 1, u'v')]
# with open("dataset/linguistic_analysis_of_words/merge_words_target.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# pos = [(u'colleges', 1, u'n'), (u'coach', 3, u'n'), (u'chinese', 1, u'a'), (u'nets', 1, u'n'), (u'global', 1, u's'), (u'month', 1, u'n'), (u'manager', 1, u'n'), (u'ice', 1, u'n'), (u'skin', 1, u'n'), (u'contributions', 1, u'n'), (u'children', 5, u'n'), (u'devoted', 1, u'v'), (u'apartment', 2, u'n'), (u'terms', 1, u'n'), (u'electricity', 1, u'n'), (u'coughlin', 1), (u'vez', 1), (u'young', 1, u'n'), (u'literary', 1, u's'), (u'iraqi', 1, u'a'), (u'program', 3, u'n'), (u'lawmakers', 1, u'n'), (u'case', 1, u'n'), (u'family', 5, u'n'), (u'woman', 2, u'n'), (u'federation', 1, u'n'), (u'bedrooms', 1, u'n'), (u'libby', 1, u'n'), (u'championship', 1, u'n'), (u'school', 1, u'n'), (u'cable', 1, u'n'), (u'calif', 1, u'n'), (u'tex', 1), (u'companies', 5, u'n'), (u'democrat', 1, u'n'), (u'large', 1, u's'), (u'announced', 1, u'v'), (u'science', 3, u'n'), (u'small', 2, u's'), (u'drawings', 1, u'v'), (u'pork', 1, u'n'), (u'neighborhood', 1, u'n'), (u'leaders', 1, u'n'), (u'abortion', 1, u'n'), (u'foxman', 1), (u'holocaust', 1, u'n'), (u'chef', 1, u'n'), (u'street', 6, u'n'), (u'design', 2, u'v'), (u'castro', 1, u'n'), (u'lawyer', 1, u'n'), (u'pass', 1, u'v'), (u'nbc', 1), (u'investment', 1, u'n'), (u'oscar', 1, u'n'), (u'blue', 1, u's'), (u'afghanistan', 1, u'n'), (u'abc', 1, u'n'), (u'business', 4, u'n'), (u'paintings', 1, u'v'), (u'chicago', 1, u'n'), (u'religious', 1, u'a'), (u'cooking', 1, u'v'), (u'shares', 1, u'v'), (u'mufleh', 1), (u'ancient', 1, u's'), (u'somalia', 1, u'n'), (u'scientists', 1, u'n'), (u'international', 2, u'a'), (u'public', 5, u'n'), (u'disney', 1, u'n'), (u'told', 2, u'v'), (u'full', 1, u's'), (u'jury', 1, u'n'), (u'funeral', 1, u'n'), (u'men', 2, u'n'), (u'french', 2, u'n'), (u'water', 1, u'n'), (u'simon', 1, u'n'), (u'baseball', 1, u'n'), (u'ethanol', 1, u'n'), (u'iraq', 2, u'n'), (u'win', 1, u'v'), (u'teacher', 1, u'n'), (u'change', 1, u'v'), (u'great', 2, u's'), (u'kids', 1, u'n'), (u'prosecutors', 1, u'n'), (u'employees', 1, u'n'), (u'museums', 1, u'n'), (u'trial', 1, u'n'), (u'airport', 1, u'n'), (u'products', 1, u'n'), (u'advertising', 1, u'v'), (u'published', 1, u'v'), (u'military', 2, u'a'), (u'residents', 1, u'n'), (u'makes', 1, u'v'), (u'named', 1, u'v'), (u'love', 1, u'n'), (u'apple', 1, u'n'), (u'campaign', 2, u'n'), (u'cheney', 1), (u'africa', 1, u'n'), (u'private', 2, u's'), (u'hamas', 1, u'n'), (u'county', 1, u'n'), (u'patriots', 1, u'n'), (u'market', 3, u'n'), (u'hotels', 1, u'n'), (u'shareholders', 1, u'n'), (u'feel', 1, u'v'), (u'feb', 1, u'n'), (u'troops', 2, u'n'), (u'army', 1, u'n'), (u'hospital', 2, u'n'), (u'voters', 1, u'n'), (u'sports', 1, u'n'), (u'music', 1, u'n'), (u'films', 1, u'n'), (u'candidates', 1, u'n'), (u'markets', 1, u'n'), (u'loving', 1, u'v'), (u'fugees', 1), (u'israel', 2, u'n'), (u'started', 1, u'v'), (u'tax', 1, u'v'), (u'company', 5, u'n'), (u'chocolate', 1, u'n'), (u'downtown', 1, u'a'), (u'phone', 1, u'n'), (u'baby', 1, u'n'), (u'yard', 1, u'n'), (u'cases', 2, u'n'), (u'earth', 1, u'n'), (u'women', 3, u'n'), (u'town', 1, u'n'), (u'high', 3, u'n'), (u'word', 1, u'n'), (u'room', 3, u'n'), (u'player', 2, u'n'), (u'car', 1, u'n'), (u'work', 4, u'v'), (u'gasoline', 1, u'n'), (u'movies', 1, u'n'), (u'fla', 1), (u'making', 1, u'v'), (u'history', 3, u'n'), (u'heart', 2, u'n'), (u'estate', 1, u'n'), (u'give', 1, u'v'), (u'galleries', 1, u'n'), (u'share', 1, u'v'), (u'states', 6, u'n'), (u'professor', 1, u'n'), (u'council', 1, u'n'), (u'yankees', 1, u'n'), (u'david', 2, u'n'), (u'viewers', 1, u'n'), (u'species', 1, u'n'), (u'risk', 1, u'n'), (u'information', 1, u'n'), (u'united', 3, u'v'), (u'end', 1, u'n'), (u'winter', 1, u'v'), (u'january', 1, u'n'), (u'clothing', 1, u'v'), (u'travel', 1, u'v'), (u'magazine', 1, u'n'), (u'write', 1, u'v'), (u'hot', 1, u's'), (u'writers', 1, u'n'), (u'earnings', 1, u'v'), (u'comedy', 1, u'n'), (u'beach', 1, u'v'), (u'economy', 1, u'n'), (u'plant', 1, u'v'), (u'designer', 1, u'n'), (u'spitzer', 1), (u'hong', 1), (u'collection', 1, u'n'), (u'studies', 1, u'n'), (u'court', 1, u'n'), (u'law', 3, u'n'), (u'data', 1, u'n'), (u'man', 3, u'n'), (u'natural', 1, u's'), (u'johnson', 1, u'n'), (u'light', 1, u's'), (u'st', 3), (u'coal', 1, u'v'), (u'chief', 2, u'n'), (u'green', 1, u'n'), (u'official', 1, u's'), (u'media', 2, u'n'), (u'democratic', 1, u'a'), (u'began', 2, u'v'), (u'wine', 1, u'v'), (u'played', 1, u'v'), (u'office', 3, u'n'), (u'bowl', 1, u'n'), (u'move', 1, u'v'), (u'charities', 1, u'n'), (u'years', 8, u'n'), (u'brain', 1, u'n'), (u'including', 1, u'v'), (u'committee', 1, u'n'), (u'cuts', 1, u'v'), (u'kong', 1), (u'avenue', 3, u'n'), (u'mayor', 1, u'n'), (u'style', 1, u'n'), (u'group', 4, u'n'), (u'sunday', 3, u'n'), (u'writing', 1, u'v'), (u'late', 1, u's'), (u'resort', 1, u'n'), (u'production', 2, u'n'), (u'policy', 2, u'n'), (u'speaker', 1, u'n'), (u'weeks', 1, u'n'), (u'criminal', 1, u's'), (u'sauce', 1, u'v'), (u'texas', 1, u'n'), (u'forest', 1, u'n'), (u'character', 1, u'n'), (u'good', 4, u's'), (u'food', 2, u'n'), (u'auto', 1, u'n'), (u'nation', 1, u'n'), (u'taliban', 1, u'n'), (u'half', 2, u's'), (u'schools', 1, u'n'), (u'republican', 1, u'n'), (u'day', 3, u'n'), (u'bank', 1, u'n'), (u'kollek', 1), (u'meat', 1, u'n'), (u'james', 2, u'n'), (u'university', 3, u'n'), (u'countries', 1, u'n'), (u'detroit', 1, u'n'), (u'victory', 1, u'n'), (u'louis', 1, u'n'), (u'found', 2, u'v'), (u'quarter', 1, u'n'), (u'referred', 1, u'v'), (u'week', 2, u'n'), (u'square', 1, u'v'), (u'financial', 1, u'a'), (u'billion', 2, u'n'), (u'weight', 1, u'n'), (u'house', 5, u'n'), (u'fish', 2, u'n'), (u'hard', 1, u'r'), (u'buildings', 2, u'v'), (u'brother', 1, u'n'), (u'society', 1, u'n'), (u'books', 1, u'n'), (u'year', 13, u'n'), (u'arab', 1, u'n'), (u'teams', 2, u'n'), (u'insurance', 1, u'n'), (u'living', 1, u'v'), (u'jerusalem', 1, u'n'), (u'beauty', 1, u'n'), (u'space', 3, u'n'), (u'culture', 1, u'n'), (u'god', 2, u'n'), (u'novels', 1, u'n'), (u'rev', 1, u'v'), (u'research', 1, u'v'), (u'increase', 2, u'n'), (u'investigation', 1, u'n'), (u'health', 2, u'n'), (u'internet', 1, u'n'), (u'medicine', 1, u'n'), (u'venezuela', 1, u'n'), (u'red', 2, u'n'), (u'shows', 2, u'v'), (u'wines', 1, u'v'), (u'cars', 1, u'n'), (u'million', 6, u'n'), (u'free', 3, u'v'), (u'playing', 1, u'v'), (u'basketball', 1, u'n'), (u'california', 1, u'n'), (u'york', 7, u'n'), (u'members', 2, u'n'), (u'put', 1, u'v'), (u'wanted', 1, u'v'), (u'care', 2, u'n'), (u'benefits', 1, u'n'), (u'service', 4, u'n'), (u'english', 1, u'n'), (u'computers', 1, u'n'), (u'days', 2, u'n'), (u'times', 3, u'n'), (u'thing', 1, u'n'), (u'american', 7, u'n'), (u'place', 2, u'v'), (u'husband', 2, u'v'), (u'corrections', 1, u'n'), (u'hussein', 1, u'n'), (u'secretary', 1, u'n'), (u'museum', 1, u'n'), (u'south', 2, u'n'), (u'blood', 1, u'n'), (u'cheese', 1, u'v'), (u'major', 1, u'a'), (u'characters', 1, u'n'), (u'revenue', 1, u'n'), (u'grade', 1, u'n'), (u'number', 2, u'n'), (u'jesus', 1, u'n'), (u'feet', 2, u'n'), (u'floors', 1, u'n'), (u'americans', 2, u'n'), (u'president', 5, u'n'), (u'vote', 1, u'v'), (u'carter', 1, u'n'), (u'idea', 1, u'n'), (u'city', 4, u'n'), (u'story', 3, u'n'), (u'management', 1, u'n'), (u'district', 2, u'v'), (u'bears', 1, u'v'), (u'top', 1, u'n'), (u'girls', 1, u'n'), (u'system', 2, u'n'), (u'fiction', 1, u'n'), (u'attack', 1, u'n'), (u'rates', 1, u'v'), (u'stock', 1, u'n'), (u'white', 3, u'n'), (u'john', 4, u'n'), (u'final', 1, u's'), (u'friend', 1, u'n'), (u'listed', 1, u'v'), (u'software', 1, u'n'), (u'stars', 1, u'n'), (u'grandchildren', 1, u'n'), (u'shawn', 1, u'n'), (u'season', 3, u'v'), (u'hotel', 1, u'n'), (u'park', 3, u'n'), (u'environmental', 1, u'a'), (u'part', 2, u'n'), (u'doctors', 1, u'n'), (u'hollywood', 1, u'n'), (u'obama', 1), (u'past', 2, u'n'), (u'kind', 1, u's'), (u'minister', 2, u'n'), (u'princeton', 1, u'n'), (u'tree', 1, u'v'), (u'war', 4, u'n'), (u'project', 1, u'v'), (u'patients', 1, u'n'), (u'defense', 3, u'n'), (u'marriage', 1, u'n'), (u'williams', 1, u'n'), (u'video', 1, u'n'), (u'india', 1, u'n'), (u'sculpture', 1, u'v'), (u'russia', 1, u'n'), (u'fashion', 1, u'n'), (u'san', 1), (u'investors', 1, u'n'), (u'correction', 1, u'n'), (u'modern', 1, u's'), (u'turned', 1, u'v'), (u'mailer', 1, u'n'), (u'glass', 1, u'n'), (u'tonight', 1, u'r'), (u'medical', 1, u'a'), (u'catholic', 2, u'a'), (u'wilson', 1, u'n'), (u'dishes', 1, u'n'), (u'person', 1, u'n'), (u'agency', 1, u'n'), (u'snow', 1, u'n'), (u'dining', 1, u'v'), (u'rome', 1, u'n'), (u'chairman', 2, u'v'), (u'forces', 1, u'n'), (u'paris', 1, u'n'), (u'quarterback', 1, u'n'), (u'club', 2, u'n'), (u'play', 3, u'v'), (u'added', 1, u'v'), (u'price', 2, u'n'), (u'knew', 1, u'v'), (u'paid', 1, u'v'), (u'brooklyn', 2, u'n'), (u'plan', 2, u'v'), (u'services', 3, u'n'), (u'seasons', 1, u'v'), (u'america', 2, u'n'), (u'class', 1, u'n'), (u'queens', 1, u'n'), (u'episode', 1, u'n'), (u'consumers', 1, u'n'), (u'mobile', 1, u's'), (u'soviet', 1, u'a'), (u'average', 1, u's'), (u'metal', 1, u'n'), (u'disease', 1, u'n'), (u'mrs', 2, u'n'), (u'neediest', 1, u's'), (u'movie', 1, u'n'), (u'senior', 1, u's'), (u'left', 3, u'v'), (u'salt', 1, u'v'), (u'review', 1, u'n'), (u'fact', 1, u'n'), (u'shop', 1, u'v'), (u'thomas', 1, u'n'), (u'shot', 1, u'v'), (u'survived', 1, u'v'), (u'pope', 1, u'n'), (u'show', 2, u'v'), (u'german', 1, u'n'), (u'agreed', 1, u'v'), (u'contemporary', 1, u's'), (u'radio', 1, u'n'), (u'democrats', 1, u'n'), (u'bedroom', 1, u'n'), (u'soldiers', 1, u'n'), (u'chicken', 1, u'n'), (u'find', 1, u'v'), (u'partners', 1, u'n'), (u'producer', 1, u'n'), (u'knicks', 1), (u'justice', 1, u'n'), (u'menu', 1, u'n'), (u'writes', 1, u'v'), (u'saints', 1, u'n'), (u'written', 1, u'v'), (u'ball', 1, u'n'), (u'crime', 1, u'n'), (u'jan', 3, u'n'), (u'bush', 1, u'n'), (u'won', 1, u'v'), (u'black', 2, u's'), (u'hockey', 1, u'n'), (u'fuel', 1, u'v'), (u'communist', 1, u'n'), (u'local', 2, u'a'), (u'carolina', 1, u'n'), (u'giants', 1, u'n'), (u'sense', 1, u'n'), (u'king', 1, u'n'), (u'de', 1, u'n'), (u'television', 1, u'n'), (u'trees', 1, u'v'), (u'coast', 1, u'n'), (u'baghdad', 1, u'n'), (u'words', 1, u'n'), (u'churches', 1, u'n'), (u'hedge', 1, u'v'), (u'trade', 1, u'n'), (u'sunni', 1, u'n'), (u'prime', 2, u's'), (u'child', 1, u'n'), (u'bar', 2, u'n'), (u'smoking', 1, u'v'), (u'artist', 1, u'n'), (u'married', 1, u'a'), (u'taxes', 2, u'v'), (u'morning', 1, u'n'), (u'bad', 1, u's'), (u'miles', 1, u'n'), (u'troop', 1, u'n'), (u'ohio', 1, u'n'), (u'wrote', 2, u'v'), (u'restaurants', 1, u'n'), (u'europe', 1, u'n'), (u'set', 2, u'v'), (u'art', 1, u'n'), (u'intelligence', 1, u'n'), (u'national', 2, u'a'), (u'testing', 1, u'v'), (u'sex', 1, u'n'), (u'elected', 1, u'v'), (u'officials', 6, u'n'), (u'college', 1, u'n'), (u'european', 1, u'a'), (u'sea', 1, u'n'), (u'iran', 1, u'n'), (u'news', 1, u'n'), (u'nations', 1, u'n'), (u'points', 1, u'n'), (u'israeli', 1, u'a'), (u'federal', 2, u'a'), (u'nuclear', 1, u'a'), (u'century', 2, u'n'), (u'sites', 1, u'v'), (u'weapons', 1, u'n'), (u'state', 7, u'n'), (u'classes', 1, u'n'), (u'shiite', 1, u'n'), (u'publishers', 1, u'n'), (u'notice', 1, u'n'), (u'recently', 1, u'r'), (u'majority', 1, u'n'), (u'team', 2, u'n'), (u'jr', 1, u'n'), (u'harvard', 1, u'n'), (u'awards', 1, u'n'), (u'jets', 1, u'n'), (u'police', 2, u'v'), (u'kitchen', 2, u'n'), (u'hours', 1, u'n'), (u'climate', 1, u'n'), (u'store', 1, u'n'), (u'brown', 1, u'n'), (u'restaurant', 1, u'n'), (u'country', 2, u'n'), (u'taking', 1, u'v'), (u'readers', 1, u'n'), (u'contract', 1, u'v'), (u'foreign', 2, u'a'), (u'players', 2, u'n'), (u'games', 2, u'n'), (u'bronx', 1, u'n'), (u'senator', 1, u'n'), (u'asked', 1, u'v'), (u'jersey', 1, u'n'), (u'pakistan', 1, u'n'), (u'ch', 1), (u'yards', 1, u'n'), (u'cancer', 1, u'n'), (u'point', 2, u'n'), (u'wall', 2, u'n'), (u'sweet', 1, u's'), (u'community', 2, u'n'), (u'anti', 1, u'a'), (u'article', 1, u'n'), (u'table', 1, u'n'), (u'conference', 1, u'n'), (u'arts', 1, u'n'), (u'union', 2, u'n'), (u'west', 3, u'n'), (u'political', 3, u'a'), (u'airlines', 1, u'n'), (u'strategy', 1, u'n'), (u'secret', 1, u's'), (u'pa', 1, u'n'), (u'interest', 1, u'n'), (u'tv', 1, u'n'), (u'poet', 1, u'n'), (u'exhibition', 1, u'n'), (u'firm', 1, u's'), (u'field', 1, u'n'), (u'life', 3, u'n'), (u'flight', 1, u'n'), (u'gay', 1, u's'), (u'league', 3, u'n'), (u'drugs', 1, u'v'), (u'ages', 1, u'n'), (u'republicans', 1, u'n'), (u'gas', 1, u'n'), (u'search', 1, u'n'), (u'palestinian', 1, u'a'), (u'al', 1, u'n'), (u'fund', 2, u'v'), (u'representative', 1, u'n'), (u'mail', 1, u'n'), (u'prices', 2, u'n'), (u'daughter', 2, u'n'), (u'atlanta', 1, u'n'), (u'evidence', 1, u'v'), (u'plants', 1, u'v'), (u'bill', 2, u'n'), (u'budget', 1, u'n'), (u'governor', 1, u'n'), (u'air', 1, u'n'), (u'teachers', 1, u'n'), (u'property', 1, u'n'), (u'study', 1, u'n'), (u'bathrooms', 1, u'n'), (u'mexico', 1, u'n'), (u'site', 2, u'n'), (u'ii', 1, u's'), (u'middle', 1, u'n'), (u'drug', 1, u'v'), (u'carbon', 1, u'n'), (u'technology', 1, u'n'), (u'memorial', 1, u'n'), (u'author', 1, u'n'), (u'pay', 2, u'v'), (u'make', 2, u'v'), (u'administration', 2, u'n'), (u'trip', 1, u'n'), (u'member', 1, u'n'), (u'speech', 1, u'n'), (u'digital', 1, u'a'), (u'incorrectly', 1, u'r'), (u'party', 2, u'n'), (u'tests', 1, u'v'), (u'pan', 1, u'n'), (u'analysts', 1, u'n'), (u'development', 1, u'n'), (u'oil', 2, u'n'), (u'lawyers', 1, u'n'), (u'mountain', 1, u'n'), (u'saddam', 1, u'n'), (u'friends', 2, u'n'), (u'yesterday', 3, u'r'), (u'director', 3, u'n'), (u'student', 1, u'n'), (u'colts', 1, u'n'), (u'recent', 1, u's'), (u'dark', 1, u's'), (u'theater', 1, u'n'), (u'center', 3, u'n'), (u'programs', 1, u'n'), (u'charges', 1, u'v'), (u'iraqis', 1, u'n'), (u'poland', 1, u'n'), (u'game', 2, u'n'), (u'thought', 1, u'v'), (u'academic', 1, u's'), (u'costs', 1, u'n'), (u'china', 1, u'n'), (u'mother', 4, u'n'), (u'corporate', 1, u's'), (u'researchers', 1, u'n'), (u'charged', 1, u'v'), (u'things', 1, u'n'), (u'mind', 1, u'n'), (u'stores', 1, u'n'), (u'money', 2, u'n'), (u'executive', 1, u'n'), (u'officers', 1, u'n'), (u'foot', 1, u'n'), (u'human', 2, u'a'), (u'polish', 1, u'n'), (u'web', 1, u'n'), (u'death', 2, u'n'), (u'ads', 1, u'n'), (u'cup', 1, u'n'), (u'rose', 1, u'v'), (u'workers', 1, u'n'), (u'smith', 1, u'n'), (u'killed', 1, u'v'), (u'color', 1, u'n'), (u'add', 1, u'v'), (u'parents', 2, u'n'), (u'board', 2, u'n'), (u'beloved', 1, u's'), (u'prison', 1, u'n'), (u'east', 2, u'n'), (u'ski', 1, u'v'), (u'match', 1, u'v'), (u'real', 2, u's'), (u'customers', 1, u'n'), (u'government', 4, u'n'), (u'read', 1, u'v'), (u'big', 2, u's'), (u'online', 1, u'a'), (u'early', 2, u'a'), (u'test', 1, u'v'), (u'cultural', 1, u'a'), (u'judge', 1, u'v'), (u'world', 6, u'n'), (u'execution', 1, u'n'), (u'projects', 1, u'v'), (u'toyota', 1, u'n'), (u'michael', 1, u'n'), (u'audience', 1, u'n'), (u'officer', 1, u'n'), (u'night', 4, u'n'), (u'security', 2, u'n'), (u'works', 1, u'v'), (u'www', 1, u'n'), (u'google', 1, u'v'), (u'jews', 1, u'n'), (u'deal', 1, u'v'), (u'people', 7, u'n'), (u'senate', 1, u'n'), (u'christian', 1, u'a'), (u'church', 2, u'n'), (u'lebanon', 1, u'n'), (u'back', 4, u'v'), (u'library', 2, u'n'), (u'hair', 1, u'n'), (u'born', 1, u'v'), (u'growth', 1, u'n'), (u'election', 1, u'n'), (u'home', 4, u'n'), (u'lead', 1, u'n'), (u'manning', 1, u'v'), (u'fox', 1, u'n'), (u'legal', 1, u'a'), (u'maliki', 1), (u'leader', 1, u'n'), (u'cost', 1, u'n'), (u'patient', 1, u'n'), (u'power', 3, u'n'), (u'marketing', 1, u'v'), (u'corn', 1, u'n'), (u'broker', 1, u's'), (u'defensive', 1, u'a'), (u'super', 1, u's'), (u'sister', 1, u'n'), (u'attacks', 1, u'n'), (u'island', 2, u'n'), (u'industry', 2, u'n'), (u'violence', 1, u'n'), (u'sectarian', 1, u'a'), (u'angeles', 1), (u'dinner', 1, u'n'), (u'airline', 1, u'n'), (u'documentary', 1, u'a'), (u'executives', 1, u'n'), (u'bath', 1, u'n'), (u'clinton', 1, u'n'), (u'mets', 1), (u'travelers', 1, u'n'), (u'washington', 1, u'n'), (u'attorney', 1, u'n'), (u'son', 3, u'n'), (u'pair', 1, u'v'), (u'playoff', 1, u'n'), (u'weather', 1, u'v'), (u'homeless', 1, u's'), (u'artists', 1, u'n'), (u'france', 1, u'n'), (u'computer', 1, u'n'), (u'area', 3, u'n'), (u'spending', 1, u'v'), (u'pelosi', 1), (u'housing', 1, u'n'), (u'apartments', 1, u'n'), (u'long', 3, u'a'), (u'gallery', 1, u'n'), (u'los', 1), (u'editor', 1, u'n'), (u'lot', 2, u'n'), (u'series', 1, u'n'), (u'forward', 1, u'r'), (u'energy', 1, u'n'), (u'building', 2, u'v'), (u'head', 1, u'n'), (u'buy', 1, u'v'), (u'north', 1, u'n'), (u'ireland', 1, u'n'), (u'jewish', 1, u'a'), (u'funds', 1, u'v'), (u'pastor', 1, u'n'), (u'ford', 2, u'n'), (u'wireless', 1, u'n'), (u'boys', 1, u'n'), (u'heat', 1, u'n'), (u'jones', 1, u'n'), (u'authority', 1, u'n'), (u'solar', 1, u'a'), (u'mich', 1), (u'line', 1, u'n'), (u'true', 1, u's'), (u'eat', 1, u'v'), (u'directed', 1, u'v'), (u'made', 3, u'v'), (u'wife', 2, u'n'), (u'signed', 1, u'v'), (u'father', 3, u'n'), (u'windows', 1, u'n'), (u'emissions', 1, u'n'), (u'pm', 1, u'n'), (u'minutes', 2, u'n'), (u'called', 2, u'v'), (u'supreme', 1, u's'), (u'deaths', 1, u'n'), (u'sales', 2, u'n'), (u'doesn', 1), (u'general', 1, u's'), (u'shopping', 1, u'v'), (u'education', 1, u'n'), (u'campus', 1, u'n'), (u'film', 1, u'n'), (u'cream', 1, u'v'), (u'misstated', 1, u'v'), (u'floor', 2, u'n'), (u'corporation', 1, u'n'), (u'peace', 1, u'n'), (u'percent', 4, u'n'), (u'treatment', 1, u'n'), (u'actor', 1, u'n'), (u'graduate', 1, u'v'), (u'ny', 1, u'n'), (u'book', 2, u'n'), (u'actors', 1, u'n'), (u'income', 1, u'n'), (u'department', 3, u'n'), (u'depot', 1, u'n'), (u'manhattan', 2, u'n'), (u'francisco', 1), (u'star', 1, u'n'), (u'users', 1, u'n'), (u'congress', 3, u'n'), (u'students', 1, u'n'), (u'football', 1, u'n'), (u'diet', 1, u'n'), (u'important', 1, u'a'), (u'stocks', 1, u'n'), (u'presidential', 1, u'a'), (u'died', 1, u'v'), (u'opened', 1, u'v'), (u'ago', 2, u's'), (u'land', 2, u'n'), (u'studio', 1, u'n'), (u'vice', 1, u'n'), (u'painting', 1, u'v'), (u'microsoft', 1), (u'nelson', 1, u'n'), (u'time', 4, u'n'), (u'fresh', 1, u's'), (u'brokers', 1, u'v')]
# with open("dataset/linguistic_analysis_of_words/original_topic_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# pos = [(u'coach', 22, u'n'), (u'chinese', 8, u'a'), (u'global', 2, u's'), (u'olors', 2), (u'ice', 7, u'n'), (u'dish', 1, u'n'), (u'arriages', 3), (u'saved', 1, u'v'), (u'children', 23, u'n'), (u'apartment', 15, u'n'), (u'number', 6, u'n'), (u'randmother', 1), (u'religion', 1, u'n'), (u'father', 23, u'n'), (u'young', 1, u'n'), (u'environment', 1, u'n'), (u'iraqi', 8, u'a'), (u'program', 6, u'n'), (u'friendly', 1, u'a'), (u'roadway', 1, u'n'), (u'case', 9, u'n'), (u'ivil', 1), (u'woman', 5, u'n'), (u'risk', 8, u'n'), (u'end', 5, u'n'), (u'sellers', 1, u'n'), (u'novel', 1, u's'), (u'ridegroom', 1), (u'nets', 8, u'n'), (u'school', 9, u'n'), (u'pbs', 2, u'n'), (u'louis', 6, u'n'), (u'companies', 27, u'n'), (u'democrat', 10, u'n'), (u'things', 5, u'n'), (u'race', 2, u'n'), (u'science', 3, u'n'), (u'small', 4, u's'), (u'govenor', 1), (u'added', 2, u'v'), (u'drawings', 1, u'v'), (u'pork', 2, u'n'), (u'leaders', 1, u'n'), (u'ssociates', 1), (u'holocaust', 7, u'n'), (u'chef', 8, u'n'), (u'rate', 1, u'n'), (u'street', 27, u'n'), (u'video', 9, u'n'), (u'governor', 8, u'n'), (u'lawyer', 8, u'n'), (u'plead', 1, u'v'), (u'nbc', 9), (u'hicago', 1), (u'investment', 9, u'n'), (u'folk', 1, u'n'), (u'blue', 6, u's'), (u'abc', 2, u'n'), (u'business', 17, u'n'), (u'paintings', 8, u'v'), (u'showcase', 1, u'n'), (u'religious', 1, u'a'), (u'disease', 9, u'n'), (u'asia', 1, u'n'), (u'energy', 7, u'n'), (u'merican', 2), (u'new', 3, u's'), (u'public', 8, u'n'), (u'told', 5, u'v'), (u'scenery', 1, u'n'), (u'iran', 8, u'n'), (u'funeral', 9, u'n'), (u'olicy', 1), (u'french', 7, u'n'), (u'water', 8, u'n'), (u'minor', 1, u'a'), (u'baseball', 8, u'n'), (u'ethanol', 8, u'n'), (u'iraq', 16, u'n'), (u'tragedy', 1, u'n'), (u'change', 7, u'v'), (u'ocations', 1), (u'great', 3, u's'), (u'kids', 4, u'n'), (u'daughter', 7, u'n'), (u'employees', 8, u'n'), (u'guilty', 1, u'a'), (u'trial', 9, u'n'), (u'airport', 16, u'n'), (u'advertising', 8, u'v'), (u'nited', 2), (u'military', 19, u'a'), (u'residents', 6, u'n'), (u'makes', 3, u'v'), (u'struggle', 1, u'v'), (u'named', 6, u'v'), (u'diagramed', 1, u'v'), (u'ago', 5, u's'), (u'family', 36, u'n'), (u'transit', 1, u'v'), (u'litigators', 1, u'n'), (u'county', 8, u'n'), (u'patriots', 6, u'n'), (u'names', 2, u'v'), (u'congolese', 1, u'a'), (u'carter', 3, u'n'), (u'armed', 1, u'a'), (u'market', 16, u'n'), (u'cost', 6, u'n'), (u'jan', 2, u'n'), (u'troops', 17, u'n'), (u'army', 8, u'n'), (u'illegal', 1, u'a'), (u'hospital', 6, u'n'), (u'destination', 1, u'n'), (u'sports', 4, u'n'), (u'music', 9, u'n'), (u'films', 7, u'n'), (u'candidates', 1, u'n'), (u'manufacturer', 1, u'n'), (u'prep', 1, u'n'), (u'defendant', 1, u'n'), (u'loving', 6, u'v'), (u'israel', 15, u'n'), (u'club', 2, u'n'), (u'tax', 10, u'v'), (u'company', 29, u'n'), (u'freedom', 1, u'n'), (u'testified', 1, u'v'), (u'chocolate', 8, u'n'), (u'phone', 11, u'n'), (u'train', 1, u'v'), (u'adult', 1, u's'), (u'rands', 1, u'n'), (u'baby', 5, u'n'), (u'cases', 10, u'n'), (u'women', 12, u'n'), (u'town', 6, u'n'), (u'high', 11, u'n'), (u'room', 8, u'n'), (u'ocial', 1), (u'player', 8, u'n'), (u'car', 9, u'n'), (u'ride', 1, u'v'), (u'work', 19, u'v'), (u'abortion', 2, u'n'), (u'reviews', 2, u'n'), (u'movies', 8, u'n'), (u'culture', 1, u'n'), (u'of', 3), (u'fla', 1), (u'making', 3, u'v'), (u'history', 17, u'n'), (u'giants', 6, u'n'), (u'violence', 1, u'n'), (u'trump', 2, u'v'), (u'estate', 13, u'n'), (u'hooting', 1, u'v'), (u'process', 1, u'v'), (u'household', 1, u'n'), (u'share', 1, u'v'), (u'agent', 2, u'n'), (u'ditor', 2), (u'states', 17, u'n'), (u'numbers', 1, u'n'), (u'david', 3, u'n'), (u'viewers', 9, u'n'), (u'ceremony', 1, u'n'), (u'information', 2, u'n'), (u'united', 18, u'v'), (u'court', 10, u'n'), (u'winter', 10, u'v'), (u'january', 6, u'n'), (u'travel', 38, u'v'), (u'uther', 1), (u'ockey', 1), (u'write', 4, u'v'), (u'earnings', 1, u'v'), (u'comedy', 8, u'n'), (u'beach', 10, u'v'), (u'stock', 10, u'n'), (u'fare', 1, u'n'), (u'plant', 7, u'v'), (u'designer', 9, u'n'), (u'spitzer', 4), (u'isc', 1), (u'ethnic', 1, u's'), (u'president', 27, u'n'), (u'pleaded', 2, u'v'), (u'law', 14, u'n'), (u'man', 8, u'n'), (u'johnson', 3, u'n'), (u'light', 4, u's'), (u'voice', 1, u'n'), (u'season', 27, u'v'), (u'obama', 1), (u'ards', 1, u'n'), (u'chief', 8, u'n'), (u'green', 9, u'n'), (u'eath', 1), (u'healthcare', 1, u'n'), (u'banks', 1, u'n'), (u'preventive', 1, u'n'), (u'democratic', 6, u'a'), (u'landmarks', 2, u'n'), (u'ourtroom', 2), (u'mexican', 1, u'a'), (u'office', 7, u'n'), (u'heater', 1, u'n'), (u'rabbi', 1, u'n'), (u'wedding', 2, u'n'), (u'major', 3, u'a'), (u'years', 22, u'n'), (u'omney', 1), (u'earth', 6, u'n'), (u'committee', 7, u'n'), (u'ity', 2), (u'avenue', 2, u'n'), (u'mayor', 7, u'n'), (u'style', 1, u'n'), (u'hildren', 1), (u'group', 10, u'n'), (u'eather', 1), (u'sale', 1, u'n'), (u'writing', 6, u'v'), (u'late', 4, u's'), (u'resort', 24, u'n'), (u'production', 9, u'n'), (u'laces', 2, u'v'), (u'listing', 2, u'v'), (u'policy', 9, u'n'), (u'mail', 8, u'n'), (u'weeks', 4, u'n'), (u'holiday', 2, u'n'), (u'sauce', 8, u'v'), (u'non', 2, u'r'), (u'good', 9, u's'), (u'finance', 2, u'n'), (u'civilian', 1, u'a'), (u'food', 15, u'n'), (u'auto', 1, u'n'), (u'bama', 1), (u'eligion', 1), (u'half', 2, u's'), (u'schools', 7, u'n'), (u'republican', 11, u'n'), (u'day', 6, u'n'), (u'bank', 6, u'n'), (u'feet', 1, u'n'), (u'meat', 8, u'n'), (u'james', 3, u'n'), (u'university', 9, u'n'), (u'countries', 8, u'n'), (u'ife', 1), (u'found', 14, u'v'), (u'quarter', 8, u'n'), (u'ports', 2, u'v'), (u'aseball', 1), (u'square', 8, u'v'), (u'financial', 8, u'a'), (u'suspended', 1, u'v'), (u'house', 28, u'n'), (u'fish', 8, u'n'), (u'artists', 7, u'n'), (u'society', 9, u'n'), (u'books', 9, u'n'), (u'year', 52, u'n'), (u'ew', 6, u'n'), (u'insurance', 10, u'n'), (u'hostel', 1, u'n'), (u'living', 1, u'v'), (u'entertainment', 2, u'n'), (u'profit', 1, u'v'), (u'god', 8, u'n'), (u'motel', 1, u'n'), (u'testify', 1, u'v'), (u'research', 9, u'v'), (u'investigation', 9, u'n'), (u'health', 20, u'n'), (u'ights', 1), (u'internet', 10, u'n'), (u'medicine', 1, u'n'), (u'calif', 4, u'n'), (u'red', 7, u'n'), (u'shows', 10, u'v'), (u'wines', 6, u'v'), (u'cars', 7, u'n'), (u'million', 23, u'n'), (u'free', 7, u'v'), (u'ifestyle', 1), (u'basketball', 9, u'n'), (u'york', 25, u'n'), (u'plea', 1, u'n'), (u'ord', 1), (u'card', 1, u'n'), (u'care', 15, u'n'), (u'ate', 1, u'v'), (u'udiaism', 1), (u'times', 12, u'n'), (u'thing', 4, u'n'), (u'american', 33, u'n'), (u'husband', 7, u'v'), (u'homelessness', 1, u'n'), (u'corrections', 5, u'n'), (u'elatives', 1), (u'hussein', 9, u'n'), (u'secretary', 5, u'n'), (u'uilding', 1), (u'origin', 2, u'n'), (u'cheese', 8, u'v'), (u'ccord', 1), (u'bowl', 6, u'n'), (u'hero', 1, u'n'), (u'ove', 1), (u'ong', 1), (u'channels', 1, u'n'), (u'delicious', 1, u's'), (u'spanish', 1, u'n'), (u'vote', 9, u'v'), (u'size', 2, u'n'), (u'city', 15, u'n'), (u'story', 8, u'n'), (u'management', 10, u'n'), (u'fair', 1, u's'), (u'service', 17, u'n'), (u'bears', 4, u'v'), (u'shooting', 1, u'v'), (u'system', 16, u'n'), (u'relations', 2, u'n'), (u'fiction', 2, u'n'), (u'attack', 2, u'n'), (u'merica', 1), (u'orrow', 1), (u'listed', 8, u'v'), (u'passed', 1, u'v'), (u'palestine', 3, u'n'), (u'white', 10, u'n'), (u'john', 3, u'n'), (u'finances', 1, u'n'), (u'williams', 3, u'n'), (u'software', 10, u'n'), (u'murder', 1, u'v'), (u'awyer', 1), (u'hotel', 24, u'n'), (u'park', 16, u'n'), (u'uper', 1, u's'), (u'environmental', 7, u'a'), (u'part', 8, u'n'), (u'doctors', 7, u'n'), (u'oland', 1), (u'udi', 1), (u'hollywood', 7, u'n'), (u'center', 8, u'n'), (u'tex', 3), (u'kind', 3, u's'), (u'furnishings', 1, u'n'), (u'manning', 4, u'v'), (u'nations', 11, u'n'), (u'project', 8, u'v'), (u'chool', 1), (u'patients', 9, u'n'), (u'accused', 1, u'v'), (u'marriage', 9, u'n'), (u'store', 9, u'n'), (u'coat', 1, u'v'), (u'briefing', 1, u'v'), (u'hurch', 1), (u'sculpture', 2, u'v'), (u'russia', 9, u'n'), (u'published', 7, u'v'), (u'sentenced', 1, u'v'), (u'bridge', 1, u'n'), (u'fashion', 8, u'n'), (u'san', 5), (u'investors', 9, u'n'), (u'correction', 4, u'n'), (u'nteraction', 1), (u'locations', 1, u'n'), (u'glass', 6, u'n'), (u'tonight', 3, u'r'), (u'medical', 9, u'a'), (u'slam', 1, u'v'), (u'rent', 2, u'v'), (u'raq', 1), (u'st', 7), (u'mountain', 6, u'n'), (u'wilson', 2, u'n'), (u'oughlin', 1), (u'veteran', 1, u'n'), (u'foxman', 2), (u'snow', 8, u'n'), (u'dining', 7, u'v'), (u'chairman', 8, u'v'), (u'forces', 9, u'n'), (u'online', 11, u'a'), (u'interior', 2, u's'), (u'quarterback', 7, u'n'), (u'play', 9, u'v'), (u'mileage', 1, u'n'), (u'theatre', 1, u'n'), (u'transactions', 1, u'n'), (u'price', 8, u'n'), (u'systems', 1, u'n'), (u'paid', 5, u'v'), (u'uninsured', 1, u'a'), (u'brooklyn', 8, u'n'), (u'plan', 14, u'v'), (u'letter', 1, u'n'), (u'services', 2, u'n'), (u'america', 6, u'n'), (u'class', 9, u'n'), (u'soviet', 7, u'a'), (u'professor', 6, u'n'), (u'orrections', 1), (u'playing', 4, u'v'), (u'federal', 15, u'a'), (u'neediest', 9, u's'), (u'tech', 1, u'n'), (u'movie', 8, u'n'), (u'wine', 10, u'v'), (u'painting', 7, u'v'), (u'away', 1, u'r'), (u'atings', 1), (u'son', 7, u'n'), (u'thomas', 3, u'n'), (u'show', 17, u'v'), (u'agreed', 10, u'v'), (u'recipe', 1, u'n'), (u'design', 10, u'v'), (u'sites', 9, u'v'), (u'radio', 6, u'n'), (u'democrats', 6, u'n'), (u'bedroom', 9, u'n'), (u'soldiers', 9, u'n'), (u'chicken', 10, u'n'), (u'bail', 1, u'v'), (u'networks', 2, u'n'), (u'decade', 1, u'n'), (u'producer', 4, u'n'), (u'knicks', 7), (u'justice', 9, u'n'), (u'menu', 9, u'n'), (u'writes', 5, u'v'), (u'winner', 1, u'n'), (u'written', 5, u'v'), (u'crime', 1, u'n'), (u'penalty', 1, u'n'), (u'bush', 7, u'n'), (u'black', 8, u's'), (u'hockey', 2, u'n'), (u'fuel', 10, u'v'), (u'rinking', 1), (u'communist', 9, u'n'), (u'rice', 1, u'n'), (u'local', 9, u'a'), (u'nj', 1, u'n'), (u'photographs', 1, u'v'), (u'ranking', 1, u'v'), (u'hungarian', 1, u'n'), (u'king', 4, u'n'), (u'contracts', 1, u'v'), (u'iesta', 1), (u'photography', 1, u'n'), (u'television', 9, u'n'), (u'trees', 6, u'v'), (u'baghdad', 6, u'n'), (u'ervice', 1), (u'international', 9, u'a'), (u'buyer', 1, u'n'), (u'oney', 1), (u'sunni', 8, u'n'), (u'randfather', 1), (u'prime', 2, u's'), (u'bar', 8, u'n'), (u'artist', 9, u'n'), (u'married', 9, u'a'), (u'ealthcare', 1), (u'taxes', 1, u'v'), (u'teams', 6, u'n'), (u'bad', 3, u's'), (u'miles', 5, u'n'), (u'esidents', 1), (u'ohio', 4, u'n'), (u'wrote', 5, u'v'), (u'restaurants', 6, u'n'), (u'shiite', 9, u'n'), (u'learn', 1, u'v'), (u'art', 13, u'n'), (u'olitics', 3), (u'anning', 3), (u'national', 9, u'a'), (u'sex', 5, u'n'), (u'elected', 1, u'v'), (u'officials', 39, u'n'), (u'college', 7, u'n'), (u'are', 2, u'v'), (u'sea', 1, u'n'), (u'nternet', 1), (u'transportation', 2, u'n'), (u'news', 3, u'n'), (u'flavor', 1, u'n'), (u'best', 3, u's'), (u'points', 8, u'n'), (u'israeli', 7, u'a'), (u'hrysler', 1), (u'nuclear', 8, u'a'), (u'review', 9, u'n'), (u'representatives', 1, u'n'), (u'state', 36, u'n'), (u'won', 6, u'v'), (u'pets', 1, u'n'), (u'diamonds', 1, u'n'), (u'ations', 3), (u'available', 1, u's'), (u'notice', 8, u'n'), (u'men', 6, u'n'), (u'terms', 11, u'n'), (u'nature', 2, u'n'), (u'team', 12, u'n'), (u'jr', 3, u'n'), (u'boss', 1, u'n'), (u'efficiency', 1, u'n'), (u'harvard', 4, u'n'), (u'awards', 2, u'n'), (u'oker', 1, u's'), (u'bituary', 1), (u'genre', 7, u'n'), (u'police', 11, u'v'), (u'lawsuit', 1, u'n'), (u'ccomodation', 1), (u'league', 15, u'n'), (u'climate', 1, u'n'), (u'accident', 1, u'n'), (u'brown', 5, u'n'), (u'restaurant', 8, u'n'), (u'country', 7, u'n'), (u'drug', 10, u'v'), (u'display', 1, u'n'), (u'ouse', 1, u'n'), (u'players', 17, u'n'), (u's', 2, u'n'), (u'hite', 1), (u'bronx', 8, u'n'), (u'senator', 8, u'n'), (u'grooming', 1, u'v'), (u'traded', 1, u'v'), (u'asked', 1, u'v'), (u'jersey', 7, u'n'), (u'negotiation', 1, u'n'), (u'and', 5), (u'groups', 1, u'n'), (u'cancer', 9, u'n'), (u'color', 1, u'n'), (u'community', 8, u'n'), (u'jets', 6, u'n'), (u'anti', 4, u'a'), (u'article', 4, u'n'), (u'eediest', 1), (u'li', 2, u'n'), (u'speak', 1, u'v'), (u'arts', 7, u'n'), (u'ocal', 1), (u'political', 17, u'a'), (u'vacation', 4, u'n'), (u'strategy', 2, u'n'), (u'convicted', 1, u'v'), (u'secret', 6, u's'), (u'offers', 1, u'v'), (u'west', 1, u'n'), (u'interest', 1, u'n'), (u'killed', 9, u'v'), (u'exhibition', 8, u'n'), (u'firm', 6, u's'), (u'life', 18, u'n'), (u'shopping', 3, u'v'), (u'gay', 6, u's'), (u'eastern', 1, u's'), (u'drugs', 8, u'v'), (u'omputer', 1), (u'republicans', 5, u'n'), (u'gas', 7, u'n'), (u'palestinian', 7, u'a'), (u'al', 2, u'n'), (u'fund', 14, u'v'), (u'minister', 10, u'n'), (u'ovies', 1), (u'child', 6, u'n'), (u'prices', 14, u'n'), (u'plants', 8, u'v'), (u'criminal', 2, u's'), (u'senat', 1), (u'budget', 6, u'n'), (u'value', 1, u'n'), (u'air', 8, u'n'), (u'will', 1, u'v'), (u'teachers', 9, u'n'), (u'newspaper', 1, u'n'), (u'property', 11, u'n'), (u'study', 9, u'n'), (u'layer', 1, u'n'), (u'layoff', 1, u'n'), (u'bathrooms', 8, u'n'), (u'century', 9, u'n'), (u'resident', 3, u'a'), (u'site', 9, u'n'), (u'middle', 9, u'n'), (u'prosecutor', 1, u'n'), (u'properties', 1, u'n'), (u'contract', 13, u'v'), (u'in', 1, u's'), (u'foreign', 9, u'a'), (u'technology', 9, u'n'), (u'obituary', 1, u'n'), (u'memorial', 10, u'n'), (u'education', 9, u'n'), (u'author', 8, u'n'), (u'pay', 7, u'v'), (u'make', 8, u'v'), (u'administration', 7, u'n'), (u'textile', 1, u'a'), (u'economy', 4, u'n'), (u'ews', 1, u'n'), (u'party', 11, u'n'), (u'european', 8, u'a'), (u'development', 10, u'n'), (u'oil', 7, u'n'), (u'lawyers', 8, u'n'), (u'ratings', 1, u'v'), (u'social', 1, u'a'), (u'closings', 1, u'v'), (u'yesterday', 2, u'r'), (u'director', 14, u'n'), (u'bituaries', 3), (u'student', 6, u'n'), (u'opinion', 1, u'n'), (u'nation', 1, u'n'), (u'colts', 7, u'n'), (u'warming', 1, u's'), (u'recent', 6, u's'), (u'eams', 2), (u'jurors', 1, u'n'), (u'charges', 9, u'v'), (u'iraqis', 7, u'n'), (u'no', 1, u'r'), (u'ocean', 1, u'n'), (u'media', 1, u'n'), (u'china', 9, u'n'), (u'mother', 10, u'n'), (u'hearts', 1, u'n'), (u'the', 2), (u'audio', 1, u'n'), (u'peration', 1), (u'researchers', 8, u'n'), (u'left', 6, u'v'), (u'summer', 1, u'n'), (u'onda', 1), (u'stores', 8, u'n'), (u'sentence', 1, u'n'), (u'money', 10, u'n'), (u'laptop', 1, u'n'), (u'executive', 8, u'n'), (u'domestic', 1, u'a'), (u'foot', 6, u'n'), (u'fighters', 1, u'n'), (u'rooms', 2, u'n'), (u'victim', 1, u'n'), (u'alternative', 1, u's'), (u'ist', 1), (u'eaths', 2), (u'web', 10, u'n'), (u'death', 14, u'n'), (u'campaign', 11, u'n'), (u'field', 5, u'n'), (u'residential', 3, u'a'), (u'workers', 7, u'n'), (u'demographic', 1, u'a'), (u'nline', 1), (u'other', 2, u's'), (u'parents', 19, u'n'), (u'board', 11, u'n'), (u'beloved', 6, u's'), (u'lection', 1), (u'east', 4, u'n'), (u'ski', 8, u'v'), (u'ravel', 1, u'v'), (u'real', 16, u's'), (u'vendor', 1, u'n'), (u'government', 31, u'n'), (u'africa', 1, u'n'), (u'couple', 1, u'n'), (u'test', 7, u'v'), (u'game', 17, u'n'), (u'judge', 8, u'v'), (u'world', 24, u'n'), (u'apple', 8, u'n'), (u'amputation', 1, u'n'), (u'lost', 1, u'v'), (u'toyota', 8, u'n'), (u'eep', 1), (u'ootball', 1), (u'offices', 1, u'n'), (u'night', 12, u'n'), (u'security', 10, u'n'), (u'works', 5, u'v'), (u'antique', 1, u's'), (u'www', 4, u'n'), (u'amily', 1), (u'jews', 7, u'n'), (u'deal', 10, u'v'), (u'people', 48, u'n'), (u'senate', 10, u'n'), (u'church', 18, u'n'), (u'back', 6, u'v'), (u'dead', 5, u's'), (u'hair', 6, u'n'), (u'clubs', 1, u'n'), (u'growth', 8, u'n'), (u'election', 9, u'n'), (u'escape', 1, u'n'), (u'home', 18, u'n'), (u'ealth', 3), (u'dvice', 1), (u'est', 1, u'n'), (u'caribbean', 1, u'n'), (u'decision', 1, u'n'), (u'fox', 9, u'n'), (u'legal', 10, u'a'), (u'seller', 3, u'n'), (u'students', 9, u'n'), (u'maliki', 5), (u'niversity', 1), (u'temple', 1, u'n'), (u'patient', 1, u'n'), (u'power', 6, u'n'), (u'schedule', 1, u'v'), (u'ocation', 1), (u'leadership', 1, u'n'), (u'super', 5, u's'), (u'by', 1, u'r'), (u'artin', 1), (u'faith', 1, u'n'), (u'island', 16, u'n'), (u'industry', 1, u'n'), (u'citizens', 1, u'n'), (u'location', 5, u'n'), (u'o', 1, u'n'), (u'drama', 1, u'n'), (u'dinner', 8, u'n'), (u'militia', 1, u'n'), (u'testimony', 2, u'n'), (u'executives', 7, u'n'), (u'owl', 1, u'n'), (u'clinton', 7, u'n'), (u'casualty', 1, u'n'), (u'civil', 1, u'a'), (u'travelers', 23, u'n'), (u'attorney', 8, u'n'), (u'airlines', 11, u'n'), (u'weather', 10, u'v'), (u'homeless', 1, u's'), (u'parties', 1, u'n'), (u'computer', 9, u'n'), (u'area', 1, u'n'), (u'spending', 1, u'v'), (u'friends', 8, u'n'), (u'museum', 8, u'n'), (u'long', 10, u'a'), (u'gallery', 9, u'n'), (u'jewish', 7, u'a'), (u'editor', 12, u'n'), (u'series', 10, u'n'), (u'cultures', 1, u'n'), (u'war', 32, u'n'), (u'irthday', 1), (u'billion', 6, u'n'), (u'mailer', 1, u'n'), (u'medium', 1, u'n'), (u'jury', 3, u'n'), (u'manufacturers', 1, u'n'), (u'olidays', 1), (u'funds', 8, u'v'), (u'brand', 1, u'n'), (u'pastor', 6, u'n'), (u'ford', 8, u'n'), (u'ork', 6), (u'brain', 5, u'n'), (u'gain', 1, u'v'), (u'survived', 6, u'v'), (u'line', 6, u'n'), (u'he', 2, u'n'), (u'made', 7, u'v'), (u'signed', 1, u'v'), (u'economic', 2, u's'), (u'emissions', 8, u'n'), (u'played', 4, u'v'), (u'minutes', 1, u'n'), (u'called', 2, u'v'), (u'partnerships', 1, u'n'), (u'medication', 1, u'n'), (u'deaths', 9, u'n'), (u'tournament', 1, u'n'), (u'sales', 12, u'n'), (u'evidence', 1, u'v'), (u'cbs', 3), (u'politics', 6, u'n'), (u'ing', 1), (u'campus', 7, u'n'), (u'film', 9, u'n'), (u'cream', 8, u'v'), (u'misstated', 2, u'v'), (u'mutual', 1, u'a'), (u'lemon', 1, u'n'), (u'ingredients', 1, u'n'), (u'percent', 15, u'n'), (u'event', 1, u'n'), (u'ny', 3, u'n'), (u'politicians', 2, u'n'), (u'book', 8, u'n'), (u'branch', 1, u'n'), (u'digital', 10, u'a'), (u'department', 6, u'n'), (u'europe', 2, u'n'), (u'games', 10, u'n'), (u'congress', 9, u'n'), (u'ases', 1, u'n'), (u'eyton', 2), (u'football', 9, u'n'), (u'diet', 1, u'n'), (u'otice', 1), (u'ather', 1), (u'brands', 1, u'n'), (u'ransactions', 2), (u'presidential', 10, u'a'), (u'sland', 1), (u'died', 8, u'v'), (u'building', 17, u'v'), (u'simon', 1, u'n'), (u'spades', 1, u'n'), (u'wife', 13, u'n'), (u'space', 8, u'n'), (u'microsoft', 9), (u'directors', 1, u'n'), (u'time', 25, u'n'), (u'prizes', 1, u'v')]
# with open("dataset/linguistic_analysis_of_words/refined_topic_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# pos = [(u'coach', 1, u'n'), (u'producer', 1, u'n'), (u'show', 1, u'v'), (u'money', 1, u'n'), (u'executive', 2, u'n'), (u'years', 1, u'n'), (u'nations', 1, u'n'), (u'radio', 1, u'n'), (u'cuts', 1, u'v'), (u'soldiers', 1, u'n'), (u'children', 1, u'n'), (u'knicks', 1), (u'father', 2, u'n'), (u'iraqi', 1, u'a'), (u'bush', 2, u'n'), (u'board', 1, u'n'), (u'policy', 1, u'n'), (u'giants', 1, u'n'), (u'good', 1, u's'), (u'risk', 1, u'n'), (u'no-trump', 1, u'n'), (u'game', 2, u'n'), (u'world', 1, u'n'), (u'trump ', 1), (u'james', 1, u'n'), (u'university', 1, u'n'), (u'married', 1, u'a'), (u'toyota', 1, u'n'), (u'grandfather', 1, u'n'), (u'queen', 1, u'n'), (u'architecture', 1, u'n'), (u'night', 1, u'n'), (u'small', 1, u's'), (u'anti', 1, u'a'), (u'works', 1, u'v'), (u'husband', 2, u'v'), (u'restaurants', 2, u'n'), (u'deal', 1, u'v'), (u'people', 3, u'n'), (u'climate change', 1), (u'energy', 2, u'n'), (u'Internet', 1, u'n'), (u'play', 1, u'v'), (u'phone', 1, u'n'), (u'hair', 3, u'n'), (u'clubs', 1, u'n'), (u'officials', 1, u'n'), (u'college', 1, u'n'), (u'year', 1, u'n'), (u'transportation', 1, u'n'), (u'calendar', 1, u'n'), (u'teams', 1, u'n'), (u'israeli', 1, u'a'), (u'business', 1, u'n'), (u'paintings', 1, u'v'), (u'entertainment', 1, u'n'), (u'grandmother', 1, u'n'), (u'companies', 4, u'n'), (u'state', 1, u'n'), (u'won', 1, u'v'), (u'diamonds', 1, u'n'), (u'Drinking', 3, u'v'), (u'real estate profiles', 1), (u'notice', 3, u'n'), (u'million', 1, u'n'), (u'iran', 1, u'n'), (u'power', 3, u'n'), (u'cars', 1, u'n'), (u'team', 2, u'n'), (u'paid', 3, u'v'), (u'ethanol', 1, u'n'), (u'jets', 1, u'n'), (u'article', 1, u'n'), (u'iraq', 3, u'n'), (u'change', 1, u'v'), (u'great', 1, u's'), (u'kids', 1, u'n'), (u'restaurant', 1, u'n'), (u'palestinian', 1, u'a'), (u'david', 1, u'n'), (u'players', 1, u'n'), (u'american', 1, u'n'), (u'games', 3, u'n'), (u'published', 1, u'v'), (u'corrections', 4, u'n'), (u'military', 1, u'a'), (u'residents', 1, u'n'), (u'executives', 1, u'n'), (u'Obituary', 1, u'n'), (u'major', 1, u'a'), (u'family', 3, u'n'), (u'community', 1, u'n'), (u'son', 1, u'n'), (u'patriots', 1, u'n'), (u'church', 1, u'n'), (u'light', 3, u's'), (u'city', 1, u'n'), (u'line', 2, u'n'), (u'management', 1, u'n'), (u'troops', 1, u'n'), (u'army', 1, u'n'), (u'bears', 1, u'v'), (u'museum', 1, u'n'), (u'played', 1, u'v'), (u'cats', 1, u'n'), (u'call', 1, u'v'), (u'house', 1, u'n'), (u'john', 2, u'n'), (u'war', 2, u'n'), (u'exhibition', 1, u'n'), (u'firm', 1, u's'), (u'life', 1, u'n'), (u'dummy', 1, u'n'), (u'club', 3, u'n'), (u'company', 3, u'n'), (u'gas', 2, u'n'), (u'pastor', 1, u'n'), (u'oil', 2, u'n'), (u'ford', 1, u'n'), (u'environmental', 2, u'a'), (u'train', 1, u'v'), (u'survived', 1, u'v'), (u'Healthcare', 1, u'n'), (u'prices', 1, u'n'), (u'cases', 1, u'n'), (u'earth', 1, u'n'), (u'king', 1, u'n'), (u'made', 2, u'v'), (u'furnishings', 1, u'n'), (u'car', 1, u'n'), (u'budget', 1, u'n'), (u'cat', 1, u'n'), (u'states', 1, u'n'), (u'emissions', 1, u'n'), (u'learn', 1, u'v'), (u'cards', 1, u'n'), (u'called', 1, u'v'), (u'history', 1, u'n'), (u'exhibit', 1, u'v'), (u'deaths', 3, u'n'), (u'correction', 3, u'n'), (u'tax', 1, u'v'), (u'israel', 1, u'n'), (u'glass', 3, u'n'), (u'dog', 1, u'n'), (u'high', 1, u'n'), (u'player', 2, u'n'), (u'Politicians', 1, u'n'), (u'smartphone', 1), (u'home', 3, u'n'), (u'foreign', 1, u'a'), (u'misstated', 2, u'v'), (u'author', 1, u'n'), (u'percent', 2, u'n'), (u'dining', 1, u'v'), (u'points', 1, u'n'), (u'chairman', 2, u'v'), (u'interior', 1, u's'), (u'events', 1, u'n'), (u'plant', 1, u'v'), (u'added', 1, u'v'), (u'closings', 1, u'v'), (u'global warming', 1), (u'hand', 1, u'n'), (u'director', 1, u'n'), (u'plan', 1, u'v'), (u'president', 3, u'n'), (u'law', 1, u'n'), (u'colts', 1, u'n'), (u'building', 1, u'v'), (u'cellphone', 1, u'n'), (u'spades', 1, u'n'), (u'center', 1, u'n'), (u'johnson', 1, u'n'), (u'wife', 2, u'n'), (u'mobile', 1, u's'), (u'poker', 1, u'n'), (u'space', 6, u'n'), (u'baghdad', 3, u'n'), (u'chief', 1, u'n'), (u'neediest', 1, u's'), (u'green', 1, u'n'), (u'mother', 1, u'n'), (u'hearts', 1, u'n'), (u'painting', 1, u'v'), (u'playing', 1, u'v')]
# with open("dataset/linguistic_analysis_of_words/split_theme_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# pos = [(u'coach', 3, u'n'), (u'dish', 1, u'n'), (u'children', 6, u'n'), (u'foreign nations', 1), (u'apartment', 3, u'n'), (u'father', 4, u'n'), (u'iraqi', 1, u'a'), (u'green friendly', 1), (u'street', 2, u'n'), (u'risk', 2, u'n'), (u'school', 1, u'n'), (u'companies', 4, u'n'), (u'democrat', 7, u'n'), (u'team', 2, u'n'), (u'small', 1, u's'), (u'Super Bowl', 2), (u'holocaust', 1, u'n'), (u'chef', 2, u'n'), (u'cost', 1, u'n'), (u'design', 3, u'v'), (u'lawyer', 3, u'n'), (u'investment', 5, u'n'), (u'paintings', 3, u'v'), (u'asia', 1, u'n'), (u'cars', 6, u'n'), (u'new', 1, u's'), (u'public', 3, u'n'), (u'iran', 4, u'n'), (u'funeral', 2, u'n'), (u'men', 1, u'n'), (u'Health Care', 2), (u'baseball', 4, u'n'), (u'ethanol', 2, u'n'), (u'iraq', 1, u'n'), (u'change', 3, u'v'), (u'daughter', 2, u'n'), (u'employees', 1, u'n'), (u'guilty', 1, u'a'), (u'trial', 1, u'n'), (u'airport', 1, u'n'), (u'published', 3, u'v'), (u'military', 6, u'a'), (u'residents', 1, u'n'), (u'york', 5, u'n'), (u'named', 1, u'v'), (u'campaign', 3, u'n'), (u'transit', 2, u'v'), (u'litigators', 1, u'n'), (u'Football Teams', 3), (u'market', 4, u'n'), (u'troops', 1, u'n'), (u'army', 1, u'n'), (u'eastern europe', 1), (u'hospital', 2, u'n'), (u'century', 1, u'n'), (u'sports', 1, u'n'), (u'music', 1, u'n'), (u'black', 3, u's'), (u'loving', 3, u'v'), (u'israel', 1, u'n'), (u'company', 9, u'n'), (u'chocolate', 1, u'n'), (u'phone', 1, u'n'), (u'baby', 1, u'n'), (u'cases', 3, u'n'), (u'women', 4, u'n'), (u'town', 1, u'n'), (u'middle', 1, u'n'), (u'science', 1, u'n'), (u'work', 1, u'v'), (u'reviews', 1, u'n'), (u'movies', 2, u'n'), (u'freedom', 1, u'n'), (u'history', 4, u'n'), (u'estate', 2, u'n'), (u'tax', 2, u'v'), (u'high', 4, u'n'), (u'Relatives', 1, u'n'), (u'numbers', 1, u'n'), (u'viewers', 2, u'n'), (u'ceremony', 1, u'n'), (u'united', 1, u'v'), (u'court', 3, u'n'), (u'winter', 1, u'v'), (u'travel', 5, u'v'), (u'beach', 1, u'v'), (u'stock', 2, u'n'), (u'designer', 4, u'n'), (u'spitzer', 1), (u'List', 1, u'v'), (u'president', 6, u'n'), (u'Residents', 1, u'n'), (u'law', 4, u'n'), (u'man', 3, u'n'), (u'Marriages', 2, u'n'), (u'Politics', 2, u'n'), (u'democratic', 2, u'a'), (u'playing', 1, u'v'), (u'Obituary', 1, u'n'), (u'years', 1, u'n'), (u'committee', 1, u'n'), (u'nets', 1, u'n'), (u'mayor', 2, u'n'), (u'board of directors', 1), (u'style', 2, u'n'), (u'police', 3, u'v'), (u'Transactions', 1, u'n'), (u'writing', 1, u'v'), (u'late', 4, u's'), (u'resort', 1, u'n'), (u'production', 1, u'n'), (u'listing', 1, u'v'), (u'mail', 1, u'n'), (u'holiday', 1, u'n'), (u'senat', 1), (u'good', 2, u's'), (u'finance', 1, u'n'), (u'food', 1, u'n'), (u'schools', 4, u'n'), (u'republican', 7, u'n'), (u'day', 1, u'n'), (u'presidential', 4, u'a'), (u'meat', 2, u'n'), (u'january', 4, u'n'), (u'university', 1, u'n'), (u'countries', 2, u'n'), (u'economy', 2, u'n'), (u'financial', 3, u'a'), (u'city service', 1), (u'series', 1, u'n'), (u'fish', 1, u'n'), (u'Sports', 1, u'n'), (u'society', 2, u'n'), (u'year', 3, u'n'), (u'insurance', 3, u'n'), (u'space', 2, u'n'), (u'god', 2, u'n'), (u'research', 4, u'v'), (u'investigation', 2, u'n'), (u'health', 2, u'n'), (u'internet', 1, u'n'), (u'shows', 1, u'v'), (u'wines', 2, u'v'), (u'Notice Deaths', 1), (u'contract terms', 1), (u'University', 1, u'n'), (u'million', 3, u'n'), (u'free', 1, u'v'), (u'square foot', 1), (u'basketball', 4, u'n'), (u'struggle', 1, u'v'), (u'Corrections', 1, u'n'), (u'care', 3, u'n'), (u'times', 3, u'n'), (u'american', 6, u'n'), (u'residential sales', 1), (u'corrections', 2, u'n'), (u'cheese', 2, u'v'), (u'delicious', 1, u's'), (u'vote', 2, u'v'), (u'art', 1, u'n'), (u'pleaded', 1, u'v'), (u'city', 6, u'n'), (u'story', 2, u'n'), (u'management', 5, u'n'), (u'service', 3, u'n'), (u'system', 3, u'n'), (u'relations', 1, u'n'), (u'new york', 1), (u'listed', 2, u'v'), (u'Date', 1, u'n'), (u'hollywood', 1, u'n'), (u'Iraq', 1, u'n'), (u'finances', 1, u'n'), (u'store', 5, u'n'), (u'season', 4, u'v'), (u'hotel', 3, u'n'), (u'park', 1, u'n'), (u'doctors', 2, u'n'), (u'king', 1, u'n'), (u'television', 2, u'n'), (u'stock market', 1), (u'war', 11, u'n'), (u'project', 3, u'v'), (u'patients', 2, u'n'), (u'New York', 3), (u'Local News', 1), (u'russia', 1, u'n'), (u'exhibit', 1, u'v'), (u'fashion', 5, u'n'), (u'investors', 3, u'n'), (u'correction', 1, u'n'), (u'sports teams', 1), (u'tonight', 1, u'r'), (u'medical', 4, u'a'), (u'car', 1, u'n'), (u'ratings', 1, u'v'), (u'dining', 2, u'v'), (u'chairman', 3, u'v'), (u'online', 2, u'a'), (u'quarterback', 1, u'n'), (u'theatre', 1, u'n'), (u'price', 1, u'n'), (u'paid', 3, u'v'), (u'brooklyn', 2, u'n'), (u'plan', 1, u'v'), (u'letter', 1, u'n'), (u'america', 1, u'n'), (u'gallery', 7, u'n'), (u'united nations', 1), (u'professor', 1, u'n'), (u'disease', 2, u'n'), (u'neediest', 5, u's'), (u'Election', 1, u'n'), (u'painting', 2, u'v'), (u'microsoft', 2), (u'son', 1, u'n'), (u'show', 4, u'v'), (u'agreed', 1, u'v'), (u'Healthcare', 1, u'n'), (u'Religion', 2, u'n'), (u'radio', 1, u'n'), (u'democrats', 2, u'n'), (u'earth', 2, u'n'), (u'chicken', 1, u'n'), (u'knicks', 1), (u'justice', 1, u'n'), (u'menu', 4, u'n'), (u'crime', 1, u'n'), (u'bush', 1, u'n'), (u'candidates', 1, u'n'), (u'fuel', 1, u'v'), (u'communist', 1, u'n'), (u'local', 3, u'a'), (u'The Neediest Cases', 1), (u'Bridegroom', 1, u'n'), (u'wedding', 2, u'n'), (u'bar', 1, u'n'), (u'artist', 4, u'n'), (u'married', 3, u'a'), (u'teams', 4, u'n'), (u'husband', 3, u'v'), (u'restaurants', 4, u'n'), (u'art news', 1), (u'climate change', 1), (u'national', 2, u'a'), (u'manning', 4, u'v'), (u'officials', 5, u'n'), (u'college', 2, u'n'), (u'transportation', 1, u'n'), (u'calendar', 2, u'n'), (u'nations', 1, u'n'), (u'best', 1, u's'), (u'federal', 3, u'a'), (u'New York City', 2), (u'review', 4, u'n'), (u'sites', 1, u'v'), (u'state', 6, u'n'), (u'marriage', 6, u'n'), (u'europe', 1, u'n'), (u'notice', 3, u'n'), (u'terms', 2, u'n'), (u'boss', 1, u'n'), (u'awards', 1, u'n'), (u'article', 1, u'n'), (u'middle east', 2), (u'lawsuit', 1, u'n'), (u'league', 1, u'n'), (u'accused', 1, u'v'), (u'restaurant', 1, u'n'), (u'country', 2, u'n'), (u'contract', 2, u'v'), (u'foreign', 2, u'a'), (u'players', 1, u'n'), (u'games', 4, u'n'), (u'bronx', 2, u'n'), (u'grooming', 1, u'v'), (u'jersey', 2, u'n'), (u'non green', 1), (u'cancer', 2, u'n'), (u'community', 2, u'n'), (u'news', 1, u'n'), (u'arts', 3, u'n'), (u'best seller', 1), (u'political', 14, u'a'), (u'vacation', 1, u'n'), (u'strategy', 1, u'n'), (u'secret', 1, u's'), (u'Obituaries', 2, u'n'), (u'killed', 2, u'v'), (u'life', 4, u'n'), (u'shopping', 2, u'v'), (u'Poland', 1, u'n'), (u'republicans', 3, u'n'), (u'gas', 2, u'n'), (u'fund', 2, u'v'), (u'minister', 1, u'n'), (u'child', 2, u'n'), (u'health insurance', 3), (u'case', 2, u'n'), (u'novel', 1, u's'), (u'Deaths', 1, u'n'), (u'budget', 4, u'n'), (u'Colors', 1, u'n'), (u'teachers', 3, u'n'), (u'Church', 1, u'n'), (u'property', 3, u'n'), (u'study', 4, u'n'), (u'played', 1, u'v'), (u'player', 2, u'n'), (u'stock prices', 1), (u'drug', 1, u'v'), (u'technology', 6, u'n'), (u'NY NBA Teams', 1), (u'memorial', 3, u'n'), (u'author', 4, u'n'), (u'home sales', 1), (u'administration', 1, u'n'), (u'political party', 1), (u'events', 1, u'n'), (u'european', 1, u'a'), (u'development', 8, u'n'), (u'lawyers', 1, u'n'), (u'mountain', 1, u'n'), (u'social', 1, u'a'), (u'closings', 2, u'v'), (u'director', 1, u'n'), (u'colts', 1, u'n'), (u'center', 1, u'n'), (u'charges', 2, u'v'), (u'ocean', 1, u'n'), (u'mother', 3, u'n'), (u'audio', 1, u'n'), (u'soviet', 2, u'a'), (u'researchers', 4, u'n'), (u'stores', 5, u'n'), (u'sentence', 1, u'n'), (u'money', 4, u'n'), (u'laptop', 2, u'n'), (u'Cards', 3, u'n'), (u'Internet', 2, u'n'), (u'flavor', 1, u'n'), (u'death', 4, u'n'), (u'family', 14, u'n'), (u'residential', 3, u'a'), (u'workers', 1, u'n'), (u'Holidays', 1, u'n'), (u'parents', 3, u'n'), (u'exhibition', 3, u'n'), (u'beloved', 2, u's'), (u'Brands', 1, u'n'), (u'real estate', 3), (u'municipal', 1, u'a'), (u'government', 11, u'n'), (u'couple', 1, u'n'), (u'game', 5, u'n'), (u'judge', 2, u'v'), (u'world', 6, u'n'), (u'Martin Luther King', 1), (u'toyota', 3, u'n'), (u'works', 5, u'v'), (u'attorney', 2, u'n'), (u'jews', 2, u'n'), (u'people', 8, u'n'), (u'senate', 1, u'n'), (u'church', 4, u'n'), (u'back', 2, u'v'), (u'dead', 2, u's'), (u'hair', 2, u'n'), (u'economic', 1, u's'), (u'election', 1, u'n'), (u'home', 2, u'n'), (u'caribbean', 1, u'n'), (u'seller', 1, u'n'), (u'Drinking', 1, u'v'), (u'business', 5, u'n'), (u'Groom', 1, u'v'), (u'leadership', 1, u'n'), (u'passed away', 1), (u'Bride ', 1), (u'executives', 2, u'n'), (u'island', 2, u'n'), (u'citizens', 1, u'n'), (u'dinner', 2, u'n'), (u'Best', 1, u's'), (u'software', 4, u'n'), (u'travelers', 1, u'n'), (u'airlines', 1, u'n'), (u'homeless', 1, u's'), (u'artists', 4, u'n'), (u'computer', 3, u'n'), (u'museum', 3, u'n'), (u'Birthday', 1, u'n'), (u'editor', 4, u'n'), (u'house', 2, u'n'), (u'NBA', 1), (u'energy', 1, u'n'), (u'jewish', 2, u'a'), (u'funds', 2, u'v'), (u'brand', 1, u'n'), (u'American people', 1), (u'pastor', 2, u'n'), (u'ford', 1, u'n'), (u'holiday office closings', 1), (u'line', 2, u'n'), (u'made', 2, u'v'), (u'major league baseball', 1), (u'Locations', 1, u'n'), (u'growth', 1, u'n'), (u'emissions', 2, u'n'), (u'display', 1, u'n'), (u'USA', 1, u'n'), (u'deaths', 1, u'n'), (u'sales', 2, u'n'), (u'health care', 1), (u'politics', 6, u'n'), (u'education', 7, u'n'), (u'cream', 1, u'v'), (u'misstated', 1, u'v'), (u'percent', 1, u'n'), (u'ny', 1, u'n'), (u'digital', 1, u'a'), (u'department', 1, u'n'), (u'congress', 1, u'n'), (u'students', 4, u'n'), (u'football', 5, u'n'), (u'stocks', 1, u'n'), (u'died', 1, u'v'), (u'building', 3, u'v'), (u'time', 2, u'n'), (u'international', 6, u'a')]
# with open("dataset/linguistic_analysis_of_words/word_order_pos.csv","w") as fp:
# 	writer = csv.writer(fp)
# 	writer.writerows(pos)

# exit()


##########################################################################
##########################################################################
##### REMOVE WORDS : DETAIL
##########################################################################
##########################################################################
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())
# freq_removal_by_index = {i:0 for i in range(20)}
# freq_removal_created_words = 0
# for tid,tlist in TOPICS.iteritems():
# 	original_words = [w['word'] for w in topicJSON[str(tid)]['words'][:20]]
# 	for rid, topic in tlist.iteritems():
# 		logs = topic["log_data"]
# 		rw_list = [e["message"] for e in logs if e["event"]=="REMOVE_WORDS"]
# 		for rw in rw_list:
# 			if rw in original_words: 
# 				freq_removal_by_index[original_words.index(rw)]+=1
# 			else:
# 				freq_removal_created_words+=1
# print freq_removal_by_index
# print freq_removal_created_words
# # CALCULATING PEARSON CORRELATION (BUT IT ASSUMES THE DATA IS LINEAR)
# print stats.pearsonr(freq_removal_by_index.keys(), freq_removal_by_index.values())
# (slope, intercept, r,p,stderr) = stats.linregress(freq_removal_by_index.keys(), freq_removal_by_index.values())
# print "r-squared: ", r**2
# # CALCULATING SPEARMAN RANK-ORDER CORRELATION (ASSUMING tHE DATA IS MONOTONIC)
# print "SPEARMAN: ", stats.spearmanr(freq_removal_by_index.keys(), freq_removal_by_index.values())

# exit()


##########################################################################
##########################################################################
##### CHANGE WORD ORDER : DETAIL
##########################################################################
##########################################################################
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())
# freq_by_index = {i:0 for i in range(20)}
# freq_created_words = 0
# all_count = 0
# topic_count = 0
# topic_count_all = 0

# count = {"up":0, "down":0}
# for tid,tlist in TOPICS.iteritems():
# 	original_words = [w['word'] for w in topicJSON[str(tid)]['words'][:20]]
# 	for rid, topic in tlist.iteritems():
# 		logs = topic["log_data"]
# 		w_list = [e["message"] for e in logs if e["event"]=="CHANGE_WORD_ORDER"]
# 		all_count+=len(w_list)
# 		topic_count_all += 1
# 		if len(w_list)>0:
# 			topic_count += 1
# 		improved_words = topic["improved_theme"]
# 		for w in w_list:
# 			if w in original_words: 
# 				idx_from = original_words.index(w)
# 				freq_by_index[idx_from]+=1
# 				idx_to = -1
# 				for iw_idx, iw in enumerate(improved_words):
# 					if w in iw:
# 						idx_to = iw_idx
# 						break
# 				if idx_to != -1:
# 					if idx_from > idx_to:  ## MOVING UP
# 						count["up"]+=1
# 					if idx_from < idx_to:
# 						count["down"]+=1
# 				else:
# 					pass  # MOVED WORD NOT DISAPPEARED EVENTUALLY
# 			else:
# 				freq_created_words+=1
# print topic_count, topic_count_all, float(topic_count) / float(topic_count_all)
# print freq_by_index
# print "SPEARMAN: ", stats.spearmanr(freq_by_index.keys(), freq_by_index.values())
# print all_count
# print "CREATED WORDS:", freq_created_words
# print count
# print stats.pearsonr(freq_by_index.keys(), freq_by_index.values())
# (slope, intercept, r,p,stderr) = stats.linregress(freq_by_index.keys(), freq_by_index.values())
# print "r-squared: ", r**2
# exit()


### OLD CODE
	# 		words_moved = []
	# 		for w in [e["message"] for e in logs if e["event"]=="CHANGE_WORD_ORDER"]:
	# 			idx_from = original_theme.index(w) if w in original_theme else 20
	# 			idx_to =  improved_theme.index(w) if w in improved_theme else 20
	# 			if idx_to<20:
	# 				if idx_from > idx_to:
	# 					count["up"]+=1
	# 				elif idx_from < idx_to:
	# 					count["down"]+=1
	# 			if idx_from==20:  ## IF THE WORDs DIDN't EXIST INtHE ORGINIAL 
	# 				repositioned_new_words.append(w)
	# 			words_moved.append((w, idx_from, idx_to))
	# 			try:
	# 				pos_matrix[idx_from][idx_to]+=1
	# 			except IndexError:
	# 				print idx_from, idx_to
	# 		# print original_theme
	# 		# print improved_theme
	# 		# print words_moved
	# 		all_logs_per_topic[tid].append(words_moved)
# all_changes = sum([sum([len(d)for d in data]) for tid,data in all_logs_per_topic.iteritems()])
# changes_per_topic =  sum([sum([len(d)for d in data]) for tid,data in all_logs_per_topic.iteritems()]) / 270.0
# # pp.pprint(all_logs_per_topic)
# pp.pprint(pos_matrix)

# print sum(pos_matrix[20])
# print len(repositioned_new_words)
# print count

# print sum([sum(l) for l in pos_matrix[0:5]])
# print sum([sum(l) for l in pos_matrix[5:10]])
# print sum([sum(l) for l in pos_matrix[10:15]])
# print sum([sum(l) for l in pos_matrix[15:20]])
	
# exit()


##########################################################################
##########################################################################
##### MERGE WORDS : DETAIL
##########################################################################
##########################################################################
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())
# words_merged = []
# for tid, tlist in TOPICS.iteritems():
# 	for rid, topic in tlist.iteritems():
# 		loglist = topic["log_data"]
# 		for w in [e["message"] for e in loglist if e["event"]=="MERGE_WORDS"]:
# 			words_merged.append(w)
# print words_merged
# num_merge_from = [len(message.split("->")[0].split(","))  for message in words_merged]
# data = num_merge_from
# print "# MERGED_WORDS:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# exit()

### WRITING CSV FILE 
# with open('merged_words.csv','w') as fp:
# 	writer = csv.writer(fp)
# 	for tid,loglist in all_logs_per_topic.iteritems():
# 		for log in loglist:
# 			for message in log:
# 				merged_words = message.split("->")[0]
# 				new_word = message.split("->")[1]
# 				writer.writerow((tid,merged_words,new_word))

### CHECKING THE NEW WORD IS AMONG MERGED WORDS 
# new_words_from_merged_words = []
# new_words_from_nowhere = []
# for tid,loglist in all_logs_per_topic.iteritems():
# 	for log in loglist:
# 		for message in log:
# 			merged_words = message.split("->")[0]
# 			new_words = message.split("->")[1].split(" ")
# 			flag=True
# 			for nw in new_words:
# 				if nw.lower() not in merged_words.lower():
# 					flag=False
# 			if flag:
# 				print "[IN] " + message
# 				new_words_from_merged_words.append(message)
# 			else:
# 				print message
# 				new_words_from_nowhere.append(message)
# print len(new_words_from_merged_words), len(new_words_from_merged_words) / 337.0
# print len(new_words_from_nowhere), len(new_words_from_nowhere) / 337.0
# exit()


# num_merged_words = arr_join([arr_join([[len(re.sub(r'\[.*\]','',d.split("->")[0]).split(',')) for d in event] for event in logs]) for i,logs in all_logs_per_topic.iteritems()])
# data = num_merged_words
# print "# MERGED_WORDS:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))

# # print [[[k.split("->")[0].split(",") for k in e] for e in tdata] for i,tdata in all_logs_per_topic.iteritems()]
# exit()


##########################################################################
##########################################################################
##### REMOVE DOCUMENTS : DETAIL
##########################################################################
##########################################################################
# freq_by_index = {i:0 for i in range(40)}
# # num_uniq_removed_docs = []
# number_of_topics_with_removed_documents = 0
# for tid,tlist in TOPICS.iteritems():
# 	removed_docs = []
# 	for rid, topic in tlist.iteritems():
# 		removed_docs += [idx for idx,boolean in enumerate(topic["improved_articles"]) if boolean==False]
# 	for id_removed_doc in removed_docs:
# 		freq_by_index[id_removed_doc] += 1
# 	# uniq_removed_docs = list(Set(removed_docs))
# 	# num_uniq_removed_docs.append(len(uniq_removed_docs))
# print freq_by_index
# # CALCULATING SPEARMAN RANK-ORDER CORRELATION (ASSUMING tHE DATA IS MONOTONIC)
# print "SPEARMAN: ", stats.spearmanr(freq_by_index.keys(), freq_by_index.values())
# # print num_uniq_removed_docs
# # data = num_uniq_removed_docs
# # print "# UNIQ DOCUMENTS REMOVED:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))
# exit()

# ### TOPIC QUALITY AFFECT REMOVAL RATE  ###
# data = [d for i,d in freq_removal_per_doc.iteritems()]
# freq_removal_per_topic = [sum(d) for d in data]
# fig = plt.figure(facecolor="white")
# plt.bar(range(0,31), freq_removal_per_topic, color='gray')
# plt.title("# REMOVED ARTICLES PER TOPIC", fontsize="14")
# plt.xlabel("TOPIC ID",fontsize="13");	plt.ylabel("Total # removal",fontsize="13");
# plt.show()

# ### DOC ORDER AFFECT REMOVAL RATE?  ###
# # freq_removal_per_doc_order = [sum([d[i] for d in data]) for i in range(40)]
# # fig = plt.figure(facecolor="white")
# # plt.bar(range(0,40), freq_removal_per_doc_order, color='gray')
# # plt.title("# REMOVE ARTICLES FOR DOCUMENTS AT i-TH POSITION", fontsize="14")
# # plt.xlabel("Document rank",fontsize="13");	plt.ylabel("Total # removal",fontsize="13");
# # plt.show()
# ###

# # plt.matshow(data,cmap=cm.gray)
# # plt.show()
# exit()



##########################################################################
##########################################################################
##### SPLIT THEME : DETAIL
##########################################################################
##########################################################################
# topicJSON = json.loads(open("dataset/nytimes-31-topics.json","r").read())
# split_words_per_topic = {}
# for tid,tlist in TOPICS.iteritems():
# 	split_words_per_topic[tid]=[]
# 	# print tid, " ".join([w["word"] for w in topicJSON[str(tid)]["words"][:20]])
# 	for rid, topic in tlist.iteritems():
# 		sw = [e["message"] for e in topic["log_data"] if e["event"]=="SPLIT_THEME"]
# 		if len(sw)>0:
# 			# print "-->"," ".join(sw), "("+",".join(topic['improved_theme'])+")"
# 			split_words_per_topic[tid].append(sw)
# 			if sw[0]=="climate change":	
# 				pp.pprint(topic)
# 				exit()
# 			else:
# 				print sw[0]
# pp.pprint(split_words_per_topic)


# for hit in HITS:
# 	log = hit["data"]["topics"][2]["log"]
# 	idx_improvement_begin = [i for i,v in enumerate(log) if v["message"]=="theme_improvements"]
# 	idx_improvement_end = [i for i,v in enumerate(log) if v["message"]=="questionnaire"]
# 	for i in range(3):
# 		tid = int(hit["data"]["topics"][i]["tid"])
# 		logs = log[idx_improvement_begin[i]:idx_improvement_end[i]]
# 		words_split = Set([])
# 		if tid==21:
# 			print "21 is found"
# 			print [e for e in logs if e["event"]=="SPLIT_THEME" or e["event"]=="UN_SPLIT_THEME" ] 
# 		for w in [e for e in logs if e["event"]=="SPLIT_THEME" or e["event"]=="UN_SPLIT_THEME" ]:
# 			#print w
# 			if w["event"]=="SPLIT_THEME": 
# 				words_split.add(w["message"])
# 			elif w["event"]=="UN_SPLIT_THEME": 
# 				words_split.remove(w["message"])
# 		# print words_split
# 		all_logs_per_topic[tid].append(list(words_split))
# pp.pprint(all_logs_per_topic)
# num_split_words = [sum([len(e) for e in tdata]) for i,tdata in all_logs_per_topic.iteritems()]
# data = num_split_words
# print num_split_words
# print "# SPLIT_WORDS:   Avg.:%f, STD:%f, Median:%f, Max:%f, Min:%f"%(np.mean(data), np.std(data), np.median(data), np.max(data), np.min(data))

exit()



