import sys
import os
import src.backend.dataload as dl


def main():
    # MySQL 서버 정보 설정
    host = '127.0.0.1'
    user = 'root'
    password = 'hj010701'
    database = 'employee'

    # 데이터 로드
    member_based_okr_assignments, okr_df, member_okr = dl.load_data_from_mysql(host, user, password, database)

    # 데이터 사용 예시
    print(member_based_okr_assignments.head())
    print(okr_df.head())
    print(member_okr.head())

if __name__ == "__main__":
    main()
