import re
from collections import OrderedDict
from pathlib import Path
from dataclasses import dataclass
from tool import common

metadata_keys_dtype = {
    "Doc_ID": str,
    "Filename": str,
    "Title": str,
    "Text": str,
    "Pub_Type": str,
    "Pub_Subj": str,
    "Pub_Date": str,
    "Col_Date": str,
    "Sen_ID": str
}

data_keys_dtype = {
    "Sen_ID": str,
    "Word_Count": int,
    "NER_Count": int,
    "Anno_ID": str,
    "Raw_data": str
}

Entities_keys_dtype = {
    "entity": str,
    "entityClass": str,
    "entityStart": int,
    "entityEnd": int
}

MAJOR_SET = {"PS", "PD", "WA", "BO", "LC", "EV", "O"}
MINOR_SET = {"Name", "Character", "Group", "Sports", "Food", "Drink", "Clothing", "Cosmetic", "Vehicle", "Accessories", "Others", "Document", "Performance", "Video", "Art_Craft", "Music", "Musical_Instruments", "Economy", "Education", "Military", "Media", "Art", "Religion", "Law", "Politics", "Hotel", "Country", "Province", "City", "Space", "Building", "Activity", "Incident", "Festival"}
ENDING_SET = {"B", "I"}

DUPLICATED_TAG_PATTERN = re.compile(r"(PS)|(PD)|(WA)|(BO)|(LC)|(EV)")
DEFAULT_TAG = "O"



@dataclass
class Entity:
    major: str
    minor: str = ""
    ending: str = "" # "B", "I"

    def is_valid(self):
        if self.major not in MAJOR_SET or self.minor not in MINOR_SET or self.ending not in ENDING_SET:
            return False
        return True
    
    def is_blank(self):
        if self.major == "O": return True
        return False
    
    def is_ending_B(self):
        if self.ending == "B": return True
        return False

    def __str__(self):
        # 각 요소 사이에 '-'를 넣어서 반환
        # 단, major가 "O"인 경우에는 "O"를 반환
        if self.is_blank(): return "O"
        return f"{self.major}-{self.minor}-{self.ending}"

    @property
    def string(self):
        return self.__str__()

class EntityMemory:
    """
    Entity 클래스 2개를 큐 형태로 저장하는 클래스\n
    선언한 뒤 append 메서드를 통해 Entity 클래스를 추가하는 식으로 사용
    """

    def __init__(self):
        self._memory = []
        self._max_size = 2

    def append(self, entity:Entity):
        if not isinstance(entity, Entity): raise TypeError("param:entity must be Entity class")
        self._memory.append(entity)
        if len(self._memory) > self._max_size:
            self._memory.pop(0)
    
    def is_full(self):
        if len(self._memory) == self._max_size: return True
        return False
    
    def __str__(self):
        return str(self._memory)
    
    def __repr__(self):
        return str(self._memory)

    def __len__(self):
        return len(self._memory)
    
    @property
    def first(self) -> Entity:
        return self._memory[0]
    
    @property
    def second(self) -> Entity:
        return self._memory[1]
    

def is_tag_duplicated(tag:str):

    if len(DUPLICATED_TAG_PATTERN.findall(tag)) > 1:
        return True

def correct_metadata_dtype(dictionary:dict, key:str):
    # key가 없으면 키에 맞는 기본값을 반환
    # str인 경우 ""를 반환
    # int인 경우 0을 반환

    if key in dictionary:
        if isinstance(dictionary[key], metadata_keys_dtype[key]):
            return dictionary[key]
        else:
            if metadata_keys_dtype[key] == str:
                return ""
            elif metadata_keys_dtype[key] == int:
                return 0
    else:
        if metadata_keys_dtype[key] == str:
            return ""
        elif metadata_keys_dtype[key] == int:
            return 0

def correct_data_dtype(dictionary:dict, key:str):
    # key가 없으면 키에 맞는 기본값을 반환
    # str인 경우 ""를 반환
    # int인 경우 0을 반환

    if key in dictionary:
        if isinstance(dictionary[key], data_keys_dtype[key]):
            return dictionary[key]
        else:
            if data_keys_dtype[key] == str:
                return ""
            elif data_keys_dtype[key] == int:
                return 0
    else:
        if data_keys_dtype[key] == str:
            return ""
        elif data_keys_dtype[key] == int:
            return 0

def handle_format_exceptions(data:dict):

    data = common.update_key(data, 'Raw-Data', 'Raw_data')

    if 'Doc_ID' not in data:
        data = common.update_key(data, 'Filename', 'Doc_ID')

    if 'Pub_Date' not in data:
        data = common.update_key(data, 'Pub_date', 'Pub_Date')
    
    if 'Col_Date' not in data:
        data = common.update_key(data, 'Coll_Date', 'Col_Date')
        data = common.update_key(data, 'Coll_date', 'Col_Date')
        data = common.update_key(data, 'Col_date', 'Col_Date')
    
    if 'Sen_ID' not in data:
        data = common.update_key(data, 'SEN_ID', 'Sen_ID')
    
    if 'Anno_ID' not in data:
        data = common.update_key(data, 'ANNO_ID', 'Anno_ID')

    if 'Text' not in data:
        text_list = [item["Raw_data"] for item in data["data"]]
        data['Text'] = " ".join(text_list)
    
    for item in data["data"]:
        if isinstance(item["Word_Count"], float): item["Word_Count"] = int(item["Word_Count"])
    
    return data

