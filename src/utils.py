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
        self.end_date = '2024-01-01'

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
        historical_data = obb.equity.price.historical(ticker, interval='1d', start_date=start_date, end_date=end_date, provider='yfinance').to_df()
        return historical_data

class TimeSeriesAnalysis:
    """
    A class for performing time series analysis.
    - estimate_long_run_short_run_relationships(y, x) to estimate the long-run and short-run cointegration relationships.
    - engle_granger_two_step_cointegration_test(y, x) to perform the two-step Engle & Granger test for cointegration.
    - adf_test(data) to perform the Augmented Dickey-Fuller test for cointegration.
    """
    
    @staticmethod
    def estimate_long_run_short_run_relationships(df1, df2):
        """
        Estimates the long-run and short-run cointegration relationship between two series, df1 and df2.
        
        Parameters:
            df1 (pd.Series): The first input series.
            df2 (pd.Series): The second input series.
        
        Returns:
            tuple: A tuple containing the estimated coefficients for the long-run relationship (c and gamma),
                   the estimated coefficient for the short-run relationship (alpha), and the residuals (z).
        """
        assert isinstance(df1, pd.Series), 'Input series df1 should be of type pd.Series'
        assert isinstance(df2, pd.Series), 'Input series df2 should be of type pd.Series'
        assert sum(df1.isnull()) == 0, 'Input series df1 has nan-values. Unhandled case.'
        assert sum(df2.isnull()) == 0, 'Input series df2 has nan-values. Unhandled case.'
        assert df1.index.equals(df2.index), 'The two input series df1 and df2 do not have the same index.'
        
        long_run_ols = OLS(df1, add_constant(df2), has_const=True)
        long_run_ols_fit = long_run_ols.fit()

        c, gamma = long_run_ols_fit.params
        z = long_run_ols_fit.resid

        short_run_ols = OLS(df1.diff().iloc[1:], (z.shift().iloc[1:]))
        short_run_ols_fit = short_run_ols.fit()

        alpha = short_run_ols_fit.params[0]

        return c, gamma, alpha, z

    @staticmethod
    def engle_granger_two_step_cointegration_test(df1, df2):
        """
        Applies the two-step Engle & Granger test for cointegration.
        
        This function performs the two-step Engle & Granger test for cointegration between two time series, df1 and df2.
        Cointegration is a statistical property that indicates a long-term relationship between two time series, 
        even if they are not directly correlated in the short term. The Engle & Granger test is a common method 
        used to test for cointegration.
        
        Parameters:
            df1 (pd.Series): The first input time series.
            df2 (pd.Series): The second input time series.
            
        Returns:
            Tuple: A tuple containing the Augmented Dickey-Fuller test statistic (adfstat) and the p-value (pvalue).
        """
        assert isinstance(df1, pd.Series), 'Input series df1 should be of type pd.Series'
        assert isinstance(df2, pd.Series), 'Input series df2 should be of type pd.Series'
        assert sum(df1.isnull()) == 0, 'Input series df1 has nan-values. Unhandled case.'
        assert sum(df2.isnull()) == 0, 'Input series df2 has nan-values. Unhandled case.'
        assert df1.index.equals(df2.index), 'The two input series df1 and df2 do not have the same index.'

        c, gamma, alpha, z = TimeSeriesAnalysis.estimate_long_run_short_run_relationships(df1, df2)

        adfstat, pvalue, usedlag, nobs, crit_values = adfuller(z, maxlag=1, autolag=None)

        return adfstat, pvalue
    
    @staticmethod
    def adf_test(df1, df2):
        """
        Applies the Augmented Dickey-Fuller test for cointegration.

        This function performs the Augmented Dickey-Fuller test for cointegration between two time series, df1 and df2.
        Cointegration is a statistical property that indicates a long-term relationship between two time series,
        even if they are not directly correlated in the short term. The Augmented Dickey-Fuller test is a common method
        used to test for cointegration.

        Parameters:
            df1 (pd.Series): The first input time series.
            df2 (pd.Series): The second input time series.

        Returns:
            Tuple: A tuple containing the Augmented Dickey-Fuller test statistic (adfstat) and the p-value (pvalue).
        """
        assert isinstance(df1, pd.Series), 'Input series df1 should be of type pd.Series'
        assert isinstance(df2, pd.Series), 'Input series df2 should be of type pd.Series'
        assert sum(df1.isnull()) == 0, 'Input series df1 has nan-values. Unhandled case.'
        assert sum(df2.isnull()) == 0, 'Input series df2 has nan-values. Unhandled case.'
        assert df1.index.equals(df2.index), 'The two input series df1 and df2 do not have the same index.'

        #store result of OLS regression on closing prices of fetched data
        df1 = df1.dropna()
        df2 = df2.dropna()
        result = stat.OLS(df1, df2).fit()
        #run the adfuller test by passing residuals of the regression as the input, store the result in computation
        computationResults = adfuller(result.resid)

        # print("Time series 1 vs Time series 2")
        # print ("Significance Level:", computationResults[0] )
        # print ("pValue is:", computationResults[1] )
        # print ("Critical Value Parameters", computationResults[4] )

        if computationResults[0] <= computationResults[4]['10%']  and computationResults[1]<= 0.05:
            print("Given Sig Level <= Critical Value @ 10%, and pValue <= 0.05")
            print ("Co-integrated")
            return True