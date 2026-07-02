import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
import os

def run_markowitz():
    print("Loading NAV data for portfolio optimization...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nav_file = os.path.join(base_dir, "..", "data", "processed", "02_nav_history.csv")
    funds_file = os.path.join(base_dir, "..", "data", "processed", "01_fund_master.csv")
    
    nav = pd.read_csv(nav_file, parse_dates=['date'])
    funds = pd.read_csv(funds_file)
    
    # Select 5 top funds for portfolio
    target_amfis = [119551, 120503, 118632, 119092, 120841]
    
    # Pivot to get daily NAV for selected funds
    df = nav[nav['amfi_code'].isin(target_amfis)].pivot(index='date', columns='amfi_code', values='nav')
    df = df.dropna()
    
    # Calculate daily returns
    returns = df.pct_change().dropna()
    
    # Number of assets
    num_assets = len(returns.columns)
    
    # Calculate annualized mean returns and covariance matrix (252 trading days)
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Risk-free rate
    risk_free_rate = 0.065
    
    # Functions for optimization
    def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
        returns = np.sum(mean_returns * weights)
        std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return std, returns
        
    def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
        p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
        return - (p_ret - risk_free_rate) / p_var
        
    def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix, risk_free_rate)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bound = (0.0, 1.0)
        bounds = tuple(bound for asset in range(num_assets))
        
        result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                            method='SLSQP', bounds=bounds, constraints=constraints)
        return result
        
    def min_variance(mean_returns, cov_matrix):
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix)
        def portfolio_volatility(weights, mean_returns, cov_matrix):
            return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]
            
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bound = (0.0, 1.0)
        bounds = tuple(bound for asset in range(num_assets))
        
        result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args,
                            method='SLSQP', bounds=bounds, constraints=constraints)
        return result

    # 1. Maximum Sharpe Portfolio
    max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
    sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix)
    max_sharpe_allocation = pd.DataFrame(max_sharpe.x, index=df.columns, columns=['allocation'])
    max_sharpe_allocation.allocation = [round(i*100,2) for i in max_sharpe_allocation.allocation]
    max_sharpe_allocation = max_sharpe_allocation.T
    
    # Map AMFI code to Scheme Name
    amfi_to_name = dict(zip(funds['amfi_code'], funds['scheme_name']))
    max_sharpe_allocation.rename(columns=amfi_to_name, inplace=True)
    
    print("-" * 80)
    print("MAXIMUM SHARPE RATIO PORTFOLIO ALLOCATION (MARKOWITZ)")
    print("-" * 80)
    print(f"Annualised Return: {round(rp*100,2)}%")
    print(f"Annualised Volatility (Risk): {round(sdp*100,2)}%")
    print(f"Sharpe Ratio: {round((rp - risk_free_rate)/sdp, 2)}")
    print("\nOptimal Fund Weights:")
    for fund in max_sharpe_allocation.columns:
        print(f"{fund[:40]}: {max_sharpe_allocation[fund].values[0]}%")
    print("-" * 80)

if __name__ == "__main__":
    run_markowitz()
