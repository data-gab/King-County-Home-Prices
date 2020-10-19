import pandas as pd
import numpy as np 
import statsmodels.api as sm
import scipy.stats as scs

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression

# Create a function to build a statsmodels ols model
def build_sm_ols(df, features_to_use, target, add_constant=False, show_summary=True):
    X = df[features_to_use]
    if add_constant:
        X = sm.add_constant(X)
    y = df[target]
    ols = sm.OLS(y, X).fit()
    if show_summary:
        print(ols.summary())
    return ols


# Check the validity of your model
# - Measure multicollinearity using vif of features
# - Test the normality of your residuals 
##  Ho: the variance is constant            
##  Ha: the variance is not constant


# assumptions of ols
# Check that residuals are normally distributed
def check_residuals_normal(ols):
    residuals = ols.resid
    t, p = scs.shapiro(residuals)
    if p <= 0.05:
        return False
    return True


# Check that residuals are equally spaced along the baseline (Homoscedasticity)
# Using the Breusch Pagan Test 
def check_residuals_homoskedasticity(ols):

    import statsmodels.stats.api as sms
    resid = ols.resid
    exog = ols.model.exog
    lg, p, f, fp = sms.het_breuschpagan(resid=resid, exog_het=exog)
    if p >= 0.05:
        return True
    return False



# Get the VIF score for use in multicollinearity check
def calculate_vif(df, features_to_use, target_feature):
    ols = build_sm_ols(df=df, features_to_use=features_to_use, target=target_feature, show_summary=False)
    r2 = ols.rsquared
    return 1 / (1 - r2)
    
    
    
# Check for multicollinearity in our feature space. 
def check_vif_feature_space(df, features_to_use, vif_threshold=3.0):
    all_good_vif = True
    for feature in features_to_use:
        target_feature = feature
        _features_to_use = [f for f in features_to_use if f!=target_feature]
        vif = calculate_vif(df=df, features_to_use=_features_to_use, target_feature=target_feature)
        if vif >= vif_threshold:
            print(f"{target_feature} surpassed threshold with vif={vif}")
            all_good_vif = False
    return all_good_vif


def check_model(df, 
                features_to_use, 
                target_col, 
                add_constant=False, 
                show_summary=False, 
                vif_threshold=3.0):
    has_multicollinearity = check_vif_feature_space(df=df, 
                                                    features_to_use=features_to_use, 
                                                    vif_threshold=vif_threshold)
    if not has_multicollinearity:
        print("Model contains multicollinear features")
    
    # build model 
    ols = build_sm_ols(df=df, features_to_use=features_to_use, 
                       target=target_col, add_constant=add_constant, 
                       show_summary=show_summary)
    
    # check residuals
    resids_are_norm = check_residuals_normal(ols)
    resids_are_homo = check_residuals_homoskedasticity(ols)
    
    if not resids_are_norm:
        print("Residuals failed normality test using Shaprio Test")
    if not resids_are_homo:
        print("Residuals failed homoskedasticity test using the Breusch Pagan Test")
    return ols



def normalize(feature):
    return (feature - feature.mean()) / feature.std()