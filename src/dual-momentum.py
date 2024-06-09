from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os
import sys
import pandas as pd
import backtrader as bt
import yfinance as yf

class DualMomentum(bt.Strategy):
    params = (
        ('rebalance_months', 3),
        ('num_stocks', 20),
        ('risk_free_asset', 'IRX'),  # Example ticker for 3-month T-bill
        ('momentum_periods', [3, 6, 9, 12]),
        ('commission', 0.001),
        ('stop_loss', -0.1),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = {d._name: d.close for d in self.datas}
        self.order = None
        self.last_rebalance = None
        self.holding_stocks = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        if self.order:
            return

        dt = self.datas[0].datetime.date(0)
        if self.last_rebalance is None or (dt - self.last_rebalance).days >= self.params.rebalance_months * 30:
            self.rebalance_portfolio()
            self.last_rebalance = dt

        for stock in self.holding_stocks:
            if stock.close[0] / stock.close[-1] - 1 <= self.params.stop_loss:
                self.order = self.close(data=stock)
                self.holding_stocks.remove(stock)

    def rebalance_portfolio(self):
        for stock in self.holding_stocks:
            self.order = self.close(data=stock)

        stock_momentums = []
        for d in self.datas:
            if d._name == self.params.risk_free_asset:
                continue

            momentum_scores = []
            for period in self.params.momentum_periods:
                ret = (d.close[0] - d.close[-int(period * 21)]) / d.close[-int(period * 21)]
                momentum_scores.append(ret)
            average_momentum = sum(momentum_scores) / len(momentum_scores)
            if average_momentum > 0:
                stock_momentums.append((average_momentum, d))

        stock_momentums.sort(reverse=True, key=lambda x: x[0])
        self.holding_stocks = [stock for _, stock in stock_momentums[:self.params.num_stocks]]

        for stock in self.holding_stocks:
            self.order = self.buy(data=stock)

    def stop(self):
        self.log('Ending Value %.2f' % self.broker.getvalue())


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DualMomentum)

    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB']  # Example tickers, replace with KOSPI/KOSDAQ tickers
    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for ticker in tickers:
        data = yf.download(ticker, start='2000-01-01', end='2020-12-31')
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
