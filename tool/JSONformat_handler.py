import re, json, unicodedata
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
    "Col_Date": str
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

DIACRITICS_MAP = {
    'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a', 'å': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o', 'ø': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    'ý': 'y', 'ÿ': 'y',
    'ç': 'c', 'ñ': 'n',
    'Á': 'A', 'À': 'A', 'Â': 'A', 'Ä': 'A', 'Ã': 'A', 'Å': 'A',
    'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
    'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
    'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Ö': 'O', 'Õ': 'O', 'Ø': 'O',
    'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
    'Ý': 'Y',
    'Ç': 'C', 'Ñ': 'N'
}

# Dictionary mapping common Latin ligatures to their decompositions
LIGATURE_MAP:dict[str, str] = {
    'æ': 'ae',
    'œ': 'oe',
    'ß': 'ss',  # German sharp s
    # Add more mappings as needed
}

@dataclass
class Entity:
    major: str
    minor: str = ""
    ending: str = "" # "B", "I"

    def is_valid(self):
        if self.major not in MAJOR_SET:
            return False
        if self.minor != "" and self.minor not in MINOR_SET:
            return False
        if self.ending != "" and self.ending not in ENDING_SET:
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

def remove_diacritics(text:str) -> str:
    # Replace characters in the input string based on the diacritics_map
    for diac, basic in DIACRITICS_MAP.items():
        text = text.replace(diac, basic)
    
    return text

def split_latin_ligatures(text:str) -> str:

    # Replace each ligature in the text with its decomposition
    for ligature, decomposition in LIGATURE_MAP.items():
        text = text.replace(ligature, decomposition)
    
    return text

def remove_duplicates_keep_order(lst):
    result = []
    seen = set()
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

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

def handle_format_exceptions(jsonfile:dict):

    jsonfile = common.update_key(jsonfile, 'Raw-Data', 'Raw_data')

    if 'Doc_ID' not in jsonfile:
        jsonfile = common.update_key(jsonfile, 'Filename', 'Doc_ID')

    if 'Pub_Date' not in jsonfile:
        jsonfile = common.update_key(jsonfile, 'Pub_date', 'Pub_Date')
    
    if 'Col_Date' not in jsonfile:
        jsonfile = common.update_key(jsonfile, 'Coll_Date', 'Col_Date')
        jsonfile = common.update_key(jsonfile, 'Coll_date', 'Col_Date')
        jsonfile = common.update_key(jsonfile, 'Col_date', 'Col_Date')
    
    if 'Sen_ID' not in jsonfile:
        jsonfile = common.update_key(jsonfile, 'SEN_ID', 'Sen_ID')
    
    if 'Anno_ID' not in jsonfile:
        jsonfile = common.update_key(jsonfile, 'ANNO_ID', 'Anno_ID')

    if 'Text' not in jsonfile:
        text_list = [item["Raw_data"] for item in jsonfile["data"]]
        jsonfile['Text'] = " ".join(text_list)
    
    for item in jsonfile["data"]:
        if isinstance(item["Word_Count"], float): item["Word_Count"] = int(item["Word_Count"])
    
    return jsonfile

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
            entity = Entity(*tag.split("-"))
            if not entity.is_valid():
                common.print_log(f"Doc_ID : {jsonfile['Doc_ID']}\n{tag} 태그 형태 오류 발생")
                entity = Entity(DEFAULT_TAG)
            memory.append(entity)

            if memory.is_full() and memory.first.is_blank() and not memory.second.is_blank():
                if not memory.second.is_ending_B():
                    memory.second.ending = "B"

            new_entities_list.append(entity.string)

        item["Entities_list"] = new_entities_list
    
    return jsonfile

