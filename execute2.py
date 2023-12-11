from pathlib import Path
from natsort import natsorted
from datetime import datetime
from tool import common
import json, re

CWD = Path.cwd()
SOURCE = CWD / 'source'
RESULT_STORAGE = CWD / 'result_storage'
MASSIVE_RESULT_STORAGE = Path('../MassiveResultStorage')

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
# result_path = result_path = TWITTER_JSONS / "twitter_1205"

# # 통계를 만들지 않은 파일에 작업한다면, statistic = True 가 되어 있는지 확인 
# JSONconverter.main(source_path, result_path, statistic=True)

# sen_token_counter
from tool import sen_token_counter

sen_token_counter.main(
    ARTICLE_JSONS,
    ARTICLE_JSONS / "entire_article_statistic.json",
)

# entity_extractor
# from tool import entity_extractor

# entity_extractor.main(
#     ARTICLE_JSONS,
#     RESULT_STORAGE / "entity_extractor",
#     statistic=True,
#     report_interval=10000
# )