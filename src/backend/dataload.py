import mysql.connector
import pandas as pd

def load_data_from_mysql(host, user, password, database):
    # MySQL 서버에 연결
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    # 커서 생성
    cursor = conn.cursor()

    # member_based_okr_assignments 데이터 가져오기
    cursor.execute("SELECT * FROM member_based_okr_assignments")
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    member_based_okr_assignments = pd.DataFrame(result, columns=column_names)

    # okr_peer_30 데이터 가져오기
    cursor.execute("SELECT * FROM okr_peer_30")
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    okr_df = pd.DataFrame(result, columns=column_names)

    # member_based_okr_assignments와 okr_peer_30을 JOIN하여 데이터 가져오기
    sql_query = '''
    SELECT *
    FROM member_based_okr_assignments
    JOIN okr_peer_30 
    ON okr_peer_30.OKR_NUM IN (member_based_okr_assignments.project1, member_based_okr_assignments.project2, member_based_okr_assignments.project3);
    '''
    cursor.execute(sql_query)
    result = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    member_okr = pd.DataFrame(result, columns=column_names)

    # 연결 종료
    cursor.close()
    conn.close()
    
    return member_based_okr_assignments, okr_df, member_okr
