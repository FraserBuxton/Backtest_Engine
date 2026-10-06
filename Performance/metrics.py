import pandas as pd
import numpy as np

class PerformanceAnalyser:
    
    def __init__(self, results, initial_cash, ppy):
        
        if not isinstance(results, pd.DataFrame):
            raise TypeError('Results must be a DataFrame')
        
        if 'Equity' not in results.columns:
            raise ValueError('Results must have equity column')
        
        if not isinstance(initial_cash, (int, float)):
            raise TypeError('Initial cash must be a number')
        
        if initial_cash <= 0:
            raise ValueError('Initial cash must be strictly positive')
        
        if not isinstance(ppy, int):
            raise TypeError('Periods per Year must be an integer')
        
        if ppy <= 0:
            raise ValueError('Periods per year must be an integer')
        
        if results.empty:
            raise ValueError('Results cannot be empty')
        
        if results['Equity'].isna().any():
            raise ValueError('Equity cannot contain missing values')
        
        if (results['Equity'] <= 0).any():
            raise ValueError('Equity values must be strictly positive')
        
        self.results = results.copy()
        self.initial_cash = initial_cash
        self.ppy = ppy
        
    @property
    def equity(self):
        return self.results['Equity']
    
    @property
    def returns(self):
        return self.equity.pct_change().dropna()
    
    def total_return(self):
        return self.equity.iloc[-1] / self.initial_cash - 1
    
    def annualised_return(self):
        final_equity = self.equity.iloc[-1]
        
        if len(self.equity) < 2:
            return 0.0
        
        periods = len(self.equity) - 1
        
        return (final_equity / self.initial_cash) ** (self.ppy / periods) - 1
    
    def annualised_volatility(self):
        
        if len(self.returns) < 2:
            return 0.0
        
        return self.returns.std() * np.sqrt(self.ppy)
    
    def sharpe_ratio(self, rfr = 0.0):
        if not isinstance(rfr, (int, float)):
            raise TypeError('Risk free rate must be a number')
        
        if len(self.returns) < 2:
            return 0.0
        
        periodic_rfr = rfr / self.ppy
        
        excess = self.returns - periodic_rfr
        
        volatility = excess.std()
        
        return excess.mean() / volatility * np.sqrt(self.ppy)
        
    def cumulative_returns(self):
        
        return self.equity / self.initial_cash - 1
    
    def drawdowns(self):
        
        running_max = self.equity.cummax()
        
        return self.equity / running_max - 1
    
    def maximum_drawdown(self):
        
        return self.drawdowns().min()
    
    def calmar_ratio(self):
        
        max_drawdown = abs(self.maximum_drawdown())
        
        if max_drawdown == 0:
            return 0.0
        
        return self.annualised_return() / max_drawdown
    
    def summary(self):
        
        return {
            "Total Return": self.total_return(),
            "Annualised Return": self.annualised_return(),
            "Annualised Volatility": self.annualised_volatility(),
            "Sharpe Ratio": self.sharpe_ratio(),
            "Maximum Drawdown": self.maximum_drawdown(),
            "Calmar Ratio": self.calmar_ratio(),
        }