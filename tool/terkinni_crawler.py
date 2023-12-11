"""
## 설정
target_file : 2023.xlsx
target_sheets : JANUARI, FEBRUARI, AGUSTUS

reference_file : "Terkinni양식 3.xlsx"
result_file : 2023_result.xlsx

## 작업방식
1. target_file의 target_sheet들과 result_file을 pandas.read_excel로 읽어온다. target_file의 시트들에 for 문을 걸어 순회한다.
2. target_sheet의 "Date of Release" 컬럼의 날짜 데이터를 변수에 저장해둔다.
3. target_sheet의 "Terkinni" 컬럼에 있는 데이터가 유효한 url인지 re로 확인한다. (단순히 https://로 시작하는지만 확인해도 된다)
4. 유효한 url이면 해당 url로 요청을 보내서 html을 받아온다.
5. 받아온 html을 BeautifulSoup으로 파싱한다.
    1. a class="tdb-author-name"의 value를 변수에 저장한다. 이것이 기사를 쓴 사람의 이름이다. (엑셀에는 애칭으로 나와 있다.)
    2. css 셀렉터 div h1으로 기사 제목을 가져와 변수에 저장한다. h1 태그의 클래스는 tdb-title-text이다.
    3. div class="tdb-block-inner td-fix-index"를 찾고, 해당 태그 밑에 존재하는 p 태그의 내용을 가져와 리스트 변수에 append하여 저장한다. (즉, p 태크가 여러 개 있어서 for 문을 걸어야 한다는 것이다.) 이것이 기사의 내용이다.
    4. 엑셀의 date_of_release에 오류가 있어서, time 태그의 class = "entry-date updated td-module-date"의 value를 가져와서 변수에 저장한다. 이것이 기사가 쓰여진 날짜이다.
6. result_file의 "Date" 컬럼에 날짜 데이터를, "Author" 컬럼에 기사를 쓴 사람 이름 데이터를, "Headline" 컬럼에 기사 제목을, "Article" 컬럼에 기사 내용을 입력한다. 기사 내용은 "\n".join()으로 입력한다.
7. result_file을 to_excel로 export한다.
"""

import requests
from bs4 import BeautifulSoup
import re

from pathlib import Path

from datetime import datetime

import pandas

# url을 받아 html을 반환하는 함수
def get_html(url:str) -> str:
    """
    url을 받아 html을 반환하는 함수\n
    status_code가 200이 아니면 빈 문자열을 반환한다.
    """
    response = requests.get(url)
    return response.text if response.status_code == 200 else ""

def string_to_datestring(date:str) -> str:
    """
    날짜를 받아서 yyyy-mm-dd 형식의 문자열로 반환하는 함수\n
    날짜는 인도네시아어며, 다음과 같은 형식이다.\n
    January 2, 2023
    """
    if date == "": return ""
    date = date.replace("Januari", "January")
    date = date.replace("Februari", "February")
    date = date.replace("Maret", "March")
    date = date.replace("Mei", "May")
    date = date.replace("Juni", "June")
    date = date.replace("Juli", "July")
    date = date.replace("Agustus", "August")
    date = date.replace("Oktober", "October")
    date = date.replace("Desember", "December")
    return datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")

def get_text_from_html(soup:BeautifulSoup, css_selector:str) -> str:
    """
    BeautifulSoup 객체와 css_selector를 받아서 텍스트를 반환하는 함수\n
    css_selector로 찾은 태그가 없으면 빈 문자열을 반환한다.
    """
    selected_tag = soup.select_one(css_selector)
    return selected_tag.text if selected_tag else ""

def main(df_dict:dict[str, pandas.DataFrame], result_df_format:pandas.DataFrame, result_dir:Path):
    task_count = 0
    for sheet_name, df in df_dict.items():

        result_df = result_df_format.copy()

        for row_num in range(len(df)):

            # Artikel Bu Rini 등의 시트는 따로 처리한다.
            if "Link" in df.columns:
                url = df.loc[row_num, "Link"]
            else:
                url = df.loc[row_num, "Terkinni"]
            date_of_release = ""
            author = ""
            headline = ""
            article_components = []

            # url 정보가 NaN이면 해당 행을 건너뛴다.
            if pandas.isna(url): continue

            if re.match(r"https://", url) and "terkinni.com" in url:
                html = get_html(url)
                soup = BeautifulSoup(html, "html.parser")
                date_of_release = get_text_from_html(soup, "div.tdb-block-inner.td-fix-index time.entry-date.updated.td-module-date")
                author = get_text_from_html(soup, "a.tdb-author-name")
                headline = get_text_from_html(soup, "div h1.tdb-title-text")
                article_components = [p.text for p in soup.select("div.tdb-block-inner.td-fix-index p")]
            else: continue

            result_df.loc[task_count, "Date"] = string_to_datestring(date_of_release)
            result_df.loc[task_count, "Author"] = author
            result_df.loc[task_count, "Headline"] = headline
            result_df.loc[task_count, "Article"] = "\n".join(article_components).replace("TERKINNI.COM – ", "")
            task_count += 1

        result_df.to_excel(result_dir / (sheet_name + ".xlsx"), index=False)

if __name__ == "__main__":
    target_file = Path("2022.xlsx")
    result_dir = Path("result_2022")
    result_dir.mkdir(exist_ok=True)
    reference_file = Path("Terkinni양식 3.xlsx")
    result_file = Path(f"{target_file.stem}_result.xlsx")
    # 
    target_sheets = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER", "Artikel Bu Rini", "HAi"]

    result_df_format:pandas.DataFrame = pandas.read_excel(reference_file)
    # result_df 파일의 1행을 삭제한다.
    result_df_format = result_df_format.drop(0)

    df_dict:dict[str, pandas.DataFrame] = {}
    for sheet in target_sheets:
        df_dict[sheet] = pandas.read_excel(target_file, sheet_name=sheet)
    main(df_dict, result_df_format, result_dir)