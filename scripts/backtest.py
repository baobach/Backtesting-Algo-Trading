from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
sys.path.append("/Users/baobach/Backtesting-Algo-Trading")
import backtrader as bt
from src.strategy import PairsTradingStrategy
from src.analyzer import AnalyzerSuite
from src.data_manager import DataManager

if __name__ == '__main__':
    # ------------------------------------------------------------------------------------
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    data = DataManager()
    # Add a strategy
    ticker_1 = 'CSCO'
    ticker_2 = 'MSFT'
    cerebro.addstrategy(PairsTradingStrategy)
    data.cerebro_add_data(ticker1=ticker_1, ticker2=ticker_2, cerebro=cerebro)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # Set the commission
    #cerebro.broker.setcommission(commission=0.001)

    # ------------------------------------------------------------------------------------

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Analyzer
    AnalyzerSuite.defineAnalyzers(AnalyzerSuite,cerebro)
    # Run over everything
    thestrats = cerebro.run(stdstats=True)

    # -----------------------------------------------------------------------------------

    print(AnalyzerSuite.returnAnalyzers(AnalyzerSuite,thestrats))
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot()