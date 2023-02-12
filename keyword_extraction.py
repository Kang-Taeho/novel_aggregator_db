import pymysql
import re

from konlpy.tag import Okt

okt = Okt()
stop_List = ['것', '그', '그렇다', '같다', '위', '더', '순', '수']

# 소설 사이트에서 사용 중인 키워드 집합
def novel_site_keyword() :
    keywords_set = set()

    with db.cursor() as cursor :
        sql = """SELECT keyword
                FROM novelpia_product
                """
        cursor.execute(sql)
        db_keywords = cursor.fetchall()

        for keywords in db_keywords :
            if keywords[0] == None : continue
            for i in keywords[0].split('#') :
                keywords_set.add(i)
    print(keywords_set)

# 소설 내용 전처리 함수
def processing(content, title) :
    pro_content = ''
    sentence_List = [title]
    sentence_List += filter(lambda a : a, re.split('[.!?]',content))

    for sentence in sentence_List :
        sentence = sentence.strip()
        sentence = re.sub('\n','',sentence)
        # sentence = re.sub('([a-zA-Z])','',sentence)
        sentence = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',sentence)
        sentence = re.sub('[-=+/\?;:!@#$%^&*"\'.`~ㆍ\\|\(\)\[\]\<\>「」『』【】《》]','',sentence) # ! ? , 빼고 생각
        

        if len(sentence) == 0 : continue
        sentence = okt.pos(sentence, stem=True)

        for word, tag in sentence :
            if word in stop_List : continue

            if tag == 'Noun' or tag == 'Alpha' : pro_content += word + " "
            elif tag == 'Verb' or tag == 'Adjective' : pro_content += word + ". "

    return pro_content.strip()

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try :
    content_List = []
    pro_content_List = []
    keyword_List = []

    with db.cursor() as cursor :
        sql = """SELECT title, content, keyword
                FROM kakaopage_product
                WHERE keyword LIKE '%#{0}%'
                """.format("삼국지")
        cursor.execute(sql)
        db_novel = cursor.fetchall()
        print("kakaopage : %s" % len(db_novel))

        for db_infos in db_novel :
            pro_content_List.append(processing(db_infos[1],db_infos[0]))
            content_List.append(db_infos[0] + ". " + db_infos[1])
            keyword_List.append(db_infos[2])
        
        # sql = """SELECT title, keyword, content
        #         FROM munpia_product
        #         WHERE keyword IS NOT NULL
        #         """
        # cursor.execute(sql)
        # db_novel = cursor.fetchall()
        # print("munpia : %s" % len(db_novel))

        # for db_infos in db_novel :
        #     for keyword in processing(db_infos[1],db_infos[0]) :
        #         if keyword in pro_content_dict : pro_content_dict[keyword] = pro_content_dict[keyword] + 1
        #         else :  pro_content_dict[keyword] = 1

        #     content_List.append(db_infos[0] + ". " + db_infos[1])
        
        # sql = """SELECT title, content
        #         FROM novelpia_product
        #         WHERE keyword LIKE '%{0}%'
        #         """.format(taeho)
        # cursor.execute(sql)
        # db_novel = cursor.fetchall()
        # print("novelpia : %s" % len(db_novel))

        # for db_infos in db_novel :
        #     pro_content_List.append(processing(db_infos[1],db_infos[0]))
        #     content_List.append(db_infos[0] + ". " + db_infos[1])


    for num in range(0,len(content_List)) : 
        print(str(num+1), end=', ')
        print(content_List[num].replace('\n',' '))
        print('\n')
        print(keyword_List[num])
        print(pro_content_List[num])
        print('\n')
        

finally :
    db.close()