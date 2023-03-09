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
    First_ep_date = ""
    Latest_ep_date = ""
    Visitor = 0
    Keyword = ""

with db.cursor() as cursor :
    sql = """SELECT title, author
                FROM total_product"""
    cursor.execute(sql)
    INSERT_Tlist = list(cursor.fetchall())

    sql = """SELECT kakao_id, title, author, img_url
                FROM total_product
                WHERE kakao_id IS NOT NULL"""
    cursor.execute(sql)
    UPDATE_Tlist = list(cursor.fetchall())
    UPDATE_id_Tlist = list(map(lambda a : a[0],UPDATE_Tlist))
    UPDATE_img_Tlist = list(map(lambda a : a[3],UPDATE_Tlist))
    UPDATE_other_Tlist = list(map(lambda a : (a[0],a[1],a[2]),UPDATE_Tlist))

# 신작 DB INSERT 함수
def DB_Insert() :
    try :
        with db.cursor() as cursor :
            if Novel_Info.Age_15gt :
                sql = """INSERT INTO kakaopage_15gt(id, age_15gt)
                            VALUES(%s,%s)
                """
                val = (Novel_Info.Id, Novel_Info.Age_15gt)
                cursor.execute(sql,val)
                db.commit()
                return

            else :
                sql = """INSERT INTO kakaopage_product(id, age_15gt, completion_status, number, first_ep_date, latest_ep_date, visitor, keyword)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                val = (Novel_Info.Id, Novel_Info.Age_15gt, Novel_Info.Completion_status, Novel_Info.Number,
                        Novel_Info.First_ep_date, Novel_Info.Latest_ep_date, Novel_Info.Visitor, Novel_Info.Keyword)
                cursor.execute(sql,val)
                db.commit()

                if (Novel_Info.Title, Novel_Info.Author) in INSERT_Tlist :
                    sql = """UPDATE total_product
                                SET kakao_id=%s
                                WHERE title=%s AND author=%s"""
                    val = (Novel_Info.Id, Novel_Info.Title, Novel_Info.Author)
                    cursor.execute(sql,val)

                else :
                    sql = """INSERT INTO total_product(kakao_id, title, author, img_url, description)
                                VALUES(%s, %s, %s, %s, %s)"""
                    val = (Novel_Info.Id, Novel_Info.Title, Novel_Info.Author, Novel_Info.Img_url, Novel_Info.Description)
                    cursor.execute(sql,val)
                db.commit()
    except Exception :
            db.close()
    return 

# 구작 DB UPDATE 함수
def DB_Update() :
    try :
        with db.cursor() as cursor :
            if Novel_Info.Age_15gt : return
            
            sql = """UPDATE kakaopage_product
                        SET pre_visitor=visitor
                        WHERE id=%s
            """
            val = (Novel_Info.Id)
            cursor.execute(sql,val)
            db.commit()

            sql = """UPDATE kakaopage_product
                        SET completion_status=%s, number=%s, latest_ep_date=%s, visitor=%s, keyword=%s 
                        WHERE id=%s"""
            val = (Novel_Info.Completion_status, Novel_Info.Number, Novel_Info.Latest_ep_date, Novel_Info.Visitor, Novel_Info.Keyword, Novel_Info.Id)
            cursor.execute(sql,val)
            db.commit()

            #img_url 변경시
            if UPDATE_img_Tlist[UPDATE_id_Tlist.index(Novel_Info.Id)].find('kakao.com') :
                 sql = """UPDATE total_product
                            SET img_url=%s
                            WHERE kakao_id=%s"""
                 val = (Novel_Info.Img_url, Novel_Info.Id)
                 cursor.execute(sql,val)
                 db.commit()
            
            #title 또는 author 변경시
            if (Novel_Info.Id, Novel_Info.Title, Novel_Info.Author) not in UPDATE_other_Tlist :
                 sql = """UPDATE total_product
                            SET title=%s, author=%s
                            WHERE kakao_id=%s"""
                 val = (Novel_Info.Title, Novel_Info.Author, Novel_Info.Id)
                 cursor.execute(sql,val)
                 db.commit()
                
    except Exception :
            db.close()
    return 

def DB_Delete() :
    try:
        with db.cursor() as cursor :
            sql = """UPDATE total_product
                        SET kakao_id=NULL
                        WHERE kakao_id=%s"""
            val = (Novel_Info.Id)
            cursor.execute(sql,val)
            db.commit()

            sql = """DELETE FROM kakao_product
                        WHERE id=%s"""
            val = (Novel_Info.Id)
            cursor.execute(sql,val)
            db.commit()

    except Exception :
         db.close()
               