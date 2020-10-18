import pandas as pd
import statsmodels.api as sm
import scipy.stats as scs


def build_sm_ols(df, features_to_use, target, add_constant=False, show_summary=True):
    X = df[features_to_use]
    if add_constant:
        X = sm.add_constant(X)
    y = df[target]
    ols = sm.OLS(y, X).fit()
    if show_summary:
        print(ols.summary())
    return ols

def check_residuals_normal(ols):
    residuals = ols.resid
    t, p = sps.shapiro(residuals)
    if p <= 0.05:
        return False
    return True
    
    
def check_resid_homosked(ols):
    resid = ols.resid
    exog = ols.model.exog
    lg, p, f, fp = sms.het_breuschpagan(resid=resid, exog_het=exog)
    if p >= 0.05:
        return True
    return False
    
def check_vif(df, features_to_use, target_feature):
    ols = build_sm_ols(df=df, features_to_use=features_to_use, target=target_feature, show_summary=False)
    r2 = ols.rsquared
    return 1 / (1 - r2)

    
def check_vif_feat_space(df, features_to_use, vif_threshold=3.0):
    all_good_vif = True
    for feature in features_to_use:
        target_feature = feature
        _features_to_use = [f for f in features_to_use if f!=target_feature]
        vif = check_vif(df=df,features_to_use=features_to_use, target_feature=target_feature)
        if vif >= vif_threshold:
            print(f'{target_feature} surpasses threshold with vif={vif}')
            all_good_vif = False
    return all_good_vif
   
        
        
def check_model(df,
                features_to_use, 
                target_col, 
                add_constant=False,
                show_summary=False,
                vif_threshold=3.0):
    has_multicoll = check_vif_feat_space(df=df,
                                         features_to_use=features_to_use,
                                         vif_threshold=vif_threshold)
    if not has_multicoll:
        print("Model contains multicollinearity features")
        return False
    
    #build model
    ols = build_sm_ols(df=df,
                       features_to_use=features_to_use,
                       target=target_col,
                       add_constant=add_constant,
                       show_summary=show_summary)
    
    #check residulas
    resids_are_norm = check_residuals_normal(ols)
    resids_are_homo = check_residuals_homoskedasticity(ols)
    
    if not resids_are_norm:
        print("Residuals failed normality test")
    if not resids_are_homo:
        print("Residuals failed homoskedasticity test")
    return ols



def normalize(feature):
    return (feature - feature.mean()) / feature.std()