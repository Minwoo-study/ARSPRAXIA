# 레포지토리 설명
회사 "아르스프락시아"에서 2023년 9월부터 12월까지 일하면서 작성한 코드와 그 사용법을 정리한 레포지토리

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
1. `common.py`

2. `JSONconverter.py`
3. `JSONformat_handler.py`
4. `handler1221.py`
5. `bloody_s3.py`
6. `sen_token_counter.py`
7. `entity_extractor.py`
8. `terkinni_crawler.py`
9. `json_to_csv.py`
10. `JSONcatcher.py`
11. `JSONsampler.py`
12. `catch_duplicate.ipynb`
13. `file_splitter.py`
14. `make_docid.py`
15. `datetime_test.py`
