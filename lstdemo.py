# lst = [1,3,4]
# lst2 = [3,4,5]
# lstt = []
#
# # lstt.append(lst)
# # # lstt.append(lst2)
# # # print(lstt)
# lstt.extend(lst)
# lstt.extend(lst2)
# print(lstt)
from collections import Counter

lst = ['2020-09','2020-08','2020-08','2020-08','2020-09','2020-09','2020-09']
counter = Counter(lst)
print(counter.items())
sorted_counter = sorted(counter.items(),key=lambda t:t[0])
print(sorted_counter)
print(counter.most_common(1)[0][1])