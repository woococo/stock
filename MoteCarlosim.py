#!/usr/bin/env python

import pandas as pd
import numpy as np

from base import BaseAlgo, TransformerMixin
from codec import codecs_manager
from util.param_util import convert_params


class MonteCarloSim(BaseAlgo):
    def __init__(self, options):
        feature_variables = options.get('feature_variables', {})
        target_variable = options.get('target_variable', {})

        if len(feature_variables) == 0:
            raise RuntimeError('You must spply one or more fields')

        if len(target_variable) > 0:
            raise RuntimeError('MonteCarloSim does not support the from clause')

        # Check to see if parameters exist
        params = options.get('params', {})

        # Check if method is in parameters in search
        if 'counter' in params:
            self.counter = int(params['counter'])
        else:
            self.counter = 5000

        # Check for bad parameters
        if len(params) > 1:
            raise RuntimeError('The only valid parameter is counter.')

    def fit(self, df, options):
        """ Compute the Monte Carlo Simulator """
        # df contains all the search results, including hidden fields
        # but the requested are saved as self.feature_variables
        input_df = df[self.feature_variables]
        input_df.sort_values(by=['date'])
        input_df.set_index('date', inplace=True)
        codes = input_df.columns
        days = input_df.shape[0]/len(codes) 

        daily_ret = input_df.pct_change()
        annual_ret = daily_ret.mean() * days
        daily_cov = daily_ret.cov()
        annual_cov = daily_cov * days

        port_ret = []
        port_risk = []
        port_weights = []

        for _ in range(self.counter): 
            weights = np.random.random(len(codes))
            weights /= np.sum(weights)

            returns = np.dot(weights, annual_ret)
            risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

            port_ret.append(returns)
            port_risk.append(risk)
            port_weights.append(weights)

        portfolio = { 'Returns' : port_ret, 'Risk': port_risk }
        for i, s in enumerate(codes):
            portfolio[s] = [weight[i] for weight in port_weights]
        output_df = pd.DataFrame(portfolio)
        output_df = output_df[['Returns', 'Risk'] + [s for s in codes]]
        return output_df