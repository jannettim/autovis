from sklearn import datasets
import statsmodels.api as sm
import pandas as pd
from statsmodels.sandbox.regression.predstd import wls_prediction_std



def get_regression_line(X, y):

    # X = X.as_matrix()
    # y = y.as_matrix()

    X_cons = sm.add_constant(X)
    lm = sm.OLS(y, X_cons).fit()

    pred, upper, lower = wls_prediction_std(lm)

    return X, lm.fittedvalues, upper, lower