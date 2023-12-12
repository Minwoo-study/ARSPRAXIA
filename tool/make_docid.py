from pathlib import Path
import pandas

file_path = Path("json_trans_20231024_원천데이터(트위터)_23_자동가공_done.xlsx")

df = pandas.read_excel(file_path)
df['Doc_ID'] = df['Sen_ID'].str.split('_sen').str[0]

# 파일명에 "_처리됨" 붙이고 저장
df.to_excel(file_path.stem.split('.')[0] + '_처리됨.xlsx', index=False)