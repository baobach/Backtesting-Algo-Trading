from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math

class PairsTradingStrategy(bt.Strategy):
    """
    PairsTradingStrategy is a strategy for pairs trading algorithmic trading.
    It uses a mean-reversion approach to identify trading opportunities between two correlated assets.
    The strategy checks conditions for entering short or long positions based on the z-score of the spread between the assets.
    It also implements position sizing based on the deviation from the simple moving averages (SMA) of the assets.
    """

    params = dict(
        period=20,
        stake=10,
        qty1=0,
        qty2=0,
        upper=2.5,
        lower=-2.5,
        up_medium=0.5,
        low_medium=-0.5,
        status=0,
        portfolio_value=100000,
        stop_loss=3.0
    )

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None

    def __init__(self):
        # To control operation entries
        self.orderid = None
        self.qty1 = self.p.qty1
        self.qty2 = self.p.qty2
        self.upper_limit = self.p.upper
        self.lower_limit = self.p.lower
        self.up_medium = self.p.up_medium
        self.low_medium = self.p.low_medium
        self.status = self.p.status
        self.portfolio_value = self.p.portfolio_value
        self.stop_loss = self.p.stop_loss

        self.sma1 = bt.indicators.SimpleMovingAverage(self.datas[0], period=50)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.datas[1], period=50)
        # Signals performed with PD.OLS :
        self.transform = btind.OLS_TransformationN(self.data0, self.data1, period=self.p.period)
        self.zscore = self.transform.zscore

    def next(self):
        x = 0
        y = 0
        if self.orderid:
            return  # if an order is active, no new orders are allowed

        # Step 2: Check conditions for SHORT & place the order
        # Checking the condition for SHORT
        if (self.zscore[0] > self.upper_limit) and (self.status != 1):
            # POSITION SIZING based off SMA
            deviationOffSMA1 = math.fabs((self.data0.close[0] / self.sma1[0]) - 1)
            deviationOffSMA2 = math.fabs((self.data1.close[0] / self.sma2[0]) - 1)
            value1 = 0.6 * self.portfolio_value  # Divide the cash equally
            value2 = 0.4 * self.portfolio_value
            if deviationOffSMA1 > deviationOffSMA2:
                x = int(value1 / self.data0.close[0])  # Find the number of shares for Stock1
                y = int(value2 / self.data1.close[0])  # Find the number of shares for Stock2
            else:
                x = int(value2 / self.data0.close[0])  # Find the number of shares for Stock1
                y = int(value1 / self.data1.close[0])  # Find the number of shares for Stock2

            # Placing the order
            self.sell(data=self.data0, size=(x + self.qty1))  # Place an order for buying x + qty1 shares
            self.buy(data=self.data1, size=(y + self.qty2))  # Place an order for selling y + qty2 shares

            # Updating the counters with new value
            self.qty1 = x  # The new open position quantity for Stock1 is x shares
            self.qty2 = y  # The new open position quantity for Stock2 is y shares

            self.status = 1  # The current status is "short the spread"

        # Step 3: Check conditions for LONG & place the order
        # Checking the condition for LONG
        elif (self.zscore[0] < self.lower_limit) and (self.status != 2):
            # POSITION SIZING based off SMA
            deviationOffSMA1 = math.fabs((self.data0.close[0] / self.sma1[0]) - 1)
            deviationOffSMA2 = math.fabs((self.data1.close[0] / self.sma2[0]) - 1)
            value1 = 0.6 * self.portfolio_value  # Divide the cash equally
            value2 = 0.4 * self.portfolio_value
            if deviationOffSMA1 > deviationOffSMA2:
                x = int(value1 / self.data0.close[0])  # Find the number of shares for Stock1
                y = int(value2 / self.data1.close[0])  # Find the number of shares for Stock2
            else:
                x = int(value2 / self.data0.close[0])  # Find the number of shares for Stock1
                y = int(value1 / self.data1.close[0])  # Find the number of shares for Stock2

            # Place the order
            self.buy(data=self.data0, size=(x + self.qty1))  # Place an order for buying x + qty1 shares
            self.sell(data=self.data1, size=(y + self.qty2))  # Place an order for selling y + qty2 shares

            # Updating the counters with new value
            self.qty1 = x  # The new open position quantity for Stock1 is x shares
            self.qty2 = y  # The new open position quantity for Stock2 is y shares
            self.status = 2  # The current status is "long the spread"

        # Step 4: Check conditions for No Trade
        # If the z-score is within the two bounds, close all
        elif ((self.zscore[0] < self.up_medium) and (self.zscore[0] > self.low_medium)):
            order1 = self.close(self.data0)
            order2 = self.close(self.data1)
            if order1 is not None:
                print('CLOSE POSITION %s, price = %.2f' % ("Visa", self.data0.close[0]))
            if order2 is not None:
                print('CLOSE POSITION %s, price = %.2f' % ("Mastercard", self.data1.close[0]))

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')


class SimpleMovingAverage(bt.Strategy):
    '''This is a long-only strategy which operates on a moving average cross

    Note:
      - Although the default

    Buy Logic:
      - No position is open on the data

      - The ``fast`` moving averagecrosses over the ``slow`` strategy to the
        upside.

    Sell Logic:
      - A position exists on the data

      - The ``fast`` moving average crosses over the ``slow`` strategy to the
        downside

    Order Execution Type:
      - Market

    '''
    params = (
        # period for the fast Moving Average
        ('fast', 5),
        # period for the slow moving average
        ('slow', 30),
        # moving average to use
        ('_movav', btind.MovAv.SMA)
    )
    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None    

    def __init__(self):
        sma_fast = self.p._movav(period=self.p.fast)
        sma_slow = self.p._movav(period=self.p.slow)

        self.buysig = btind.CrossOver(sma_fast, sma_slow)

    def next(self):
        if self.position.size:
            if self.buysig < 0:
                self.sell()

        elif self.buysig > 0:
            self.buy()

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

