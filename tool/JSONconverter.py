"""
원천데이터를 수합해 json 파일로 만드는 코드

원천데이터 파일 형식 (.xlsx)
Doc_ID, Filename, Title, Pub_Type, Pub_Subj, Pub_Date, Col_Date, Sen_ID, Word_Count, Text, Sentence, Tokenized_Sentence, Token, Column1, Column2 ...

Column1 : Token 데이터를 text화한 것
Column2 ~ : Token 데이터를 NER화한 것

특이사항: 데이터의 최소 단위가 2개 행이기 때문에, 행 2개 단위로 묶어서 처리해야 함

예외 : Doc_ID 열이 없는 경우, Sen_ID 열의 데이터를 기반으로 Doc_ID를 자동으로 생성해줌

원천데이터 재가공:
    1. 모든 원천데이터 파일을 하나의 데이터프레임으로 합침
    2. 1의 과정에서 예외사항을 고려하기
    3. 

변환 논리:
    Doc_ID 기준으로
    1. Doc_ID -> Filename
    2. Title -> Title
    3. Pub_Type -> Pub_Type
    4. Pub_Subj -> Pub_Subj
    5. Pub_Date -> Pub_date
    6. Col_Date -> Coll_date

    7. data 리스트 생성
    8. data 리스트에 추가할 dict 생성
    9. Sen_ID -> SEN_ID
    10. Word_Count -> Word_Count (int 자료형으로 변환)
    11. Column1 -> Raw_data
    12. Column2 ~ -> Entities_list


결과물 json 파일 형식
{
    "Doc_ID": "20230808_newsdata_Korea_007413",
    "Filename": "",
    "Title": "Kang Daniel Dipilih Sebagai Wajah Baru untuk Merek Kecantikan Global Mernel", # 제목
    "Text": "Kang Daniel Dipilih Sebagai Wajah Baru untuk Merek Kecantikan Global Mernel", # 본문
    "Pub_Type": "Newspaper",
    "Pub_Subj": "Korea",
    "Pub_date": "2021-01-01",
    "Coll_date": "2023-08-08",
    "data": [
        ...
    ]
}

data에 들어갈 dict 형식
{
    "SEN_ID": "20230808_newsdata_Korea_007413_sen000001",
    "Word_Count": 10,
    "NER_Count": 1,
    "ANNO_ID": "IN_001",
    "Raw_data": "Kang Daniel telah menjadi wajah baru dari merek kecantikan .",
    "Entities_list": [
        "PS-Name-B",
        "PS-Name-I",
        "O",
        "O",
        "O",
        "O",
        "O",
        "O",
        "O",
        "O"
    ],
    "Entities": [
        {
            "entity": "Kang Daniel",
            "entityClass": "PS-Name",
            "entityStart": 0,
            "entityEnd": 1
        }
    ]
}

"""

import pathlib
import pandas
import json
from numpy import float64
from copy import deepcopy
from datetime import datetime, timedelta
from natsort import natsorted
from dateutil.parser import parse

from tool import common, JSONformat_handler

EXCEL_INITIAL_DATE = datetime(1899, 12, 30)

# 오류 찾는 용도
data_columns = {
    "Doc_ID" : 0,
    "Filename" : 1, 
    "Title" : 2, 
    "Pub_Type" : 3, 
    "Pub_Subj" : 4, 
    "Pub_Date" : 5, 
    "Col_Date" : 6, 
    "Sen_ID" : 7, 
    "Word_Count" : 8, 
    "Text" : 9, 
    "Sentence" : 10, 
    "Tokenized_Sentence" : 11, 
    "Token" : 12
}
data_columns_set = set(data_columns)

def evade_special_glyphs(string:str) -> str:
    """
    파일명에 들어가면 안 되는 특수문자를 치환합니다.
    """
    evade_list = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
    for char in evade_list:
        string = string.replace(char, "_")
    return string

def convert_date(date:datetime|float64) -> str:
    """
    
    """
    if isinstance(date, float64):
        return (EXCEL_INITIAL_DATE + timedelta(days=date)).strftime("%Y-%m-%d")
    elif isinstance(date, str):
        return parse(date).strftime("%Y-%m-%d")
    else:
        return date.strftime("%Y-%m-%d")

def result_dir(result_path:pathlib.Path, result_folder_prefix:str, result_folder_number:int):
    """
    데이터 소분 폴더 경로를 반환합니다.
    """
    return result_path / f'{result_folder_prefix}_{result_folder_number}'

def now():
    return datetime.now().strftime("%H:%M:%S") + "\t"

def get_row_data(row:pandas.Series, column_name:str) -> str:
    """
    데이터프레임의 행에서 column_name에 해당하는 열의 데이터를 가져옵니다.\n
    만약 해당 열이 없다면 빈 문자열을 반환합니다.
    """
    if column_name in row.index:
        return row[column_name]
    else:
        return ""

