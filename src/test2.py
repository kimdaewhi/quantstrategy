import datetime
import os
import sys
import pandas as pd
import FinanceDataReader as fdr


# main 함수
if __name__ == '__main__':
    # DataFrame
    kospi = fdr.StockListing('KOSPI')
    kosdaq = fdr.StockListing('KOSDAQ')

    kospi