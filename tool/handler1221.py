import json, re

from pathlib import Path
from tool import JSONformat_handler, common

def main(
    target_dir:Path,
    big_result_dir:Path,
    file_ban_pattern:str = r"statistic",
    folder_ban_pattern:str = r"final",
    report_interval:int = 100000
):

    big_result_dir.mkdir(exist_ok=True)

    # 혹시라도 잘못된 파일 이름이 있을 경우를 대비한 정규식
    file_ban = re.compile(file_ban_pattern)
    folder_ban = re.compile(folder_ban_pattern)

    task_count = 0

    for file in target_dir.glob('**/*.json'):
        if file_ban.search(str(file)): continue
        if folder_ban.search(file.parent.name): continue

        if task_count % report_interval == 0:
            common.print_log(f"task_count: {task_count}")
        
        RESULT_DIR = (big_result_dir / file.parent.name)
        RESULT_DIR.mkdir(exist_ok=True)

        # json 파일 읽기
        with open(file, 'r', encoding='utf-8-sig') as f:
            json_data = json.load(f)
        
        # json 파일 오류 대처
            
        # json 파일 컬럼 오류 대처
        # json_data = JSONformat_handler.handle_format_exceptions(json_data)
        
        # json 파일 데이터타입 오류 대처
        # json_data = JSONformat_handler.handle_dtype_exceptions(json_data)
            
        # json 파일 NER 태그 오류(Entities_list) 대처
        json_data = JSONformat_handler.handle_tag_exceptions(json_data)

        # json 파일 NER 태그 정보 오류 (Entities) 대처
        for idx, sentence_data in enumerate(json_data['data']):
            sentence_data['Entities'] = common.make_entity_data(sentence_data['Raw_data'], sentence_data['Entities_list'])
            sentence_data["NER_Count"] = len(sentence_data["Entities"])
            json_data['data'][idx] = sentence_data

        # json 파일 내용 오류 대처
        json_data = JSONformat_handler.handle_content_exceptions(json_data)

        if json_data is None:
            continue

        # json 파일 컬럼 순서 수정
        # json_data = JSONformat_handler.arrange_json_format(json_data)

        # json 파일 저장
        with open(RESULT_DIR / (json_data["Doc_ID"] + ".json"), 'w', encoding='utf-8-sig') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        task_count += 1