from pathlib import Path
import json, re

from tool.common import ConsoleLogger

# target_dir = Path("C:\\Users\\정진혁\\Ars Praxia\\[T] 23-05-001 NIA AI 데이터셋 구축 - General\\06-수집데이터\\가공 완료 데이터\\가공 완료 데이터 종합(바로잡음)")

def main(target_folder:Path, result_file_path:str|Path, *,report_interval:int=10000, tag_count:bool=False, tag_by_PubType:bool=False):

    cl = ConsoleLogger()

    result = {
        "files":0,
        "total_sentences": 0,
        "total_tokens": 0
    }

    if tag_count:
        result["tags"] = dict()

    ban = re.compile(r"statistic")

    for json_file in target_folder.glob("**/*.json"):

        if ban.search(json_file.name): continue

        with open(json_file, "r", encoding="utf-8-sig") as f:
            json_data = json.load(f)

        result["files"] += 1

        result["total_sentences"] += len(json_data["data"])

        for data in json_data["data"]:
            word_count = data["Word_Count"]
            if not isinstance(word_count, (int, float)):
                continue
            result["total_tokens"] += int(word_count)

            if tag_count and not tag_by_PubType:
                
                for entity in data["Entities"]:
                    tag = entity["entityClass"]

                    if tag not in result["tags"]:
                        result["tags"][tag] = 1
                    else:
                        result["tags"][tag] += 1
            
            elif tag_count and tag_by_PubType:
                pubType = json_data["Pub_Type"]
                if pubType not in result["tags"]:
                    result["tags"][pubType] = dict()
                for entity in data["Entities"]:
                    tag = entity["entityClass"]

                    if tag not in result["tags"][pubType]:
                        result["tags"][pubType][tag] = 1
                    else:
                        result["tags"][pubType][tag] += 1
        
        if result["files"] % report_interval == 0:
            cl.print(f"{result['files']} files processed.")
    
    if tag_count and not tag_by_PubType:
        result["tags"] = dict(sorted(result["tags"].items(), key=lambda x:x[1], reverse=True))
    elif tag_count and tag_by_PubType:
        for pubType in result["tags"]:
            result["tags"][pubType] = dict(sorted(result["tags"][pubType].items(), key=lambda x:x[1], reverse=True))

    with open(result_file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
