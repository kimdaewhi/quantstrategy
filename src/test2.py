import datetime
import os
import sys
import pandas as pd
import FinanceDataReader as fdr
from tabulate import tabulate


# main 함수
if __name__ == '__main__':
    # DataFrame
    kospi = fdr.StockListing('KOSPI')
    kosdaq = fdr.StockListing('KOSDAQ')
    
    # 관리종목
    adm_stock = fdr.StockListing('KRX-ADMIN')

    # print(tabulate(kospi, headers='keys', tablefmt='fancy_outline'))
    print(tabulate(adm_stock, headers='keys', tablefmt='fancy_outline'))