dic1 = {
    'noteid':39,
    'time':'2020-09-11 15:37:47'
}

dic2 = {
    'noteid':34,
    'time':'2020-09-15 15:37:47'
}

dic3 = {
    'noteid':35,
    'time':'2020-09-08 15:37:47'
}

lst = []
lst.append(dic1)
lst.append(dic2)
lst.append(dic3)
print(lst)

# def sortdic(dic):
#     print(dic)
#     return dic['time']
def extract_first_time(lst):
    sorted_lst = sorted(lst, key=lambda dic:dic['time'])
    return sorted_lst[0]

dic = extract_first_time(lst)
print(dic)
# lst = [3,5,66,7,8,23,11]
# sortlst = sorted(lst)
# print(sortlst)