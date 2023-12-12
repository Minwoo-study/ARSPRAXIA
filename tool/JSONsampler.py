"""
json 가공 파일에서 토큰 기준으로 파일을 복사해 가져오는 모듈
ex) 1천만 토큰 -> 목표 디렉토리에서 1천만 토큰 분량의 json 가공 파일을 복사해 가져옴
- 총 작업 토큰이 1천만 토큰과 같거나, 그 이상이 되는 순간 작업을 종료
"""

from pathlib import Path
import json, shutil


def main(target_dir:Path, result_dir:Path, tokens:int=10000000, *, file_scale:int = 10000):
    """
    target_dir : json 가공 파일이 모여있는 폴더 위치\n
    """

    result_dir.mkdir(exist_ok=True)

    file_count = 0
    token_count = 0
    folder_count = -1
    current_dir = result_dir.joinpath(f"sample_{folder_count}")

    for json_file in target_dir.glob("**/*.json"):

        if token_count >= tokens:
            return f"files: {file_count}, tokens: {token_count} / {tokens}"
        
        with json_file.open("r", encoding="utf-8-sig") as f:
            f = json.load(f)

        for data in f["data"]:
            token_count += data["Word_Count"]
        
        # 1만 개 단위로 파일을 복사해 가져옴
        # 폴더 하나에 1만 개의 파일이 들어가도록 함
        # result_dir 내부에 폴더를 생성하고, 그 폴더에 파일을 저장함
        # 폴더 이름은 sample_0, sample_1, ... 순서대로 생성됨

        if file_count % file_scale == 0:
            folder_count += 1
            current_dir = result_dir.joinpath(f"sample_{folder_count}")
            current_dir.mkdir(exist_ok=True)
            
        shutil.copy(json_file, current_dir / json_file.name)
        file_count += 1


                
