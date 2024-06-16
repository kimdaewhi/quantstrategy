import datetime
import os
import sys
import pandas as pd
import FinanceDataReader as fdr
from tabulate import tabulate



def printCnt(df_krx, df_AdmStock, df_filterStk):
    print('상장종목 : ' + str(df_krx))
    print('관리종목 : ' + str(df_AdmStock))
    print('관리종목 제외 : ' + str(df_filterStk))

# main 함수
if __name__ == '__main__':
    # DataFrame
    df_kospi = fdr.StockListing('KOSPI')
    df_kosdaq = fdr.StockListing('KOSDAQ')
    
    # 관리종목
    df_AdmStock = fdr.StockListing('KRX-ADMIN')

    # ⭐ DataFrame 출력
    # print(tabulate(df_kospi.head(), headers='keys', tablefmt='fancy_outline'))
    # print(tabulate(df_AdmStock.head(), headers='keys', tablefmt='fancy_outline'))

    df_krx = pd.concat([df_kospi, df_kosdaq])

    # ⭐ Excel Export
    # df_krx.to_excel('stock_list.xlsx', index=False)
    # df_AdmStock.to_excel('adm_stock_list.xlsx', index=False)

    # 관리종목 제거
    df_filterStk = df_krx[~df_krx['Code'].isin(df_AdmStock['Symbol'])]

    # ⭐ DataFrame 행 개수 출력
    # printCnt(df_krx.spahe[0], df_AdmStock.shape[0], df_filterStk.shape[0])

    ticker = df_kospi['Code'].iloc[0]
    date = '2024-05-28'
    df_dateStock = fdr.DataReader(ticker, date, date)

    print(f"Data for {ticker} on {date}:")
    print(df_dateStock)




