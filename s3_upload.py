from pathlib import Path
from natsort import natsorted
from datetime import datetime
from tool import common
import json, re

CWD = Path.cwd()
SOURCE = CWD / 'source'
RESULT_STORAGE = CWD / 'result_storage'
MASSIVE_RESULT_STORAGE = CWD / 'result_storage'

DATAS = Path("../datas")
ARTICLE_JSONS = DATAS / 'article_jsons'
TWITTER_JSONS = DATAS / 'twitter_jsons'

FINAL = DATAS / 'final'
FINAL_ARTICLE = FINAL / 'article'
FINAL_TWITTER = FINAL / 'twitter'
FINAL_WIKI = FINAL / 'wiki'
FINAL_TERKINNI = FINAL / 'terkinni'
FINAL_KOREANA = FINAL / 'koreana'


# # JSONconverter
# from tool import JSONconverter
# source_path = SOURCE / "JSONconverter"
# result_path = result_path = MASSIVE_RESULT_STORAGE / "test"

# # 통계를 만들지 않은 파일에 작업한다면, statistic = True 가 되어 있는지 확인 
# JSONconverter.main(source_path, result_path, statistic=True)

# sen_token_counter
from tool import sen_token_counter

HD4 = Path("/home/arspraxia/Documents/Handled_Data4/")
S3 = Path("/home/arspraxia/ner-training/dataset/")

# TASK = ["article", "wiki", "terkinni"]

TASK = ["03.Extra", "02.Twitter", "02.Twitter_2"]

for task in TASK:
    
    sen_token_counter.main(
        S3 / task,
        S3 / f"{task}_statistic_0207.json"
    )

# result = {
#         "files":0,
#         "total_sentences": 0,
#         "total_tokens": 0
#     }

# filename_ban = re.compile(r"statistic")
# foldername_regex = re.compile(r"twitter")

# memory: set[str] = set()

# for folder in natsorted(HD4.glob("*/")):
    
#     if not folder.name in ["twitter", "twitter_2"]:
#         continue
        
#     for json_file in folder.glob("**/*.json"):

#         if filename_ban.search(json_file.name): continue

#         with open(json_file, "r", encoding="utf-8-sig") as f:
#             json_data = json.load(f)

#         result["files"] += 1

#         result["total_sentences"] += len(json_data["data"])

#         for data in json_data["data"]:
#             word_count = data["Word_Count"]
#             if isinstance(word_count, str):
#                 continue
#             result["total_tokens"] += int(word_count)
        
#         memory.add(json_file.name)

#         if result["files"] % 10000 == 0: print(f"{result['files']} files finished")
    
#     print(folder, result, sep="\t")

# print(result)
# print(f"unique files: {len(memory)}")

# with open(HD4 / "hd4_statistic.json", "w", encoding="utf-8") as f:
#     json.dump(result, f)

# with open(HD4 / "unique_twitter_files.json", "w", encoding="utf-8") as f:
#     json.dump(list(memory), f)

# sen_token_counter.main(
#     Path(),
#     ARTICLE_JSONS / "entire_article_statistic.json",
# )

# entity_extractor
# from tool import entity_extractor

# entity_extractor.main(
#     ARTICLE_JSONS,
#     RESULT_STORAGE / "entity_extractor",
#     statistic=True,
#     report_interval=10000
# )