import pandas as pd
import numpy as np

class MonteCarloSim():
    def __init__(self, numiter=5000):
        self.counter = numiter

    def fit(self, df):
        """ Compute the Monte Carlo Simulator """
        # df contains all the search results, including hidden fields
        # but the requested are saved as self.feature_variables
        df.sort_values(by=['date'])
        df.set_index('date', inplace=True)
        codes = df.columns
        days = df.shape[0] / len(codes)

        daily_ret = df.pct_change()
        annual_ret = daily_ret.mean() * days
        daily_cov = daily_ret.cov()
        annual_cov = daily_cov * days

        port_ret = []
        port_risk = []
        port_weights = []
        port_sharpe = []

        for _ in range(self.counter):
            weights = np.random.random(len(codes))
            weights /= np.sum(weights)

            returns = np.dot(weights, annual_ret)
            risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

            port_ret.append(returns)
            port_risk.append(risk)
            port_weights.append(weights)
            port_sharpe.append(returns/risk)

        portfolio = { 'Sharpe': port_sharpe, 'Returns' : port_ret, 'Risk': port_risk }
        for i, s in enumerate(codes):
            portfolio[s] = [weight[i] for weight in port_weights]
        output_df = pd.DataFrame(portfolio)
        output_df = output_df[['Sharpe', 'Returns', 'Risk'] + [s for s in codes]]
        return output_df