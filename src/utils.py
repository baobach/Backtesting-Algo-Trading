import pandas as pd
from openbb import obb
from statsmodels.api import OLS, add_constant
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as stat
from src.config import get_api_key


class DataWrangler:
    """
    A class for downloading historical data for a given ticker.
    """

    def __init__(self):
        self.pat = get_api_key()
        obb.account.login(pat=self.pat)
        self.start_date = '2020-01-01'
        self.end_date = '2023-01-01'

    def download_data(self, ticker, start_date, end_date):
        """
        Downloads historical data for the given ticker.

        Parameters:
        - ticker (str): The ticker symbol of the stock.
        - start_date (str): The start date of the historical data in the format 'YYYY-MM-DD'.
        - end_date (str): The end date of the historical data in the format 'YYYY-MM-DD'.

        Returns:
        - historical_data (pandas.DataFrame): The historical data for the given ticker.
        """
        historical_data = obb.equity.price.historical(ticker, interval='1d', start_date=start_date, end_date=end_date).to_df()
        return historical_data

class TimeSeriesAnalysis:
    
    @staticmethod
    def estimate_long_run_short_run_relationships(y, x):
        """
        Estimates the long-run and short-run cointegration relationship between two series, y and x.
        
        Parameters:
            y (pd.Series): The first input series.
            x (pd.Series): The second input series.
        
        Returns:
            tuple: A tuple containing the estimated coefficients for the long-run relationship (c and gamma),
                   the estimated coefficient for the short-run relationship (alpha), and the residuals (z).
        """
        assert isinstance(y, pd.Series), 'Input series y should be of type pd.Series'
        assert isinstance(x, pd.Series), 'Input series x should be of type pd.Series'
        assert sum(y.isnull()) == 0, 'Input series y has nan-values. Unhandled case.'
        assert sum(x.isnull()) == 0, 'Input series x has nan-values. Unhandled case.'
        assert y.index.equals(x.index), 'The two input series y and x do not have the same index.'
        
        long_run_ols = OLS(y, add_constant(x), has_const=True)
        long_run_ols_fit = long_run_ols.fit()

        c, gamma = long_run_ols_fit.params
        z = long_run_ols_fit.resid

        short_run_ols = OLS(y.diff().iloc[1:], (z.shift().iloc[1:]))
        short_run_ols_fit = short_run_ols.fit()

        alpha = short_run_ols_fit.params[0]

        return c, gamma, alpha, z

    @staticmethod
    def engle_granger_two_step_cointegration_test(y, x):
        """
        Applies the two-step Engle & Granger test for cointegration.
        
        This function performs the two-step Engle & Granger test for cointegration between two time series, y and x.
        Cointegration is a statistical property that indicates a long-term relationship between two time series, 
        even if they are not directly correlated in the short term. The Engle & Granger test is a common method 
        used to test for cointegration.
        
        Parameters:
            y (pd.Series): The first input time series.
            x (pd.Series): The second input time series.
            
        Returns:
            Tuple: A tuple containing the Augmented Dickey-Fuller test statistic (adfstat) and the p-value (pvalue).
        """
        assert isinstance(y, pd.Series), 'Input series y should be of type pd.Series'
        assert isinstance(x, pd.Series), 'Input series x should be of type pd.Series'
        assert sum(y.isnull()) == 0, 'Input series y has nan-values. Unhandled case.'
        assert sum(x.isnull()) == 0, 'Input series x has nan-values. Unhandled case.'
        assert y.index.equals(x.index), 'The two input series y and x do not have the same index.'

        c, gamma, alpha, z = TimeSeriesAnalysis.estimate_long_run_short_run_relationships(y, x)

        adfstat, pvalue, usedlag, nobs, crit_values = adfuller(z, maxlag=1, autolag=None)

        return adfstat, pvalue
    
    def adf_test(data):
        #store result of OLS regression on closing prices of fetched data
        data = data.dropna()
        result = stat.OLS(data[0], data[1]).fit()
        #run the adfuller test by passing residuals of the regression as the input, store the result in computation
        computationResults = adfuller(result.resid)

        print(f"{data[0].name} vs {data[1].name}")
        print ("Significance Level:", computationResults[0] )
        print ("pValue is:", computationResults[1] )
        print ("Critical Value Parameters", computationResults[4] )

        if computationResults[0] <= computationResults[4]['10%']  and computationResults[1]<= 0.05:
            print("Given Sig Level <= Critical Value @ 10%, and pValue <= 0.05")
            print ("Co-integrated")