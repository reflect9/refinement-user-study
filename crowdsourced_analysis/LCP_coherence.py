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


####################################################################################
### PRECALCULATING TOPIC COHERENCE : LCP, Log Conditional Probability by Mimno
####################################################################################

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


