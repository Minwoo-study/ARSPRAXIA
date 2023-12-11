import datetime

# int나 float를 datetime으로 변환
# 해당 값은 일 단위로 저장되어 있음 (엑셀의 날짜 값)
# 44488 -> 2021-10-19 가 되어야 함

value = 44488

calculated_time = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)
print(calculated_time)

# import numpy

# print(isinstance(numpy.float64, float))