from pathlib import Path
from tool import handler1221

source_path = Path("/home/arspraxia/Documents/Handled_Data4/wiki/")
result_path = Path("result_storage/wiki_handle_test/")

handler1221.main(
    source_path, result_path,
    report_interval=1000,
    special_duplication_handle=True
)