def handle_content_exceptions(jsonfile:dict):
    """
    Text : 좌우 공백이 남은 경우 오류. strip() 메소드로 좌우 공백 제거
    Anno_ID : IN_001 등 숫자가 4자리로 끝나지 않으면 면 오류. zfill() 메소드로 숫자를 4자리로 만들기
    한 문장에 5토큰 미만인 경우 문장 데이터 자체를 버리기 (그 문장이 문서의 마지막 문장인 경우, None 값을 반환)
    Doc_ID, Sen_ID : <Pub_Subj> 부분과 숫자 부분 사이에 _ 문자가 없는 경우 오류. 언더바 집어넣기
    """
    
    # 파일 전체를 문자열로 변환한 뒤 다이어크리틱 제거, 로마자 합자 변환
    jsonfile_string = json.dumps(jsonfile, ensure_ascii=False)
    jsonfile_string = remove_diacritics(jsonfile_string)
    jsonfile_string = split_latin_ligatures(jsonfile_string)
    jsonfile = json.loads(jsonfile_string)
    
    title = jsonfile['Title']
    # regex_pattern = r'[A-Za-z0-9 !@#$%^&*()_+{}[\]\―\:;<>,"‘’”“\'.°=?~`/-]+'

    new_title = re.sub(r'[^A-Za-z0-9 !@#$%^&*()_+{}[\]\―\:;<>,"‘’”“\'.?~`/-]+', '', title)
    jsonfile['Title']=new_title
    
    pub_subj = jsonfile['Pub_Subj']
    new_subj = re.sub(r'[^A-Za-z0-9 !@#$%^&*()_+{}[\]\―\:;<>,"‘’”“\'.?~`/-]+', '', pub_subj)
    new_subj = new_subj.replace('/', '_')
    
    if "wikidata" in jsonfile["Doc_ID"]: # 위키 데이터에 한해 특수하게 적용
        new_subj = "_".join(remove_duplicates_keep_order(new_subj.split("_"))) # 중복되는 부분 제거
        if new_subj.__len__() > 100: new_subj = new_subj[:100].strip() # 100자 이상인 경우 자르기
    
    jsonfile['Pub_Subj'] = new_subj
    
    jsonfile["Text"] = jsonfile["Text"].strip()
    
    if jsonfile["Pub_Type"] == "Koreana": jsonfile["Pub_Type"] = "Newspaper"

    # if 'twitter' == jsonfile['Doc_ID'].split("_")[1]:
    #     # Sen_ID에서 _sen 부분을 지우고 숫자 앞의 언더바 가져오기
    #     sen_id_parts:list = jsonfile["data"][0]["Sen_ID"].split("_")[:-2]
    #     new_doc_id_suffix =  jsonfile["data"][0]["Sen_ID"].split("_")[-2]

    #     # 새로운 Doc_ID 생성
    #     matches = re.match(r"([a-zA-Z ]+)([0-9]+)", new_doc_id_suffix)
    #     if matches:
    #         # 영문 부분과 숫자 부분 추출
    #         letters_part = matches.group(1)
    #         numbers_part = matches.group(2)
    #         numbers_part = numbers_part

    #     else:
    #         print(f"{new_doc_id_suffix} 일치하는 패턴이 없습니다.")
            
    #     sen_id_parts.append(letters_part)
    #     sen_id_parts.append(numbers_part)
    
    doc_id_split = jsonfile["Doc_ID"].split("_")
    jsonfile['Doc_ID']='_'.join(doc_id_split[:2])+"_"+jsonfile["Pub_Subj"] + "_" + doc_id_split[-1].zfill(7)
      
    for idx, item in enumerate(jsonfile["data"]):

        if item["Word_Count"] < 5:
            if jsonfile["data"].__len__() == 1:
                return None
            else:
                jsonfile["data"].pop(idx)
        
        Anno_ID_split = item["Anno_ID"].split("_")
        if Anno_ID_split[-1].__len__() < 4:
            item["Anno_ID"] = '_'.join(Anno_ID_split[:-1]) + "_" + Anno_ID_split[-1].zfill(4)
        #새로운 Sen_ID 부여    
        sen_id=item['Sen_ID'].split('_')[-1]
        new_sen_id = jsonfile['Doc_ID']+'_'+sen_id
        item['Sen_ID']=new_sen_id
        item["Raw_data"] = item["Raw_data"].strip()
    
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