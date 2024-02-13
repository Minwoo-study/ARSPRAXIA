import json
from pathlib import Path
from time import time
from datetime import datetime
import re

key_alt = {
    "Raw-Data" : "Raw_data", 
    "SEN_ID" : "Sen_ID"
}

current_time = datetime.now().strftime("%y%m%d-%H%M%S")

def get_value(data:dict, key:str):
    """
    data에서 key에 해당하는 value를 반환하는 함수
    """
    try:
        return data[key]
    except KeyError:
        return data[key_alt[key]]

# def if_entities_is_list(raw_data, result, json_file, entities:list[str]):

#     default = dict()
#     # entity : {
#     #     entity_class : [f"{json_file.stem}||{data['SEN_ID']}"],
#     #     entity_class : [f"{json_file.stem}||{data['SEN_ID']}"],
#     #     ...
#     # } 구조

#     entity = ""
#     entity_class = ""
#     for idx, entityClass in enumerate(entities):

#         # entityClass가 B로 끝나면 새로운 entity가 시작된다는 의미
#         # entityClass가 I로 끝나면 기존 entity에 이어서 entity가 이어진다는 의미
#         # 그러나 명시적으로 entityClass가 끝나는 경우가 없기 때문에, 다음 entityClass가 B로 시작하거나 O로 시작하면 entity가 끝난다고 가정
#         end = False

#         try: # 데이터의 raw_data 길이와 entities 길이가 다를 수 있기 때문에 예외처리
#             if entityClass.endswith("B"):
#                 entity = raw_data[idx]
#                 entity_class = entityClass[:-2]
                
#             elif entityClass.endswith("I") and entity_class == entityClass[:-2]:
#                 entity += " " + raw_data[idx]
#         except IndexError:
#             break

#         # entity가 끝남을 판정
#         next_entityClass = entities[idx+1] if idx+1 < len(entities) else None
#         if next_entityClass is None or next_entityClass.endswith("B") or next_entityClass.endswith("O"):
#             end = True
        
#         # entity가 끝났을 때만 저장
#         if end and entity != "" and entity_class != "":

#             default.setdefault(entity_class, [f"{json_file.stem}||{get_value(data, 'SEN_ID')}"])
            
#             if entity not in result:
#                 result.setdefault(entity, default)
#             else:
#                 if entity_class not in result[entity]:
#                     result[entity].setdefault(entity_class, default[entity_class])
#                 else:
#                     result[entity][entity_class].extend(default[entity_class])
#             # default.setdefault(entity_class, [f"{json_file.stem}||{data['SEN_ID']}"])
#             # result.setdefault(entity, default)
#             # 변수 초기화
#             entity = ""
#             entity_class = ""
#             default = dict()
    
#     return result

def main(target_dir:Path, result_dir:Path, *, file_name:str=None, task_limit:int=None, statistic:bool=False, report_interval:int=1000, ban_pattern:str="statistic"):
    """
    실행 시 target_dir에 있는 모든 json 파일을 읽어서 entity를 추출하고, result_dir에 결과를 저장함\n

    parameters:
    target_dir : json 파일들이 있는 디렉토리 (가장 상위 디렉토리여야 함)\n
    result_dir : 결과 파일들을 저장할 디렉토리\n
    file_name : 결과 파일의 이름(확장자 포함해야 함). None이면 result_{current_time}.json으로 저장됨\n
    task_limit : 처리할 파일 개수. None이면 전체 파일을 처리\n
    statistic : 문서 위치 대신 태그 개수로 따로 저장할지 여부. True면 statistic 파일을 추가로 산출함\n
    report_interval : 작업한 파일 n개마다 작업 완료 메시지를 출력함
    """

    if not target_dir.exists():
        raise FileNotFoundError(f"{target_dir}가 존재하지 않습니다.")
    
    result_dir.mkdir(parents=True, exist_ok=True)

    _task_limit = '_' + str(task_limit) if task_limit else ''
    result_file = result_dir /  f"result_{current_time}{_task_limit}.json"

    if file_name: result_file = result_dir / file_name

    result:dict[str, dict[str, list[str]|int]] = dict()

    count = 0

    for json_file in target_dir.glob("**/*.json"):

        if re.search(ban_pattern, json_file.stem): continue

        if isinstance(task_limit, int) and count >= task_limit: break

        if count % report_interval == 0 and count != 0:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {count}개의 파일을 처리했습니다.")

        with open(json_file, "r", encoding="utf-8-sig") as f:
            json_data = json.load(f)

        for data in json_data["data"]:
            
            for entity_data in data["Entities"]:

                entity = entity_data["entity"]
                entity_class = entity_data["entityClass"]

                if entity not in result:

                    result[entity] = dict()

                if entity_class not in result[entity]:

                    result[entity][entity_class] = [f"{json_file.stem}||{get_value(data, 'SEN_ID')}"]
                    
                else:

                    result[entity][entity_class].append(f"{json_file.stem}||{get_value(data, 'SEN_ID')}")

        count += 1
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    if statistic:
        for entity, entity_class in result.items():
            for entity_class, data in entity_class.items():
                result[entity][entity_class] = len(data)

        # 파일명에 _statistic 추가
        result_file = Path(str(result_file).replace(".json", "_statistic.json"))
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
