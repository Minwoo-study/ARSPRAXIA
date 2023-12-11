"""
json 파일 형식
{
    "Doc_ID": "20230808_newsdata_Korea_007413",
    "Filename": "",
    "Title": "Kang Daniel Dipilih Sebagai Wajah Baru untuk Merek Kecantikan Global Mernel", # 제목
    "Text": "Kang Daniel Dipilih Sebagai Wajah Baru untuk Merek Kecantikan Global Mernel", # 본문
    "Pub_Type": "Newspaper",
    "Pub_Subj": "Korea",
    "Pub_Date": "2021-01-01",
    "Col_Date": "2023-08-08",
    "data": [
        ...
    ]
}

data에 들어갈 dict 형식
{
    "Sen_ID": "20230808_newsdata_Korea_007413_sen000001",
    "Word_Count": 10,
    "NER_Count": 1,
    "Anno_ID": "IN_001",
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

csv 파일 형식
Doc_ID, Filename, Title, Pub_Type, Pub_Subj, Pub_Date, Col_Date, Sen_ID, Word_Count, Text, Sentence, Token

- Sentence와 Tokenized_Sentence는 아예 같을 게 뻔한데 따로 만들어야 하는지 물어봐야

csv 파일의 데이터 행이 5만개가 넘어가면 파일을 새로 만들어야 함
"""

import json, pandas, re
from pathlib import Path
from tool import common

columns = [
    "Doc_ID",
    "Filename",
    "Title",
    "Pub_Type",
    "Pub_Subj",
    "Pub_Date",
    "Col_Date",
    "Sen_ID",
    "Word_Count",
    "Text",
    "Sentence",
    "Token"
]

columns_datatype = {
    "Doc_ID": str,
    "Filename": str,
    "Title": str,
    "Pub_Type": str,
    "Pub_Subj": str,
    "Pub_Date": str,
    "Col_Date": str,
    "Sen_ID": str,
    "Word_Count": int,
    "Text": str,
    "Sentence": str,
    "Token": str
}

metadata_columns = [
    "Doc_ID",
    "Filename",
    "Title",
    "Pub_Type",
    "Pub_Subj",
    "Pub_Date",
    "Col_Date",
    "Text"
]

data_columns = [
    "Sen_ID",
    "Word_Count"
]

def get_data(dictionary:dict, key:str):
    # key가 없으면 키에 맞는 기본값을 반환
    # str인 경우 ""를 반환
    # int인 경우 0을 반환

    if key in dictionary:
        return dictionary[key]
    else:
        if isinstance(key, str):
            return ""
        elif isinstance(key, int):
            return 0


def main(
    source_path:Path,
    target_path:Path,
    *,
    result_file_prefix:str,
    result_file_start_num:int=1,
    file_scale:int=50000,
    max_token:int=None,
    encoding:str="utf-8-sig",
    ban_pattern:str = r"statistic"
):
    target_path.mkdir(parents=True, exist_ok=True)
    ban = re.compile(ban_pattern)

    result_file_num = result_file_start_num
    create_result_file_path = lambda : target_path / f"{result_file_prefix}_{result_file_num}.csv"

    def initiate_result_file():

        result_file = pandas.DataFrame()

        # result_file에 컬럼 추가
        # dtype은 columns_datatype에 있는 데이터 타입으로 설정
        for column in columns:
            result_file[column] = pandas.Series(dtype=columns_datatype[column])

        return result_file
    
    def create_and_initiate_file(result_file:pandas.DataFrame, task_count, token_count):
        result_file_path = create_result_file_path()
        result_file.to_csv(result_file_path, index=False, encoding=encoding)
        common.print_log(f"file created : {result_file_path.name}")
        common.print_log(f"task count : {task_count}")
        common.print_log(f"token count : {token_count}")
        return initiate_result_file()
    
    result_file = initiate_result_file()

    file_count = 0
    task_count = 0
    token_count = 0

    common.print_log("task started.")

    try:

        for json_file_path in source_path.glob("**/*.json"):

            # ban_pattern에 해당하는 파일은 건너뜀
            if ban.search(json_file_path.name): continue

            # max_token에 해당하는 토큰 개수를 넘으면 task를 중단함
            if max_token and token_count >= max_token: common.print_log("max_token reached; task stopped."); break

            if task_count >= file_scale:
                result_file = create_and_initiate_file(result_file, task_count, token_count)
                result_file_num += 1
                task_count = 0

            json_file = json.load(json_file_path.open(encoding="utf-8-sig"))

            for data in json_file["data"]:

                # result_file에 데이터 추가

                # # 데이터 타입이 맞지 않으면 기본값으로 설정 (str: "", int: 0)
                # # 
                # if not isinstance(data["Raw_data"], str): data["Raw_data"] = ""
                # if not isinstance(data["Word_Count"], int): data["Word_Count"] = 0

                for column in columns:
                    # metadata_columns에 있는 컬럼은 json_file에서 가져오고
                    # data_columns에 있는 컬럼은 data에서 가져옴

                    if column in metadata_columns:
                        result_file.loc[task_count, column] = get_data(json_file, column)
                    elif column in data_columns:
                        result_file.loc[task_count, column] = get_data(data, column)
                    else:
                        # Sentence의 경우 Raw_data에서 가져옴
                        # Token의 경우 Raw_data를 띄어쓰기로 나눈 리스트를 str로 변환하여 가져옴
                        
                        if column == "Sentence":
                            result_file.loc[task_count, column] = data["Raw_data"]
                        elif column == "Token":
                            result_file.loc[task_count, column] = str(data["Raw_data"].split())
                
                task_count += 1
                token_count += data["Word_Count"]
            
            file_count += 1

        # 마지막 파일 저장
        create_and_initiate_file(result_file, task_count, token_count)

    except Exception as e:
        common.print_log(f"task failed. {e}")
        common.print_log(f"last json file: {json_file_path}")
        common.print_log(f"task count: {task_count}, token count: {token_count}")

