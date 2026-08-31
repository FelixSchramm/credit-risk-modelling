# Credit Risk Modelling

This project demonstrates a full machine learning workflow for **predicting loan defaults** using the historical LendingClub dataset (2007–2018Q4). The goal is to identify loans that are at high risk of default ("Charged Off") in order to support risk-aware lending and investment decisions.

## Dataset  
The dataset consists of over **2.2 million loan records with 151 features**, including borrower information, loan characteristics, and repayment outcomes.  
- **Source:** LendingClub accepted loan data (2007–2018Q4)  
- **Target variable:** loan status, simplified to a binary outcome:  
  - `0` = Fully Paid  
  - `1` = Charged Off  

## Workflow  

### 1. Exploratory Data Analysis (EDA)  
- Distribution analysis (loan amounts, issuance per year, grades)  
- Correlation heatmaps of numerical features  

### 2. Data Cleaning & Preprocessing  
- Filtered to completed loans only (`Fully Paid`, `Charged Off`)  
- Removed irrelevant identifiers, text-based, and date-leakage features  
- Dropped columns with >40% missing values and rows with remaining nulls  
- Reduced dataset to ~418k clean samples and 95 features  

### 3. Feature Engineering  
- Converted `term` and `emp_length` into numerical values  
- One-hot encoded categorical variables  
- Standardized numerical features  
- Final dataset size: ~418k rows × 156 features  

### 4. Model Training  
- Stratified train-test split (70/30)  
- Applied **Random Forest Classifier** with `class_weight="balanced"`  
- Trained on ~293k samples, tested on ~125k  

### 5. Model Evaluation  
- **ROC AUC Score: 0.9999**  
- High precision and recall for both classes  
- Strong performance in identifying defaults, the main risk factor for investors  

## Key Findings  
- The Random Forest model demonstrates excellent discriminatory power between defaulted and fully paid loans.  
- High recall for the "Charged Off" class suggests the model is well-suited to flagging risky loans.  
- The workflow provides a robust baseline for credit risk prediction and can be extended with more advanced models (e.g., XGBoost, deep learning).  


## Folder Structure

```
Folder Structure/
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── 01_notebooks/
│   └── 1.0-eda-and-prototyping.ipynb
│
├── 02_data/
│   ├── raw/
│   │   └── lending_file_2015_2016.csv
│   └── processed/
│       └── cleaned_lending_data.csv
│
├── src/
│   ├── __init__.py
│   ├── data_processing.py
│   ├── features.py
│   ├── train.py
│   └── evaluate.py
│
└── 04_models/
    └── random_forest_v1.joblib
```
