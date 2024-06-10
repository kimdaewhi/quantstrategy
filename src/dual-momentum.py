from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os
import sys
import pandas as pd
import backtrader as bt
import yfinance as yf
import FinanceDataReader as fdr

class DualMomentum(bt.Strategy):
    params = (
        ('rebalance_months', 3),                # 리밸런싱 주기
        ('num_stocks', 20),                     # 포트폴리오 주식 수
        ('risk_free_asset', 'IRX'),             # 무위함 자산 Ticker(ex. 3개월 국채)
        ('momentum_periods', [3, 6, 9, 12]),    # 모멘텀 기간에 사용할 기간
        ('commission', 0.001),                  # 거래 수수료.(0.1%)
        ('stop_loss', -0.1),                    # 손절매 기준(-10%)
    )

    '''Log 출력'''
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    '''전략 초기화'''
    def __init__(self):
        self.dataclose = {d._name: d.close for d in self.datas}     # 데이터 종가 저장하는 dictionary
        self.order = None                                           # 현재 활성화된 주문
        self.last_rebalance = None                                  # 마지막 리밸런싱 일자
        self.holding_stocks = []                                    # 현재 보유중인 주식 목록

    '''주문 상태 알림'''
    def notify_order(self, order):
        # 주문 제출 or 접수 상태
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        # 주문 완료 상태일 때(매수 or 매도)
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        # 주문 취소 상태일 때
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    
    '''매일 호출되는 함수'''
    def next(self):
        # 현재 활성화 되어있는 주문이 있는 경우 리턴
        if self.order:
            return

        dt = self.datas[0].datetime.date(0)
        # 리밸런싱 주기가 지난 경우 포트폴리오 리밸런싱
        if self.last_rebalance is None or (dt - self.last_rebalance).days >= self.params.rebalance_months * 30:
            self.rebalance_portfolio()
            self.last_rebalance = dt

        # 보유중인 주식에 대해 손절 조건 확인, 조건 충족 시 매도
        for stock in self.holding_stocks:
            # 이부분은 바꿔야겠다... 매수평균단가 < -10% 일 때로
            if stock.close[0] / stock.close[-1] - 1 <= self.params.stop_loss:
                self.order = self.close(data=stock)
                self.holding_stocks.remove(stock)


    '''포트폴리오 리밸런싱'''
    def rebalance_portfolio(self):
        # 현재 보유중인 모든 주식 매도
        for stock in self.holding_stocks:
            self.order = self.close(data=stock)

        stock_momentums = []
        # 모든 주식에 대한 모멘텀을 계산함(무위험 자산은 제외)
        for d in self.datas:
            if d._name == self.params.risk_free_asset:
                continue

            momentum_scores = []
            for period in self.params.momentum_periods:
                ret = (d.close[0] - d.close[-int(period * 21)]) / d.close[-int(period * 21)]
                momentum_scores.append(ret)

            # 평균 계산
            average_momentum = sum(momentum_scores) / len(momentum_scores)
            if average_momentum > 0:
                stock_momentums.append((average_momentum, d))

        # 모멘텀 점수가 높은 순으로 정렬
        stock_momentums.sort(reverse=True, key=lambda x: x[0])
        self.holding_stocks = [stock for _, stock in stock_momentums[:self.params.num_stocks]]

        # 상위 n개 주식 매수
        for stock in self.holding_stocks:
            self.order = self.buy(data=stock)


    '''백테스트 종료 시 호출'''
    def stop(self):
        self.log('Ending Value %.2f' % self.broker.getvalue())


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.addstrategy(DualMomentum)
    cerebro.addstrategy(DualMomentum,
                    rebalance_months=3,
                    num_stocks=20,
                    risk_free_asset='IRX',
                    momentum_periods=[3, 6, 9, 12],
                    commission=0.001,
                    stop_loss=-0.1)

    # 여기서 종목 선정 해야함.
    # tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB']  # Example tickers, replace with KOSPI/KOSDAQ tickers
    data_dir = './data'

    # Directory 생성
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    kospi = fdr.StockListing('KOSPI')
    kosdaq = fdr.StockListing('KOSDAQ')


    for ticker in tickers:
        data = yf.download(ticker, start='2009-01-01', end='2019-12-31')
        data.to_csv(os.path.join(data_dir, f'{ticker}.csv'))


    for ticker in tickers:
        data_path = os.path.join(data_dir, f'{ticker}.csv')
        data = bt.feeds.YahooFinanceCSVData(
            dataname=data_path,
            fromdate=datetime.datetime(2000, 1, 1),
            todate=datetime.datetime(2020, 12, 31),
            reverse=False)
        cerebro.adddata(data, name=ticker)

    cerebro.broker.set_cash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