def handle_dtype_exceptions(jsonfile:dict):
    """
    각각의 dtype을 체크하고, 오류가 있는 경우 수정
    jsonfile : json 가공 파일 자체 데이터
    """

    for metadata_key in metadata_keys_dtype.keys():
        # correct_dtype 함수를 통해 각각의 dtype을 체크하고, 오류가 있는 경우 수정
        jsonfile[metadata_key] = correct_metadata_dtype(jsonfile, metadata_key)

    for item in jsonfile["data"]:
        for data_key in data_keys_dtype.keys():
            # correct_dtype 함수를 통해 각각의 dtype을 체크하고, 오류가 있는 경우 수정
            item[data_key] = correct_data_dtype(item, data_key)

    return jsonfile

def handle_tag_exceptions(jsonfile:dict):
    """
    태그 오류를 수정\n
    1. Raw_data와 Entities_list 길이 오류 대처
    2. 태그 형태 오류 대처
    3. 태그 사용 오류 대처

    jsonfile : json 가공 파일 자체 데이터
    """

    data = jsonfile["data"]

    for item in data:
        
        entities_list:list[str] = item["Entities_list"]

        raw_data:str = item["Raw_data"]

        raw_data_split = raw_data.split()
        
        # Raw_data를 split한 리스트와 Entities_list의 길이가 다른 경우 대처
        if raw_data_split.__len__() > entities_list.__len__():
            # 부족한 수만큼 entities_list에 추가 (맨 뒤에 추가)
            while raw_data_split.__len__() > entities_list.__len__():
                entities_list.append("O")
        elif raw_data_split.__len__() < entities_list.__len__():
            # 넘치는 수만큼 entities_list에서 제거 (맨 뒤에서부터 제거)
            while raw_data_split.__len__() < entities_list.__len__():
                entities_list.pop()
        
        # 태그 오류 대처
        new_entities_list = []
        memory = EntityMemory()
        for tag in entities_list:

            # 태그 수정
            if not isinstance(tag, str): tag = DEFAULT_TAG; continue

            tag = tag.strip()
            if is_tag_duplicated(tag): tag = DEFAULT_TAG; continue

            tag = re.sub(r"(Art.Craft)|ARC", "Art_Craft", tag)
            tag = re.sub(r"mnet", "ment", tag)
            tag = re.sub(r"ACC", "Accessories", tag)
            tag = re.sub(r"Musical-", "Musical_", tag)
            tag = re.sub(r"MUI", "Musical_Instruments", tag)
            tag = re.sub(r"Cosmetics", "Cosmetic", tag)
            # "-"와 "_"를 제외한 모든 특수문자 제거
            tag = re.sub(r"[^\w-]", "", tag)

            # 걸러지지 않은 태그 형태가 발견될 경우 콘솔에 Doc_ID와 태그를 출력
            try:
                entity = Entity(*tag.split("-"))
            except TypeError:
                common.print_log(f"Doc_ID : {jsonfile['Doc_ID']}\n{tag} 태그 형태 오류 발생")
            memory.append(entity)

            if memory.is_full() and memory.first.is_blank() and not memory.second.is_blank():
                if not memory.second.is_ending_B():
                    memory.second.ending = "B"

            new_entities_list.append(entity.string)

        item["Entities_list"] = new_entities_list
    
    return jsonfile

def arrange_json_format(jsonfile:dict):
    """
    컴퓨터에게는 아무 의미 없지만 사람에게 의미 있는 순서로 jsonfile을 재배열
    """
    for idx, data in enumerate(jsonfile["data"]):
        data = {
            "Sen_ID": data["Sen_ID"],
            "Word_Count": data["Word_Count"],
            "NER_Count": data["NER_Count"],
            "Anno_ID": data["Anno_ID"],
            "Raw_data": data["Raw_data"],
            "Entities_list": data["Entities_list"],
            "Entities": data["Entities"]
        }
        jsonfile["data"][idx] = data
    
    return {
    "Doc_ID": jsonfile["Doc_ID"],
    "Filename": jsonfile["Filename"],
    "Title": jsonfile["Title"],
    "Text": jsonfile["Text"],
    "Pub_Type": jsonfile["Pub_Type"],
    "Pub_Subj": jsonfile["Pub_Subj"],
    "Pub_Date": jsonfile["Pub_Date"],
    "Col_Date": jsonfile["Col_Date"],
    "data": jsonfile["data"]
    }
# if __name__ == "__main__":

#     folder_path = Path("C:\\Users\\정진혁\\offline_main\\datas\\article_jsons\\article_0808")

#     cwd = Path.cwd()
#     result_fir = cwd / "result"
#     result_fir.mkdir(exist_ok=True)

#     # 폴더 내의 모든 JSON 파일에 대해 처리
#     count = 0
#     whole_count = len(list(folder_path.glob("*.json")))
#     if folder_path.exists() and folder_path.is_dir():
#         for file_path in folder_path.glob("*.json"):
#             data = read_json(file_path)
#             data = update_key(data, 'Raw-Data', 'Raw_data')
#             data = update_key(data, "Col_Date", "Coll_Date")
#             updated_data = put_entity(data)
            
#             write_json(updated_data, result_fir / file_path.name)

#             count += 1
#             print(f"{file_path.name} 처리 완료\t({count}/{whole_count})")