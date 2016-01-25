import random, itertools
import pprint as pp

def arr_join(arr):
    return list(itertools.chain(*arr))

TOPIC_ID_FOR_PRACTICE = 21

tid_set = range(0,31)
tid_set.remove(int(TOPIC_ID_FOR_PRACTICE))
random.shuffle(tid_set)
all_refinements = []
for i in range(0, len(tid_set), 5):
    for refID in range(9):
        tid_list = [str(tid_set[i+d])+"-"+str(refID) for d in range(5)]
        for offset in range(0,5):  # TO CANCEL THE ORDERING EFFECT, WE ROTATE BY OFFSET
            tid_list_rotated = tid_list[offset:] + tid_list[:offset]
            all_refinements.append(tid_list_rotated)
            all_refinements.append(tid_list_rotated)
            print tid_list_rotated
        print "---"
    print"===="
# pp.pprint(all_refinements)
print len(all_refinements)

count = {}
for ref_list in all_refinements:
    # print ref_list
    for ref in ref_list:
        # print ref
        r = ref.split('-')[1]
        if r not in count.keys(): count[r]=0
        count[r]+=1

print count
pp.pprint(count)

# check = {i:0 for i in range(0,31)}
# for tid in all_tid:
#     three_id = tid.split(",")
#     for i in three_id:
#         check[int(i)] = check[int(i)]+1

# print check

