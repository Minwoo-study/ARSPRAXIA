from pathlib import Path
from natsort import natsorted
from datetime import datetime
from tool import common
import json, re
from const.paths import *

# JSONconverter
from tool import JSONconverter

tasks = {
    # "기사" : (FINAL / "article_2"),
    "트위" : (FINAL / "twitter_1214"),
    # "위키" : (FINAL / "wiki_"),
}

source_path = SOURCE / "JSONconverter"
candidate_path = SOURCE / "JSONconverter_candidate"
done_path = SOURCE / "JSONconverter_done"

for keyword, result_path in tasks.items():
    
    # candidate_path에서 keyword를 포함한 xlsx 파일을 모두 가져온다.
    files = natsorted([file for file in candidate_path.glob("*.xlsx") if keyword in file.name])

    # 해당 파일들을 source_path로 옮긴다.
    for file in files:
        file.rename(source_path / file.name)

    # 통계를 만들지 않은 파일에 작업한다면, statistic = True 가 되어 있는지 확인 
    JSONconverter.main(source_path, result_path, statistic=True)

    # 작업이 끝난 파일들을 done_path로 옮긴다.
    for file in source_path.glob("*.xlsx"):
        file.rename(done_path / file.name)

# # sen_token_counter
# from tool import sen_token_counter

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