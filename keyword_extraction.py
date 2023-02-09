import pymysql
import re

from konlpy.tag import Okt
from krwordrank.word import summarize_with_keywords

okt = Okt()

def processing(content, title) :
    pro_content = ''
    sentence_List = [title]
    sentence_List += filter(lambda a : a, re.split('[\n.]',content))

    for sentence in sentence_List :
        sentence = re.sub('\n','',sentence)
        #sentence = re.sub('([a-zA-Z])','',sentence)
        sentence = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',sentence)
        sentence = re.sub('[-=+,/\?;:!@#$%^&*"\'.`~ㆍ\\|\(\)\[\]\<\>「」『』【】《》]','',sentence)

        if len(sentence) == 0 : continue
        sentence = okt.pos(sentence, stem = True)
        word = []

        for i in sentence :
            if i[1] != 'Noun' or len(i[0]) == 1 : continue
            word.append(i[0])
        
        word = ' '.join(word)
        word += '.'
        pro_content += word
    return pro_content

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try :
    content_List = []

    with db.cursor() as cursor :
        sql = """SELECT title, content 
                FROM kakaopage_product
                WHERE keyword LIKE '%#이종족%'
                """
        cursor.execute(sql)
        db_novel = cursor.fetchall()

    for db_infos in db_novel :
        content = processing(db_infos[1],db_infos[0])
        content_List.append(content)

    keywords = summarize_with_keywords(content_List, min_count=5, max_length=10, beta=0.85, max_iter=10, verbose=True)
    print(keywords)

finally :
    db.close()