import jieba

sentance = '当然还是用python写爬虫代码来简书抓了，一个个复制粘贴是不可能的，要又要不到，只能写爬虫来抓，这样子才能维持数据来源'
wordlst = jieba.cut(sentance)
print(list(wordlst))

