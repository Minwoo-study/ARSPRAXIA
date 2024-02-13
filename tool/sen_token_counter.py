from pathlib import Path
import json, re

from tool.common import DEFAULT_ENCODING

# target_dir = Path("C:\\Users\\정진혁\\Ars Praxia\\[T] 23-05-001 NIA AI 데이터셋 구축 - General\\06-수집데이터\\가공 완료 데이터\\가공 완료 데이터 종합(바로잡음)")

def continuous(target_folder:Path, previous_result:dict = None):
    
    result = {
        "files":0,
        "total_sentences": 0,
        "total_tokens": 0
    }
    
    if previous_result:
        result = previous_result
    
    ban = re.compile(r"statistic")

    for json_file in target_folder.glob("**/*.json"):

        if ban.search(json_file.name): continue

        with open(json_file, "r", encoding=DEFAULT_ENCODING) as f:
            json_data = json.load(f)

        result["files"] += 1

        result["total_sentences"] += len(json_data["data"])

        for data in json_data["data"]:
            word_count = data["Word_Count"]
            if isinstance(word_count, str):
                continue
            result["total_tokens"] += int(word_count)
    
    return result

def main(target_folder:Path, result_file_name):

    result = {
        "files":0,
        "total_sentences": 0,
        "total_tokens": 0
    }

    ban = re.compile(r"statistic")

    for json_file in target_folder.glob("**/*.json"):

        if ban.search(json_file.name): continue

        with open(json_file, "r", encoding=DEFAULT_ENCODING) as f:
            json_data = json.load(f)

        result["files"] += 1

        result["total_sentences"] += len(json_data["data"])

        for data in json_data["data"]:
            word_count = data["Word_Count"]
            if isinstance(word_count, str):
                continue
            result["total_tokens"] += int(word_count)

    with open(result_file_name, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
