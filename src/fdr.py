import datetime
import os
import sys
import pandas as pd
import FinanceDataReader as fdr
from tabulate import tabulate


# main 함수
if __name__ == '__main__':
    # DataFrame
    df_kospi = fdr.StockListing('KOSPI')
    df_kosdaq = fdr.StockListing('KOSDAQ')
    
    # 관리종목
    df_AdmStock = fdr.StockListing('KRX-ADMIN')

    df_krx = pd.concat([df_kospi, df_kosdaq])

    # ⭐ Excel Export
    # df_krx.to_excel('stock_list.xlsx', index=False)
    # df_AdmStock.to_excel('adm_stock_list.xlsx', index=False)

    # 관리종목 및 우선주 제거(5, 7, 9, K)
    df_filterStk = df_krx[~df_krx['Code'].isin(df_AdmStock['Symbol'])]
    df_filterStk = df_filterStk[~df_filterStk['Code'].str.endswith(('5', '7', '9', 'K'))]    

    initDate = '2019-01-01'
    bf_halfYear = (pd.to_datetime(initDate) - pd.DateOffset(months=6)).strftime('%Y-%m-%d')


    # # 6개월 전 종가와 기준일자를 추가하는 함수
    # def AddhaldYearPrice(row):
    #     code = row['Code']
    #     try:
    #         df_price = fdr.DataReader(code, bf_halfYear, initDate)

    #         if bf_halfYear in df_price.index:
    #             bf_halfYearPrice = df_price.loc[bf_halfYear]['Close']
    #         else:
    #             bf_halfYearPrice = df_price.iloc[0]['Close'] if not df_price.empty else None  # 가장 가까운 날짜의 종가
    #         return pd.Series([bf_halfYear, bf_halfYearPrice])
    #     except Exception as e:
    #         print(f"Error fetching data for {code}: {e}")
    #         return pd.Series([bf_halfYear, None])
        
    # df_filterStk[['6M_Ago_Date', '6M_Ago_Close']] = df_filterStk.apply(AddhaldYearPrice, axis=1)

    # df_filterStk.to_excel('filtered_stock_list_with_prices.xlsx', index=False)