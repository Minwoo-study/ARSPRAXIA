from pathlib import Path
from natsort import natsorted
from datetime import datetime
from tool import common
import json, re

CWD = Path.cwd()
SOURCE = CWD / 'source'
RESULT_STORAGE = CWD / 'result_storage'
MASSIVE_RESULT_STORAGE = CWD / 'result_storage'

DATAS = Path('/home/arspraxia/ner-training/dataset/')
TRAIN_JSONS = DATAS / 'train'
VALID_JSONS = DATAS / 'validation'
TEST_JSONS= DATAS / 'test'


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


from tool import json_to_csv

TASK = ["test", "validation", "train"]

h_folder = Path("/home/arspraxia/ner-training/dataset/")

for folder in h_folder.glob("*/"):
    
    if not folder.name in TASK:
        
        continue
    
    for small_folder in natsorted(folder.glob("*/")):
        
        if "_csv" in small_folder.name: continue
        
        target_folder = (folder / f"{small_folder.name}_csv")
        target_folder.mkdir(exist_ok=True)
        
        json_to_csv.main(
            small_folder,
            target_folder,
            result_file_prefix=f"{folder.name}_{small_folder.name}",
            result_file_start_num=1
        )

# sen_token_counter.main(
#     TRAIN_JSONS / '01.Lexis&Nexis',
#     TRAIN_JSONS / "train_01.Lexis&Nexs_statistic.json",
# )

# sen_token_counter.main(
#     ARTICLE_JSONS,
#     ARTICLE_JSONS / "entire_article_statistic.json",
# )


# sen_token_counter.main(
#     ARTICLE_JSONS,
#     ARTICLE_JSONS / "entire_article_statistic.json",
# )


# sen_token_counter.main(
#     ARTICLE_JSONS,
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