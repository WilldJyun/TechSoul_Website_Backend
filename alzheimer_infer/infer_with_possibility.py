import pandas as pd
import pickle
import xgboost as xgb
from catboost import CatBoostClassifier

# Load the saved medians (assuming this was saved during training)
with open('alzheimer_infer/medians.pkl', 'rb') as f:
    medians = pickle.load(f)

# Load the feature names saved during training
with open('alzheimer_infer/feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

# Load all models
xgb_model = xgb.XGBClassifier()
xgb_model.load_model('alzheimer_infer/xgb_model.json')

cat_model = CatBoostClassifier()
cat_model.load_model('alzheimer_infer/cat_model.cbm')

with open('alzheimer_infer/gb_model.pkl', 'rb') as f:
    gb_model = pickle.load(f)

with open('alzheimer_infer/mlp_model.pkl', 'rb') as f:
    mlp_model = pickle.load(f)

with open('alzheimer_infer/voting_model.pkl', 'rb') as f:
    voting_model = pickle.load(f)

# Inference function
def predict_processing(data_dict):
    """
    Input a dictionary of data and return risk probabilities from each model.
    Parameters:
        data_dict: Input data dictionary with feature names and values
    Returns:
        dict: Risk probabilities from each model
    """
    # Convert dictionary to DataFrame
    df = pd.DataFrame([data_dict])
    
    # Handle missing values using medians from training
    for col in medians.index:
        if col not in df.columns or pd.isnull(df[col]).any():
            df[col] = medians[col]
    
    # Reorder features to match training order
    df = df[feature_names]
    
    # Model predictions (probability of class 1)
    prob_xgb = xgb_model.predict_proba(df)[0][1]  # P(class=1)
    prob_cat = cat_model.predict_proba(df)[0][1]  # P(class=1)
    prob_gb = gb_model.predict_proba(df)[0][1]    # P(class=1)
    prob_mlp = mlp_model.predict_proba(df)[0][1]  # P(class=1)
    prob_voting = voting_model.predict_proba(df)[0][1]  # P(class=1)
    
    # Return risk probabilities as a dictionary
    return {
        "XGBoost": prob_xgb,
        "CatBoost": prob_cat,
        "Gradient Boosting": prob_gb,
        "MLP": prob_mlp,
        "Voting": prob_voting
    }

def predict(input_data):
    predictions = predict_processing(input_data)
    print("预测风险值：", predictions)

    # 返回最终合并的预测值
    ans = predictions["Voting"]*100
    return int(ans)
