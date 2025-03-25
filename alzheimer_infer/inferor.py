import pandas as pd
import pickle
import xgboost as xgb
from catboost import CatBoostClassifier

# Load the saved medians (assuming this was saved during training)
with open('medians.pkl', 'rb') as f:
    medians = pickle.load(f)

# Load the feature names saved during training
with open('feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

# Load all models
xgb_model = xgb.XGBClassifier()
xgb_model.load_model('xgb_model.json')

cat_model = CatBoostClassifier()
cat_model.load_model('cat_model.cbm')

with open('gb_model.pkl', 'rb') as f:
    gb_model = pickle.load(f)

with open('mlp_model.pkl', 'rb') as f:
    mlp_model = pickle.load(f)

with open('voting_model.pkl', 'rb') as f:
    voting_model = pickle.load(f)

# Inference function
def predict(data_dict):
    """
    Input a dictionary of data and return predictions from each model.
    Parameters:
        data_dict: Input data dictionary with feature names and values
    Returns:
        dict: Predictions from each model
    """
    # Convert dictionary to DataFrame
    df = pd.DataFrame([data_dict])
    
    # Handle missing values using medians from training
    for col in medians.index:
        if col not in df.columns or pd.isnull(df[col]).any():
            df[col] = medians[col]
    
    # Reorder features to match training order
    df = df[feature_names]
    
    # Model predictions
    pred_xgb = xgb_model.predict(df)[0]
    pred_cat = cat_model.predict(df)[0]
    pred_gb = gb_model.predict(df)[0]
    pred_mlp = mlp_model.predict(df)[0]
    pred_voting = voting_model.predict(df)[0]
    
    # Return predictions as a dictionary
    return {
        "XGBoost": int(pred_xgb),
        "CatBoost": int(pred_cat),
        "Gradient Boosting": int(pred_gb),
        "MLP": int(pred_mlp),
        "Voting": int(pred_voting)
    }


# Example input data
input_data = {
    "Age": 75,
    "Gender": 0,
    "Ethnicity": 0,
    "EducationLevel": 2,
    "BMI": 22.5,
    "Smoking": 0,
    "AlcoholConsumption": 5,
    "PhysicalActivity": 3,
    "DietQuality": 7,
    "SleepQuality": 8,
    "FamilyHistoryAlzheimers": 0,
    "CardiovascularDisease": 0,
    "Diabetes": 0,
    "Depression": 0,
    "HeadInjury": 0,
    "Hypertension": 0,
    "SystolicBP": 120,
    "DiastolicBP": 80,
    "CholesterolTotal": 200,
    "CholesterolLDL": 120,
    "CholesterolHDL": 50,
    "CholesterolTriglycerides": 150,
    "MMSE": 25,
    "FunctionalAssessment": 5,
    "MemoryComplaints": 0,
    "BehavioralProblems": 0,
    "ADL": 10,
    "Confusion": 0,
    "Disorientation": 0,
    "PersonalityChanges": 0,
    "DifficultyCompletingTasks": 0,
    "Forgetfulness": 0
}
{
    "Age": 75,
    "Gender": 0,
    "Ethnicity": 0,
    "EducationLevel": 2,
    "BMI": 22.5,
    "Smoking": 0,
    "AlcoholConsumption": 5,
    "PhysicalActivity": 3,
    "DietQuality": 7,
    "SleepQuality": 8,
    "FamilyHistoryAlzheimers": 0,
    "CardiovascularDisease": 0,
    "Diabetes": 0,
    "Depression": 0,
    "HeadInjury": 0,
    "Hypertension": 0,
    "SystolicBP": 120,
    "DiastolicBP": 80,
    "CholesterolTotal": 200,
    "CholesterolLDL": 120,
    "CholesterolHDL": 50,
    "CholesterolTriglycerides": 150,
    "MMSE": 25,
    "FunctionalAssessment": 5,
    "MemoryComplaints": 0,
    "BehavioralProblems": 0,
    "ADL": 10,
    "Confusion": 0,
    "Disorientation": 0,
    "PersonalityChanges": 0,
    "DifficultyCompletingTasks": 0,
    "Forgetfulness": 0,
}

# Call the inference function
predictions = predict(input_data)
print("预测结果：", predictions)