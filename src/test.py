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
# class TestStrategy(bt.Strategy):

#     def log(self, txt, dt=None):
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s, %s' % (dt.isoformat(), txt))

#     def __init__(self):
#         # 첫 번째 데이터 피드중 종가(Close)에 접근
#         self.dataclose = self.datas[0].close

#     # 새로운 데이터가 들어올 때마다 호출.
#     def next(self):
#         # 종가를 Log로 기록
#         self.log('Close, %.2f' % self.dataclose[0])
#         if(self.dataclose[0] < self.dataclose[-1]):
#             # 당일종가 < 전일종가이면
#             if(self.dataclose[-1] < self.dataclose[-2]):
#                 # 2일연속 종가가 하락하면 매수 신호 발생
#                 self.log('BUY CREATE, %.2f' % self.dataclose[0])
#                 self.buy()


# if (__name__ == '__main__'):
#     cerebro = bt.Cerebro()

#     cerebro.addstrategy(TestStrategy)

#     # raw dataset read
#     modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
#     datapath = os.path.join(modpath, '../datas/orcl1995-2014.txt')

#     # 시작일 ~ 종료일 지정해서 데이터 추출
#     data = bt.feeds.YahooFinanceCSVData(
#         dataname = datapath,
#         fromdate = datetime.datetime(2000, 1, 1),
#         todate = datetime.datetime(2020, 12, 31),
#         reverse = False
#     )

#     cerebro.adddata(data)
#     # 초기자본 설정
#     cerebro.broker.setcash(100000.0)

#     print('Starting Portfolio Value : %.2f' %cerebro.broker.getvalue())
#     cerebro.run()
#     print('Final Portfolio Value : %.2f' %cerebro.broker.getvalue())


# ⭐예제 4
class TestStrategy(bt.Strategy):

    # log 기록
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))


    # 초기화
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        self.order = None
        self.buyprice = None
        self.buycomm = None


    def notify_order(self, order):
        if(order.status in [order.Submitted, order.Accepted]):
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        
        # 주문이 완려되었는지 여부 체크
        # 주의 : 예수금이 충분히 존재하지 않으면 오더를 거부한다.
        if (order.status in [order.Completed]):
            if(order.isbuy()):
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            elif(order.issell()):
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
            
            self.bar_executed = len(self)

        elif(order.status in [order.Calceled, order.Margin, order.Rejected]):
            self.log('Order Canceled/Margin/Rejected')

        # 보류중인 주문 x
        self.order = None

    
    def notify_trade(self, trade):
        if (not trade.isclosed):
            return
        
        self.log('OPERATION PROFIT, GROSS: %.2f, NET: %.2f' % (trade.pnl, trade.pnlcomm))


    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # 보류중인 주문 있으면 return
        if(self.order):
            return
        
        # 포지션이 없을 때 매수 신호 발생
        if(not self.position):
            if(self.dataclose[0] < self.dataclose[-1]):
                if(self.dataclose[-1] < self.dataclose[-2]):
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()
        # 포지션이 있을 때 매도 신호 발생
        else: 
            # 포지션을 가지고 있는 기간이 5일 이상이면 매도
            if(len(self) >= (self.bar_executed) + 5):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/orcl1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2000, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())