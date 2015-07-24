import re, json, os, logging, random, string, collections
from datetime import datetime
import pprint
import csv, itertools, operator



topicIdx = 3


file_topicJSON = open("dataset/nytimes-20-topics.json","r")
topicJSON = json.loads(file_topicJSON.read())



topicData = topicJSON[str(topicIdx)]["words"]        
topicWords = [w['word'] for w in topicData]

file_docJSON = open("dataset/nytimes-20-documents-"+str(topicIdx)+".json","r")
text_title = [" ".join(doc["context"]) for doc in file_docJSON]


pp.pprint(text_title)


