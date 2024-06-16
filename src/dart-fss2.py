import dart_fss as dart
from tabulate import tabulate

# Open DART API KEY 설정
api_key = 'd00cc7609f43e2b2e6b560e039442fe3751dbde7'
dart.set_api_key(api_key=api_key)

# DART 에 공시된 회사 리스트 불러오기
corp_list = dart.get_corp_list()
corp_code = '005930'

# 삼성전자 검색
samsung = corp_list.find_by_stock_code(corp_code)

# 2024년 사업보고서 불러오기
report = samsung.extract_fs(report_tp='annual', bgn_de='20240101', end_de='20241231')

# 손익계산서 추출
income_statement = report['is']

# 당기순이익 계정과목 추출
# income_statement.to_excel('005930_is.xlsx')               # 엑셀 Export
print(income_statement.columns.values.tolist())

# print(income_statement.loc[income_statement['label_ko'])net_income = income_statement.loc[income_statement['label_ko'].str.contains('당기순이익', na=False)]]
# print(net_income)