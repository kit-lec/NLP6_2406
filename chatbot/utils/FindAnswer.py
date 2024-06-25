class FindAnswer:
  # Database 인스턴스 객체를 받아 생성
  def __init__(self, db):
    self.db = db

  # 답변검색
  # 의도명(intent_name) 과 개체명 태그 리스트 (ner_tags) 를 이용해 질문의 답변을 검색
  def search(self, intent_name, ner_tags):
    # 의도명, 개체명으로 답변 검색
    sql = self._make_query(intent_name, ner_tags)
    answer = self.db.select_one(sql)

    # 검색되는 답변이 없었으면 의도명만 이용하여 답변 검색
    if answer is None:
      sql = self._make_query(intent_name, None)
      answer = self.db.select_one(sql)

    return answer['answer'], answer['answer_image']

  # 검색 쿼리 생성
  # '의도명' 만 검색할지, 여러종류의 개체명 태그와 함께 검색할지 결정하는 '조건'을 만드는 간단한 함수
  # SELECT * FROM chatbot_train_data WHERE intent = '주문' ORDER BY random() LIMIT 1
  # SELECT * FROM chatbot_train_data WHERE intent = '주문' and ( ner LIKE '%B_FOOD%' ) ORDER BY random() LIMIT 1
  # SELECT * FROM chatbot_train_data WHERE intent = '예약' and ( ner LIKE '%B_FOOD%' OR ner LIKE '%B_DT%' ) ORDER BY random() LIMIT 1

  def _make_query(self, intent_name, ner_tags):
    sql = "SELECT * FROM chatbot_train_data"
    if intent_name != None and ner_tags == None:
      sql += f" WHERE intent = '{intent_name}'"

    elif intent_name != None and ner_tags != None:
      where = f' WHERE intent = "{intent_name}"'
      if len(ner_tags) > 0 :
        where += ' and ('
        for ne in ner_tags:
          where += f" ner LIKE '%{ne}%' OR "
        where = where[:-3] + ')'   # [:-3]  마지막 'OR ' 를 없애기 위해 
      sql += where

    # 동일한 답변이 복수개인 경우, 랜덤으로 한개 선택
    sql += " ORDER BY random() LIMIT 1"
    return sql


  # ④ NER 태그를 실제 입력된 단어로 변환
  # 예를 들어 '자장명 주문할께요' 라는 텍스트가 챗본 엔진에 입력되었다고 합시다.
  # 그러면 챗봇 엔진은 '자장명'을 'B_FOOD 객체명'으로 인식합니다.
  # 이때 검색된 답변이 '{B_FOOD} 주문 처리 완료 되었습니다 주문해주셔서 감사합니다' 라고 한다면,
  # 답변 내용속 '{B_FOOD}' 를 '자장면' 으로 치환해 주는 함수입니다.
  # 치환해야 하는 태그가 더 존재한다면 치환 규칙을 추가하면 됩니다.
  def tag_to_word(self, ner_predicts, answer):
    for word, tag in ner_predicts:

      # 변환해야 하는 태그가 있는 경우 치환
      if tag in ['B_FOOD', 'B_DT', 'B_TI']:
        answer = answer.replace(f'{{{tag}}}', word)

    return answer
