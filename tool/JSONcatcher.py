from pathlib import Path
import json
from natsort import natsorted
from datetime import datetime
import re
from tool import common

def main(
    source_path:Path|str,
    result_path:Path|str,
    *,
    result_filename:str="result",
    ban_pattern:str=r"(statistic)|(1cycle)|(NER)",
    report_interval:int=1000
):

    source_path = common.str_to_path(source_path)
    result_path = common.str_to_path(result_path)

    if not source_path.exists(): raise FileNotFoundError(f"{source_path} not found")
    result_path.mkdir(exist_ok=True)

    result_file_path = result_path.joinpath(f"{result_filename}.json")
    result_file = set()

    task_count = 0
    for json_file_path in natsorted(source_path.glob("**/*.json")):

        if task_count % report_interval == 0:
            print(f"{datetime.now().strftime(common.YMDHMS)} {task_count} files processed")
        
        if ban_pattern and re.search(ban_pattern, json_file_path.name): continue
        
        json_file = json.loads(json_file_path.read_text(encoding="utf-8-sig"))

        for data in json_file["data"]:

            for entity in data["Entities_list"]:

                result_file.add(entity)
        
        task_count += 1

    result_file = natsorted(result_file)

    result_file_path.write_text(
        json.dumps(result_file, ensure_ascii=False, indent=4),
        encoding="utf-8-sig"
    )

