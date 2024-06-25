import sqlite3
import logging

class Database:
  def __init__(self, db_file):
    self.db_file = db_file
    self.conn = None

  # DB 연결
  def connect(self):
    if self.conn != None:
      return

    self.conn = sqlite3.connect(self.db_file)
    self.conn.row_factory = sqlite3.Row  # SELECT 결과를 Row 객체로 받게 함. => Row객체는 나중에 dict, tuple 형태로 변환 가능. 
    print("DB 연결 성공")

  # DB 연결 닫기
  def close(self):
    if self.conn is None:
      return

    self.conn.close()
    self.conn = None
    print("DB 연결 닫기 성공")
    
  # SQL 구문 실행  (INSERT, UPDATE, DELETE <- DML명령)
  def execute(self, sql):
    last_row_id = -1
    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
      self.conn.commit()
      last_row_id = cursor.lastrowid
    except Exception as ex:
      logging.error(ex)

    finally:
      return last_row_id

  # SELECT 구문 실행.  1개의 ROW만 불러오기
  def select_one(self, sql):
    result = None

    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
      result = dict(cursor.fetchone())  # 한개의 Row 를 읽어와 dict로 변환
    except Exception as ex:
      logging.error(ex)
    finally:
      return result

  # SELECT 구문 실행.  전체 Row(들) 불러오기, dict 의 list 형태로 리턴 
  def select_all(self, sql):
    results = None

    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
      results = [dict(row) for row in cursor.fetchall()]
    except Exception as ex:
      logging.error(ex)
    finally:
      return results