from __future__ import(absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys

import backtrader as bt

# ⭐ Cerebro라는 인스턴스를 생성한 후 run을 한 결과(getvalue는 예수금을 말하는 것 같음... 기본은 10000달러..?)
# if(__name__ == '__main__'):
#     cerebro = bt.Cerebro()

#     print('Starting Portfolio Value : %.2f' %cerebro.broker.getvalue())
#     cerebro.run()
#     print('Final Portfolio Value : %.2f' %cerebro.broker.getvalue())


# ⭐ 예제 2
# if __name__ == '__main__':
#     cerebro = bt.Cerebro()

#     # 파일 경로 설정(main함수 parameter)
#     modpath = os.path.dirname(os.path.abspath(sys.argv[0]))     # Home Directory라고 생각하면 됨
#     datapath = os.path.join(modpath, '../datas/orcl1995-2014.txt')

#     # 데이터 피드
#     data = bt.feeds.YahooFinanceCSVData(
#         dataname=datapath,
#         fromdate = datetime.datetime(2010, 1, 1),
#         todate = datetime.datetime(2023, 12, 31),
#         reverse = False
#     )

#     cerebro.adddata(data)

#     cerebro.broker.setcash(100000.0)

#     print('Starting Portfolio Value : %.2f' %cerebro.broker.getvalue())
#     cerebro.run()
#     print('Final Portfolio Value : %.2f' %cerebro.broker.getvalue())


# ⭐ 예제 3(전략 구현)
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        if(self.dataclose[0] < self.dataclose[-1]):
            # 당일종가 < 전일종가이면
            if(self.dataclose[-1] < self.dataclose[-2]):
                # 2일연속 종가가 하락하면 매수 신호 발생
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()


if (__name__ == '__main__'):
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    # raw dataset read
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/orcl1995-2014.txt')

    # 시작일 ~ 종료일 지정해서 데이터 추출
    data = bt.feeds.YahooFinanceCSVData(
        dataname = datapath,
        fromdate = datetime.datetime(2000, 1, 1),
        todate = datetime.datetime(2020, 12, 31),
        reverse = False
    )

    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value : %.2f' %cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value : %.2f' %cerebro.broker.getvalue())