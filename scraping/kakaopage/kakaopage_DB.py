import pymysql
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from security.test_setting import Test_DB

db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')

# DB 저장 정보
class Novel_Info :
    new_work = 0

    # 공통
    Id = 0

    # TAVLE total_product
    Title = ""
    Author = ""
    Img_url = ""
    Description = ""

    # TABLE kakaopage_product
    Age_15gt = 0
    Completion_status = 0
    Number = 0
    Latest_ep_date = ""
    Visitor = 0
    Keyword = ""
    
db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
with db.cursor() as cursor :
    sql = """SELECT title, author
                FROM total_product"""
    cursor.execute(sql)
    INSERT_Tlist = list(cursor.fetchall())

    sql = """SELECT kakao_id, img_url
                FROM total_product
                WHERE kakao_id IS NOT NULL AND img_url LIKE '%kakao.com%'"""
    cursor.execute(sql)
    UPDATE_img_Tlist = list(cursor.fetchall())

    sql = """SELECT kakao_id, title, author
                FROM total_product
                WHERE kakao_id IS NOT NULL"""
    cursor.execute(sql)
    UPDATE_other_Tlist = list(cursor.fetchall())
db.close()

# 신작 DB INSERT 함수
def DB_Insert_Many(insert_novel_info_Tlist) :
    """
        insert_novel_info_Tlist 구성 요소 순서
        (Id, Title, Author, Img_url, Description, Age_15gt, Completion_status, Number, Latest_ep_date, Visitor, Keyword) 
    """
    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """INSERT INTO kakaopage_product(id, age_15gt, completion_status, number, latest_ep_date, visitor, keyword)
                        VALUES(%s, %s, %s, %s, %s, %s, %s)"""
            val = list(map(lambda a: (a[0],a[5],a[6],a[7],a[8],a[9],a[10]),insert_novel_info_Tlist))
            cursor.executemany(sql,val)
            db.commit()
    finally :
        db.close()

    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """UPDATE total_product
                        SET kakao_id=%s
                        WHERE title=%s AND author=%s"""
            val = list(map(lambda a: (a[0],a[1],a[2]),
                        list(filter(lambda b : (b[1],b[2]) in INSERT_Tlist ,insert_novel_info_Tlist))))
            cursor.executemany(sql,val)
            db.commit()
    finally :
        db.close()

    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :    
            sql = """INSERT INTO total_product(kakao_id, title, author, img_url, description)
                        VALUES(%s, %s, %s, %s, %s)"""
            val = list(map(lambda a: (a[0],a[1],a[2],a[3],a[4]),
                        list(filter(lambda b : (b[1],b[2]) not in INSERT_Tlist ,insert_novel_info_Tlist))))
            cursor.executemany(sql,val)
            db.commit()
    finally :
        db.close()
    return 

# 구작 DB UPDATE 함수
def DB_Update_Many(update_novel_info_Tlist) :
    """
        update_novel_info_Tlist 구성 요소 순서
        (Id, Title, Author, Img_url, Age_15gt, Completion_status, Number, Latest_ep_date, Visitor) 
    """
    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """UPDATE kakaopage_product
                        SET pre_visitor=visitor
                        WHERE id=%s
            """
            val = list(map(lambda a: (a[0]),update_novel_info_Tlist))
            cursor.executemany(sql,val)
            db.commit()
    finally :
            db.close()

    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """UPDATE kakaopage_product
                        SET age_15gt=%s, completion_status=%s, number=%s, latest_ep_date=%s, visitor=%s 
                        WHERE id=%s"""
            val = list(map(lambda a: (a[4],a[5],a[6],a[7],a[8],a[0]),update_novel_info_Tlist))
            cursor.executemany(sql,val)
            db.commit()
    finally :
            db.close()

    #img_url 변경시
    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """UPDATE total_product
                        SET img_url=%s
                        WHERE kakao_id=%s"""
            val = list(filter(lambda a : (a[1],a[0]) not in UPDATE_img_Tlist,
                        list(filter(lambda b : (b[1]) in list(map(lambda c : (c[0]), UPDATE_img_Tlist)),
                            list(map(lambda d : (d[3],d[0]),update_novel_info_Tlist)) )) ))
            cursor.executemany(sql,val)
            db.commit()
    finally :
            db.close()
    
     #title 또는 author 변경시
    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try :
        with db.cursor() as cursor :
            sql = """UPDATE total_product
                        SET title=%s, author=%s
                        WHERE kakao_id=%s"""
            val = list(filter(lambda a : (a[0],a[1],a[2]) not in UPDATE_other_Tlist,
                        list(map(lambda b : (b[1],b[2],b[0]), update_novel_info_Tlist)) ))
            cursor.executemany(sql,val)
            db.commit()  
    finally :
            db.close()
    return 

def DB_Delete() :
    db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
    try:
        with db.cursor() as cursor :
            sql = """DELETE FROM kakao_product
                        WHERE id=%s"""
            val = (Novel_Info.Id)
            cursor.execute(sql,val)
            db.commit()

    finally :
         db.close()
    return
               