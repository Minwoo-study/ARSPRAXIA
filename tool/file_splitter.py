from pathlib import Path
from natsort import natsorted
from collections import OrderedDict
import numpy

def make_file_list(work_path:Path) -> list[Path]:
    # 중복되는 파일이 있을 경우, 가장 뒤에 있는 파일을 선택

    file_dict = {}
    for file in work_path.glob("**/*.*"):
        if file.is_file():
            file_dict[file.name] = file

    # 파일 딕셔너리를 key 기준으로 natural sort로 정렬하고, 딕셔너리의 value만 리스트로 변환
    file_dict = OrderedDict(natsorted(file_dict.items(), key=lambda x: x[0]))
    file_list = list(file_dict.values())
    return file_list

def move_files(target_path:Path, file_list:list[Path], *, unit:int=100000, folder_prefix:str="json"):
    """
    target_path 밑에 unit 개수만큼의 파일을 담을 폴더를 생성하고, 해당 폴더로 파일을 이동시킴\n
    이 작업은 file_list에 있는 모든 파일을 옮길 때까지 반복됨
    """
    # 대상 폴더명은 twitter_json_1, twitter_json_2, twitter_json_3, ...
    target_path.mkdir(exist_ok=True)
    for i in range(0, len(file_list), unit):
        folder_num = i//unit
        folder_name = folder_prefix + "_" + str(folder_num)

        target_folder = target_path / folder_name
        target_folder.mkdir(exist_ok=True)
        for file in file_list[i:i+unit]:
            file.rename(target_folder / file.name)

def split_files(target_path:Path, file_list:list[Path], *, divide_by:int=1, folder_prefix:str="json"):
    """
    source_path 밑에 있는 파일들을 target_path 밑에 unit 개수만큼의 파일을 담을 폴더를 생성하고, 해당 폴더로 파일을 이동시킴\n
    이 작업은 source_path 밑에 있는 모든 파일을 옮길 때까지 반복됨
    numpy.array_split 함수를 사용하여 파일을 분할함
    """
    
    # 대상 폴더명은 twitter_json_1, twitter_json_2, twitter_json_3, ...
    target_path.mkdir(exist_ok=True)

    for i, file_list in enumerate(numpy.array_split(file_list, divide_by)):
        folder_name = folder_prefix + "_" + str(i)

        target_folder = target_path / folder_name
        target_folder.mkdir(exist_ok=True)
        for file in file_list:
            file.rename(target_folder / file.name)
    
