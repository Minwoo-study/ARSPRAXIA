# 레포지토리 설명
"아르스프락시아"라는 국내 회사에서 일하면서 작성한 코드와 그 사용법을 정리한 레포지토리

이 레포지토리에 포함되지 않았으나, 똑같이 "아르스프락시아"에서 일하면서 작성한 다른 코드는 다음 링크 참조:
[NER Editor](https://github.com/Siadel/arspraxia_JSON_NER_Editor)

# 레포지토리 구조
## depth 0
- `execute` 계열 파일 : `tool/` 폴더에 있는 파이썬 파일을 불러와 그때그때 주어진 목표에 맞게 활용하는 일종의 코드 플랫폼

## depth 1
- `tool/` : 업무에 필요한 실제 코드를 용도에 따라 분할한 파일이 모여있는 폴더
- `const/` : `tool/` 폴더 이하의 파일은 로컬에서 돌아가기 때문에, 컴퓨터마다 이 프로젝트 폴더와 작업 대상 폴더의 절대 위치가 다름. 이 폴더의 `paths.py`를 생성해 그 경로들을 미리 적어두는 식으로 활용했음.
- `source/` : 코드 테스트나 실작업을 위한 작업 대상 파일을 넣어놓는 곳.
- `result_storage/` : 결과로 생성되는 파일의 개수가 몇백 개 단위 이하로 적을 때 활용하는, `tool/` 코드에 의한 산출물 저장소.

# `tool/` 이하의 파일 설명 (주관적 중요도 순)
## 1. `common.py`
아래 모든 파일과 `execute` 계열 코드 플랫폼 파일에 자주 쓰이는 함수나 클래스를 정의해둔 모듈
## 2. `JSONconverter.py`
`.xlsx` 파일로 되어 있는 특수한 NER 가공 데이터를 문서 ID(`Doc_ID`)별 `.json` 파일로 변환하는 코드

개수 작업을 여러 번 거치면서 `JSONformat_handler.py` 등을 이용해 유효성 검사를 자체적으로 진행하게 됨
## 3. `JSONformat_handler.py`
`.json` 파일로 되어 있는 NER 가공 데이터의 형식 오류를 교정하는 코드

형식 오류는 크게 컬럼 오류, 데이터타입 오류, 내용 오류, 컬럼 순서 오류가 있고, 각각의 오류를 교정하는 코드가 함수로 정의되어 있음
## 4. `handler1221.py`
12월 21일에 만든, `JSONformat_handler.py`를 기반으로 제작된 최종 `.json` NER 가공 데이터 형식 오류 교정 코드

`JSONformat_handler.py`의 함수들과 다르게 이 모듈의 `main()` 함수를 활용해 대규모 파일 작업 가능함
## 5. `bloody_s3.py`
대규모 파일을 S3 AWS Cloud Storage에 업로드하는 코드
## 6. `sen_token_counter.py`
대규모 `.json` NER 가공 데이터의 파일 개수, 총 문장 개수, 총 토큰 개수를 세어 그 데이터를 `.json` 파일로 저장하는 코드

예시 결과:
```json
{
  "files" : 39915,
  "total_sentences" : 102547,
  "total_tokens" : 4816079
}
```
## 7. `entity_extractor.py`
대규모 `.json` NER 가공 데이터에서 NER 태깅된 개체명과 그 태그, 태깅된 위치를 추출하는 코드. 이 코드의 결과물은 [NER Editor](https://github.com/Siadel/arspraxia_JSON_NER_Editor)를 사용할 때 필수 자료로 활용함.

예시 결과:
```json
{
  "Korea" : {
    "LC-Country" : ["SampleDoc123456||SampleDoc123456-sen123456", ...],
    ...
  },
  ...
}
```
## 8. `terkinni_crawler.py`
기사 링크를 모은 별도 `.xlsx` 파일의 데이터를 기반으로 사업 소스를 제공하는 언론사인 Terkinni의 웹페이지에서 기사 데이터를 크롤링하고, 그 데이터를 `.xlsx` 파일로 구성해 가져오는 코드

해당 홈페이지에 크롤링 방지 대책이 마련되어 있지 않아 가능했음
## 9. `json_to_csv.py`
대규모 `.json` NER 가공 데이터 파일을, 사업계획서 상 원천데이터 파일 형식인 `.csv`로 재구성하는 코드

사업 목표 상 최종 데이터 파일과 원천데이터 파일의 내용이 일치해야 하기 때문에, 내용의 일치를 위해 가공 데이터를 다시 원천데이터 형식으로 바꾸는 것임
## 10. `JSONcatcher.py`
대규모 `.json` NER 가공 데이터 파일에 포함된 `Entities_list` 데이터에서 NER 태깅 데이터만 추출해 `set` 데이터타입의 unique 보장 특징을 활용해서, 실제로 태깅된 태그의 형태를 확인하는 코드

코드의 산출 파일 형태는 `.json`

이 코드의 실행 결과는 `JSONformat_handler.py`의 오류 교정 논리를 작성할 때 활용함
## 11. `JSONsampler.py`
대규모 `.json` NER 가공 데이터 중 파일 개수를 정해, 그 파일 개수만큼 다른 지정한 디렉토리로 복사하여 별도의 샘플 데이터를 구성하는 코드

하위 폴더 구조도 정확하게 복사함
## 12. `catch_duplicate.ipynb`
`.xlsx`나 `.csv` 형식의 두 원천데이터 파일 세트를 비교해 서로 중복되는 `Doc_ID`가 있는지 확인하고, 서로 중복되는 `Doc_ID` 중 하나의 데이터를 삭제해 별도의 `.xlsx` 원천데이터 형식으로 파일을 merge하는 코드
## 13. `file_splitter.py`
몇십만 개 단위의 대규모 파일을 n개(기본값은 10만) 단위로 나눠 별도의 하위 디렉토리에 옮기는 코드
## 14. `make_docid.py`
`JSONconverter.py` 관련 작업을 수행하다가 맞닥뜨린 대규모 원천 파일의 오류를 교정하기 위해 특수 제작한 코드로, 상실된 `Doc_ID` 컬럼을 `Sen_ID` 컬럼을 이용해 재구성하는 코드
## 15. `datetime_test.py`
`datetime` 모듈 관련 테스트 코드. 원래는 `instant.ipynb`에 있어야 하지만, 작업 노하우가 부족했던 당시에 만들었고, 미처 삭제할 시간이 없어 일종의 더미 코드로 남게 됨.