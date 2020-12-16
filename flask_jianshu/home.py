import re
from collections import Counter
from datetime import datetime

import jieba
from flask import Flask, render_template, request, redirect
from pyecharts import WordCloud

from flask_jianshu.GetUserInfo import GetUserInfo
from flask_jianshu.config import *
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient(MONGO_HOST,MONGO_PORT)
db = client[MONGO_DB]

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        formdata = request.form['url']
        match_result = re.match('(https://www.jianshu.com/u/)?(\w{12}|\w{6})',formdata)
        user_slug = match_result.groups()[-1]
        print(user_slug)

        userdata = db['user_timeline'].find_one({'slug':user_slug})
        last_time = ''
        if userdata != None:
            last_time = userdata['last_time']
        gui = GetUserInfo(user_slug)
        item = gui.get_user_info()
        print(item)
        db['user_timeline'].update({'slug':item['slug']},{'$set':item},upsert=True)

        if userdata != None:
            gui.timeline = userdata
        gui.get_user_timeline(last_time)
        db['user_timeline'].update({'slug': item['slug']}, {'$set': gui.timeline}, upsert=True)

        usertimeline = db['user_timeline'].find_one({'slug': user_slug})




        item['like_notes_num'] = len(usertimeline['like_notes'])
        item['like_colls_num'] = len(usertimeline['like_colls'])
        item['like_nbs_num'] = len(usertimeline['like_notebooks'])
        item['comment_notes_num'] = len(usertimeline['comment_notes'])
        item['like_comments_num'] = len(usertimeline['like_comments'])
        item['reward_notes_num'] = len(usertimeline['reward_notes'])

        first_tag_time = get_first_tag_time(usertimeline)
        tags_data = gui.tags_data()

        time_data = gui.get_tag_month_data()
        # 2020-09
        month_data = [time[0:7] for time in time_data]
        counter = Counter(month_data)
        print(counter.items())
        sorted_counter = sorted(counter.items(), key=lambda t: t[0])
        print(sorted_counter)
        dic_month_data = {
            'month_line':[t[0] for t in sorted_counter],
            'month_freq': [t[1] for t in sorted_counter]
        }
        # 2020-09-23
        day_data = [time[0:10] for time in time_data]
        counter = Counter(day_data)
        print(counter.items())
        sorted_counter = sorted(counter.items(), key=lambda t: t[0])
        print(sorted_counter)
        dic_day_data = {
            'day_line': [t[0] for t in sorted_counter],
            'day_freqency': [t[1] for t in sorted_counter]
        }


        # 2020-09-23 12:32:21
        hour_data = [time[11:13] for time in time_data]
        counter = Counter(hour_data)
        print(counter.items())
        sorted_counter = sorted(counter.items(), key=lambda t: t[0])
        print(sorted_counter)
        dic_hour_data = {
            'hour_line': [t[0] for t in sorted_counter],
            'hour_freqency': [t[1] for t in sorted_counter]
        }

        week_data = [date_to_week(time) for time in time_data]
        counter = Counter(week_data)
        print(counter.items())
        sorted_counter = sorted(counter.items(), key=lambda t: t[0])
        print(sorted_counter)
        dic_week_data = {
            'week_line': [t[0][1:] for t in sorted_counter],
            'week_freqency': [t[1] for t in sorted_counter]
        }


        # week_data = [date_to_week(time) for time in time_data]
        week_hour_data = []
        for time in time_data:
            week_hour = date_to_week(time)[0]+time[11:13]
            week_hour_data.append(week_hour)

        counter = Counter(week_hour_data)
        print(counter.items())
        tag_week_hour_data = []
        for x in counter.items():
            # (213,5)
            # [2,13,5]
            each = [int(x[0][0]),int(x[0][1:3]),x[1]]
            tag_week_hour_data.append(each)

        max_freq = counter.most_common(1)[0][1]
        print(tag_week_hour_data)
        print(max_freq)

        comments_lst = usertimeline['comment_notes']
        comment_text_lst = [comment_dic['comment_text'] for comment_dic in comments_lst]
        big_comment_text = ''.join(comment_text_lst)
        wordslst = jieba.cut(big_comment_text)
        word_freq = Counter(wordslst).most_common(150)
        print(word_freq)
        words_dic = {x[0]:x[1] for x in word_freq if len(x[0])>=2}
        print(words_dic)

        comments_size = len(comments_lst)

        word_cloud = make_wordcloud(words_dic)

        return render_template('timeline.html'
                               ,baseinfo=item
                               ,first_tag_time = first_tag_time
                               ,tags_data=tags_data
                               ,dic_month_data=dic_month_data
                               ,dic_day_data=dic_day_data
                               ,dic_hour_data=dic_hour_data
                               ,dic_week_data=dic_week_data
                               ,tag_week_hour_data=tag_week_hour_data
                               ,max_freq=max_freq
                               ,comments_size=comments_size
                               ,word_cloud=word_cloud
                               )

def make_wordcloud(comm_data):
    '''
    由于echarts绘制词云图出现问题，用pyecharts绘制词云图
    :param comm_data:
    :return:
    '''
    name = comm_data.keys()
    value = comm_data.values()
    wordcloud = WordCloud(width='100%', height=600)
    wordcloud.add("", name, value, shape="diamond", word_size_range=[15, 120])
    return wordcloud.render_embed()

def date_to_week(str_date):
    time_date = datetime.strptime(str_date,'%Y-%m-%d %H:%M:%S')
    week_day_dict = {0: '0周一', 1: '1周二', 2: '2周三', 3: '3周四',
                     4: '4周五', 5: '5周六', 6: '6周日'}
    print(time_date)
    print(type(time_date))
    return week_day_dict[time_date.weekday()]

def get_first_tag_time(timeline):
    first_tag_time = {
        # 'join_time': self.user_data['join_time'],
        'first_like_user': extract_first_tag_time(timeline['like_users']),
        'first_share_note': extract_first_tag_time(timeline['share_notes']),
        'first_like_note': extract_first_tag_time(timeline['like_notes']),
        'first_like_coll': extract_first_tag_time(timeline['like_colls']),
        'first_like_nb': extract_first_tag_time(timeline['like_notebooks']),
        'first_comment': extract_first_tag_time(timeline['comment_notes']),
        'first_like_comment': extract_first_tag_time(timeline['like_comments']),
        'first_reward_note': extract_first_tag_time(timeline['reward_notes']),

    }

    return first_tag_time

def extract_first_tag_time(lst):
    if len(lst) == 0:
        return None
    else:
        sorted_lst = sorted(lst, key=lambda dic:dic['time'])
        return sorted_lst[0]
# https://www.jianshu.com/users/51b4ef597b53/timeline?max_id=683789554&page=2
# https://www.jianshu.com/users/51b4ef597b53/timeline?max_id=677754902&page=3
if __name__ == '__main__':
    app.run(debug=True)