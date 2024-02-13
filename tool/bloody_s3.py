"""
대규모 파일을 업로드하는 코드

파일 800만 개 업로드 강행하라고 한 놈 이름 알고 싶다
"""

import boto3, re
# Resource, Bucket 데이터타입 가져오기
from pathlib import Path
from tool.common import ConsoleLogger, read_json

with open("const/s3_keys.json", "r") as f:
    s3_keys = read_json(f)

class Mys3:

    AWS_ACCESS_KEY_ID = s3_keys["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = s3_keys["AWS_SECRET_ACCESS_KEY"]
    ENDPOINT_URL = s3_keys["ENDPOINT_URL"]
    REGION_NAME = s3_keys["REGION_NAME"]
    BUCKET_NAME = s3_keys["BUCKET_NAME"]

    def __init__(self):

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.__class__.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.__class__.AWS_SECRET_ACCESS_KEY,
            endpoint_url=self.__class__.ENDPOINT_URL,
            #region_name=self.__class__.REGION_NAME
        )
        self.bucket = self.s3_resource.Bucket(self.__class__.BUCKET_NAME)

        self._root_path:Path = None
        self._upload_path:str = None
        
        self.report_interval = 1000
        self._report_count = 0

    def _get_path(self, path:str|Path):
        return Path(path) if isinstance(path, str) else path
    
    @property
    def root_path(self):
        return self._root_path
    
    @root_path.setter
    def root_path(self, value:str|Path):
        self._root_path = self._get_path(value)
    
    @property
    def upload_path(self):
        return self._upload_path
    
    @upload_path.setter
    def upload_path(self, value:str):
        if "\\" in value: raise ValueError("구분자는 /로 해야 합니다.")
        self._upload_path = value

    def _make_upload_key(self, file_name:str):
        # 구분자가 \\가 아니라 /로 해야 함
        return f"{self._upload_path}/{file_name}"
    
    def upload_file(self, file_path:Path):
        with open(file_path, 'rb') as data:
            self.bucket.put_object(
                Key=self._make_upload_key(file_path.name), 
                Body=data
            )
        self._report_count += 1

    def upload_massive_files(
            self, 
            glob_pattern="*.csv", 
            ban_pattern=r"statistic"
        ):

        consolelogger = ConsoleLogger()

        path_glob = list(self._root_path.glob(glob_pattern))

        entire_file_count = len(path_glob)

        for file_path in path_glob:
            if re.search(ban_pattern, file_path.name): continue
            if self._report_count % self.report_interval == 0:
                consolelogger.print(f"현재 업로드 개수 : {self._report_count} / {entire_file_count}")
            self.upload_file(file_path)

    