def main(
    source_path:pathlib.Path, 
    result_path:pathlib.Path, 
    *, 
    result_folder_prefix:str="json", 
    result_folder_start_num:int = 0, 
    task_limit:int=None, 
    file_scale:int=100000,
    statistic:bool=False):
    """
    source_path : 원천데이터 폴더가 모여있는 폴더 위치 (depth 2)\n
    result_path : 결과물 json 파일이 모인 폴더를 저장할 폴더 위치 (depth 2)\n
    -- 이하 내용은 positional only며 기본값이 있음 --\n 
    result_folder_prefix : 결과물 json 파일이 모인 폴더의 이름 접두사 (기본: json)\n
    result_folder_start_num : 결과물 json 파일이 모인 폴더의 이름 시작 번호 (기본: 0)\n
    task_limit : 처리할 원천데이터 파일 개수 (None이면 전체) (기본: None)\n
    file_scale : 파일을 몇 개씩 묶어서 저장할 것인지 (기본: 10만개 단위)\n
    statistic : 파일 수, 문장 수, 토큰 수 합산 통계 json 파일을 result_path에 저장할 것인지 (기본: False)\n
    """

    if not source_path.exists(): raise FileNotFoundError(f"{source_path}가 존재하지 않습니다.")

    result_path.mkdir(exist_ok=True)

    # 통계 작성용. 관련 파라미터가 True일 때만 이 딕셔너리의 값이 채워짐
    statistic_dict = {
        "files": 0,
        "total_sentences": 0,
        "total_tokens": 0
    }

    if task_limit is None:
        task_limit = len(list(source_path.glob('*.xlsx')))
        
    new_doc = dict()
    current_doc_id = ""

    result_folder_num = result_folder_start_num -1 # 결과물 폴더 번호. 폴더 생성 직전 무조건 1을 더하는 논리 때문에 1을 뺌
    task_count = 0 # 작업한 파일 개수. 폴더를 만들 때 활용함

    # 통계 작성용
    sentence_count = 0
    token_count = 0
    
    # 전체 파일 목록을 순회하면서 처리
    for file_seq, source_file in enumerate(natsorted(source_path.glob('*.xlsx')), start=1):

        if file_seq > task_limit:
            break

        print(f'{now()}Processing {file_seq} / {task_limit}')

        df = pandas.read_excel(source_file)
        
        print(f'{now()}{source_file.name} converted to dataframe')

        new_file = False

        # 엑셀 파일을 순회하면서 처리
        for i in range(0, len(df), 2):
            # 2행씩 묶어서 처리
            # 두 번째 행의 열 중 Column2(인덱스 14)부터 끝까지 가져옴
            # nan 제외하고 가져오기
            # 이 정보를 리스트로 변환
            try:
                first_row = df.iloc[i].dropna()
                tags_list = df.iloc[i + 1, 13:]

            except IndexError:
                # 정확한 원인은 모르겠으나, IndexError가 발생하는 경우가 있음. 이런 때 해당 파일은 마지막 부분이므로 건너뜀
                break
            
            # 오류는 아니지만, 반드시 수정해서 처리해야 하는 부분 (이슈 핸들링)
            # 2번째 행에 "O"가 있어야 할 위치에 아무 데이터도 없는 상황이 존재함.
            # 이 경우, first_row와 대조하여 데이터가 없는 위치에 "O"를 삽입함
            # 그 뒤 dropna().tolist()를 통해 리스트로 변환
            if "O" not in tags_list.tolist():
                for tag_idx, col in enumerate(first_row[14:]):
                    if pandas.isna(tags_list.iloc[tag_idx]):
                        tags_list.iloc[tag_idx] = "O"
            tags_list = tags_list.dropna().tolist()

            # 오류 핸들링
            # 데이터의 K열부터 없는 경우(즉 length가 11 미만인 경우), Word_Count가 0인 경우 : 오류므로 해당 행은 건너뜀
            if "Word_Count" in first_row and int(first_row["Word_Count"]) == 0:
                continue
            # data_columns에 적힌 key 중 하나라도 없는 경우 : 오류므로 해당 행은 건너뜀
            # 단, Pub_Subj가 없는 경우만큼은 오류로 간주하지 않음
            if data_columns_set - set(first_row.index) != set():
                continue
                # if "Doc_ID" in first_row.index and "Pub_Subj" not in first_row.index and len(first_row) >= 11:
                #     pass
                # else:
                #     continue

            # Doc_ID의 길이가 190자를 넘는 경우 : 오류로 간주하고 해당 행은 건너뜀
            if len(first_row["Doc_ID"]) > 190:
                continue

            # Pub_Subj가 지정된 데이터 유형(str)이 아닌 경우 : Doc_ID에서 값을 역산함
            if "Pub_Subj" in first_row.index and not isinstance(first_row["Pub_Subj"], str):
                first_row["Pub_Subj"] = first_row["Doc_ID"].split("_")[2]

            # 실질 작업 부분: 지금 작업하는 부분이 새로운 파일인지, 기존 파일인지 확인
            if current_doc_id == "" or current_doc_id != first_row["Doc_ID"]:
                new_file = True
            else:
                new_file = False
            
            # 새롭게 파일을 만들 때
            if new_file:
                
                # 이미 작업한 파일이 있어 저장해야 하는 경우
                if current_doc_id != "":

                    # 폴더 생성
                    if task_count % file_scale == 0:
                        # file_scale개만큼 폴더에 파일이 생성되면, 새로운 폴더 생성
                        result_folder_num += 1
                        result_dir(result_path, result_folder_prefix, result_folder_num).mkdir(exist_ok=True)

                        print(f"{now()}{result_folder_num}번 폴더 생성")

                    # 파일 저장
                    with open(result_dir(result_path, result_folder_prefix, result_folder_num) / f'{current_doc_id}.json', 'w', encoding="utf-8-sig") as f:
                        json.dump(new_doc, f, indent=4, ensure_ascii=False)
                    task_count += 1

                # 초기화
                new_doc = dict()

                # 데이터 옮기기
                # Doc_ID, Sen_ID에 "/"가 들어가면 파일명으로 사용할 수 없으므로 "_"로 치환
                first_row["Doc_ID"] = evade_special_glyphs(first_row["Doc_ID"])
                first_row["Sen_ID"] = evade_special_glyphs(first_row["Sen_ID"])

                current_doc_id = first_row["Doc_ID"]

                new_doc["Doc_ID"] = first_row["Doc_ID"]
                new_doc["Filename"] = get_row_data(first_row, "Filename")
                new_doc["Title"] = get_row_data(first_row, "Title")
                new_doc["Text"] = get_row_data(first_row, "Text")
                new_doc["Pub_Type"] = get_row_data(first_row, "Pub_Type")
                new_doc["Pub_Subj"] = get_row_data(first_row, "Pub_Subj")

                new_doc["Pub_Date"] = convert_date(first_row["Pub_Date"])
                new_doc["Col_Date"] = convert_date(first_row["Col_Date"])
                new_doc["data"] = []

                # 추가 지침 : Pub_Subj에 "koreana"나 "terkinni"가 포함될 경우 (대소문자 구분 없음), Pub_Type을 Pub_Subj로 변경
                # 단, 그렇게 변경하는 Pub_Type은 "Koreana" 혹은 "Terkinni"로 변경

                if "koreana" in new_doc["Pub_Subj"].lower():
                    new_doc["Pub_Type"] = "Koreana"
                    # new_doc["Doc_ID"].replace("newsdata", "koreana")
                    # # Doc_ID로 파일명 변경
                    # current_doc_id = new_doc["Doc_ID"]

                elif "terkinni" in new_doc["Pub_Subj"].lower():
                    new_doc["Pub_Type"] = "Terkinni"
                    # new_doc["Doc_ID"].replace("newsdata", "terkinni")
                    # # Doc_ID로 파일명 변경
                    # current_doc_id = new_doc["Doc_ID"]
            
            # 새 파일 혹은 기존 파일에 작업할 때: data 리스트에 추가할 dict 생성
            data = {}

            data["Sen_ID"] = first_row["Sen_ID"]
            data["Word_Count"] = int(first_row["Word_Count"])
            data["NER_Count"] = 0 # 미리 선언
            data["Anno_ID"] = "IN_001"
            data["Raw_data"] = first_row["Tokenized_Sentence"]
            # first_row["Tokenized_Sentence"]가 str이 아닌 경우가 있음. 이 경우, Token을 공백으로 이어붙임
            if not isinstance(first_row["Tokenized_Sentence"], str):
                data["Raw_data"] = " ".join(eval(first_row["Token"]))
            data["Entities_list"] = JSONformat_handler.handle_tag_exceptions_by_data(data["Raw_data"], tags_list)

            data["Entities"] = common.make_entity_data(data["Raw_data"], data["Entities_list"])
            data["NER_Count"] = len(data["Entities"])

            new_doc["data"].append(data)

            sentence_count += 1
            token_count += data["Word_Count"]
            
    # 통계 저장
    if statistic:
        statistic_dict["files"] = task_count
        statistic_dict["total_sentences"] = sentence_count
        statistic_dict["total_tokens"] = token_count
        with open(result_path / "statistic.json", 'w', encoding="utf-8") as f:
            json.dump(statistic_dict, f, indent=2, ensure_ascii=False)

