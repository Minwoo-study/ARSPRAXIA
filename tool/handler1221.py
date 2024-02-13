import json, re

from pathlib import Path
from tool import JSONformat_handler, common

def main(
    target_dir:Path,
    big_result_dir:Path,
    *,
    file_ban_pattern:str = r"statistic",
    folder_ban_pattern:str = r"final",
    report_interval:int = 100000,
    special_duplication_handle = False
):
    """

    Args:
        target_dir (Path): 검사하고자 하는 파일이 들어있는 디렉터리
        big_result_dir (Path): 결과 파일이 있을 디렉터리
        file_ban_pattern (str, optional): 패턴에 해당하는 파일은 제외. Defaults to r"statistic".
        folder_ban_pattern (str, optional): 패턴에 해당하는 폴더는 제외. Defaults to r"final".
        report_interval (int, optional): 몇 개 파일 단위로 콘솔에 진행 상황을 출력할 것인지. Defaults to 100000.
        special_duplication_handle (bool, optional): wiki류 데이터 오류 확인할 때만 True로 할 것. 워크스테이션 기준, 검사 속도가 2배로 느려짐. Defaults to False.
    """
    logger = common.ConsoleLogger()
    filename_container = dict()

    big_result_dir.mkdir(exist_ok=True)

    # 혹시라도 잘못된 파일 이름이 있을 경우를 대비한 정규식
    file_ban = re.compile(file_ban_pattern)
    folder_ban = re.compile(folder_ban_pattern)

    task_count = 0

    for file in target_dir.glob('**/*.json'):
        if file_ban.search(str(file)): continue
        if folder_ban.search(file.parent.name): continue

        if task_count % report_interval == 0:
            logger.print(f"task_count: {task_count}")
        
        RESULT_DIR = (big_result_dir / file.parent.name)
        RESULT_DIR.mkdir(exist_ok=True)

        # json 파일 읽기
        with open(file, 'r', encoding='utf-8-sig') as f:
            json_data = json.load(f)
        
        # json 파일 오류 대처
            
        # json 파일 컬럼 오류 대처
        # json 파일 데이터타입 오류 대처
        json_data = JSONformat_handler.handle_format_exceptions(json_data)
        json_data = JSONformat_handler.handle_dtype_exceptions(json_data)
            
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
        if special_duplication_handle:
            # wiki 류 파일에 대해 적용 : pub_subj를 일괄적으로 소문자화, id값 수정
            json_data["Pub_Subj"] = json_data["Pub_Subj"].lower()
            lower_docid:str = json_data["Doc_ID"].lower()
            if lower_docid not in filename_container:
                filename_container[lower_docid] = 1
            else:
                filename_container[lower_docid] += 1
            
            if filename_container[lower_docid] > 1:
                lower_docid_split = lower_docid.split("_")
                lower_docid = "_".join(lower_docid_split[:-2] + [str(filename_container[lower_docid]).zfill(7)])
            
            json_data["Doc_ID"] = lower_docid
            json_data = JSONformat_handler.handle_content_exceptions(json_data)
            
        with open(RESULT_DIR / (json_data["Doc_ID"] + ".json"), 'w', encoding='utf-8-sig') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        task_count += 1