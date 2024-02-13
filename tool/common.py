from pathlib import Path
from collections import OrderedDict
from datetime import datetime
import json, re

YMDHMS = "%Y-%m-%d %H:%M:%S"
YMDHMS_FILENAME = "%Y%m%d_%H%M%S"

DUPLICATED_TAG_PATTERN = re.compile(r"(PS)|(PD)|(WA)|(BO)|(LC)|(EV)")
DEFAULT_TAG = "O"

DEFAULT_ENCODING = "utf-8-sig"

def is_tag_duplicated(tag:str):

    if len(DUPLICATED_TAG_PATTERN.findall(tag)) > 1:
        return True

def read_json(file_path):
    # JSON 파일을 읽어옵니다.

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
    except json.decoder.JSONDecodeError:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

    return data

def write_json(data, file_path):

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_key(data, old_key, new_key):
    """
    Update the key in a nested OrderedDict
    """
    if isinstance(data, OrderedDict):
        for key, value in list(data.items()):
            if key == old_key:
                data[new_key] = data.pop(old_key)
                print_log(f"key updated: {old_key} -> {new_key}")
            else:
                update_key(value, old_key, new_key)
    elif isinstance(data, list):
        for item in data:
            update_key(item, old_key, new_key)
    return data

def make_entity_data(raw_data:str, entities_list:list) -> list:
    entity_data = []
    current_entity = None
    
    for i, (token, entity_tag) in enumerate(zip(raw_data.split(), entities_list)):
        if entity_tag != 'O':
            # 개체명 클래스와 타입 (B/I)을 분리합니다.
            ent_class, ent_type = entity_tag.rsplit('-', 1)
            
            if ent_type == 'B':
                # 새로운 개체명이 시작되었습니다.
                if current_entity:
                    # 이전 개체명 정보를 저장합니다.
                    entity_data.append(current_entity)
                    
                # 새 개체명 정보를 초기화합니다.
                current_entity = {
                    "entity": token,
                    "entityClass": ent_class,
                    "entityStart": i,
                    "entityEnd": i
                }
                
            elif ent_type == 'I' and current_entity and ent_class == current_entity['entityClass']:
                # 이전 개체명이 계속되고 있습니다.
                current_entity['entity'] += " " + token
                current_entity['entityEnd'] = i
                
        else:
            # 개체명이 끝났습니다.
            if current_entity:
                entity_data.append(current_entity)
                current_entity = None
    
    # 마지막 개체명이 있다면 추가합니다.
    if current_entity:
        entity_data.append(current_entity)
    
    return entity_data

def update_entity_info(sentence_data):

    Raw_data = sentence_data['Raw_data']
    
    if isinstance(Raw_data, float):
        return
    else:
        entity_data = make_entity_data(Raw_data, sentence_data['Entities_list'])
    
    return entity_data

def put_entity(jsonfile:dict):
    """
    Entities 필드 오류 시 대처
    data : json 가공 파일 자체의 데이터
    """
    for sentence_data in jsonfile['data']:
        # 이미 업데이트가 진행되었는지 확인합니다.
        if 'Entities_list' not in sentence_data:
            # 기존 Entities 필드를 Entities_list로 이름을 바꿉니다.
            
            entities_list = sentence_data.pop('Entities')
            sentence_data['Entities_list'] = entities_list
            # 새로운 개체명 정보를 Entities로 추가합니다.
            sentence_data['Entities'] = update_entity_info({'Raw_data': sentence_data['Raw_data'], 'Entities': entities_list})
            sentence_data['NER_Count'] = len(update_entity_info({'Raw_data': sentence_data['Raw_data'], 'Entities': entities_list}))
            # 변경된 Entities_list를 다시 추가합니다.
    return jsonfile

def str_to_path(path:str|Path) -> Path:
    if not isinstance(path, (str, Path)):
        raise TypeError(f"str_to_path() argument must be str or Path, not {type(path).__name__}")
    return Path(path) if isinstance(path, str) else path

# def handle_tag_exceptions_in_item(item:dict):

#     entities_list:list[str] = item["Entities_list"]

#     # Raw_data가 str이 아닌 경우 오류로 인해 데이터가 비어있는 것 -> 빈 문자열로 대체
#     if not isinstance(item["Raw_data"], str):
#         item["Raw_data"] = ""

#     raw_data:str = item["Raw_data"]

#     raw_data_split = raw_data.split()
    
#     # Raw_data를 split한 리스트와 Entities_list의 길이가 다른 경우 대처
#     if raw_data_split.__len__() > entities_list.__len__():
#         # 부족한 수만큼 entities_list에 추가 (맨 뒤에 추가)
#         while raw_data_split.__len__() > entities_list.__len__():
#             entities_list.append("O")
#     elif raw_data_split.__len__() < entities_list.__len__():
#         # 넘치는 수만큼 entities_list에서 제거 (맨 뒤에서부터 제거)
#         while raw_data_split.__len__() < entities_list.__len__():
#             entities_list.pop()
    
#     # 태그 오류 대처
#     new_entities_list = []
#     for tag in entities_list:
#         if not isinstance(tag, str): tag = DEFAULT_TAG; continue

#         tag = tag.strip()
#         if is_tag_duplicated(tag): tag = DEFAULT_TAG; continue

#         # 발견된 오류 수정
#         tag = re.sub(r"(Art.Craft)|ARC", "Art_Craft", tag)
#         tag = re.sub(r"mnet", "ment", tag)
#         tag = re.sub(r"ACC", "Accessories", tag)
#         tag = re.sub(r"Musical-", "Musical_", tag)
#         tag = re.sub(r"MUI", "Musical_Instruments", tag)
#         tag = re.sub(r"Cosmetics", "Cosmetic", tag)
#         # "-"와 "_"를 제외한 모든 특수문자 제거
#         tag = re.sub(r"[^\w-]", "", tag)

#         new_entities_list.append(tag)
#     item["Entities_list"] = new_entities_list

#     return item



def print_log(message:str):
    print(f"{datetime.now()}\t{message}")
    
class ConsoleLogger:
    
    def __init__(self, initial_message:bool = False):
        
        self._timestamp = datetime.now()
        
        if initial_message:
            self.print("ConsoleLogger Initialized")
        
    def now(self):
        return datetime.now().strftime("%H:%M:%S") + "\t"
    
    def calculate_timedelta(self):
        now = datetime.now()
        delta = now - self._timestamp
        self._timestamp = now
        
        return delta
    
    def print(self, message:str):
        
        print(f"{self.now()}(+{self.calculate_timedelta().__str__().split('.')[0]})\t{message}")

