# Module 2 — Titanic Analytics and Machine Learning

## Overview

This module performs exploratory data analysis, preprocessing, classification, class-imbalance analysis, hyperparameter tuning, regression, model evaluation, and model persistence using the Titanic dataset.

The Titanic dataset is loaded using Seaborn exactly once in `01_eda.ipynb` and immediately saved as `titanic.csv`. The saved CSV is then reused for subsequent analysis and modeling.

## Files

- `01_eda.ipynb` — Exploratory data analysis
- `02_modeling.ipynb` — Machine-learning workflow
- `titanic.csv` — Saved Titanic dataset
- `charts/` — Generated visualizations
- `models/best_pipeline.joblib` — Saved fitted classification pipeline

## Exploratory Data Analysis

The EDA notebook includes:

- Dataset shape and column inspection
- Descriptive statistics
- Missing-value percentages
- Missing-data treatment
- Age and fare histograms
- Age and fare boxplots
- IQR-based outlier analysis
- Fare mean, median, mode, and skewness
- Survival analysis by sex
- Survival analysis by passenger class
- Survival analysis by sex and passenger class
- Boolean masking using `&` and `|`
- Six-variable correlation matrix
- Correlation heatmap
- Multivariate visualizations
- Standardization of age and fare

## Missing-Value Strategy

Missing values were evaluated according to their percentage in each feature.

Columns with very low missingness were handled by removing the affected rows where appropriate. Age, which contains a moderate amount of missing data, was imputed using its median. The `deck` feature contains a very high proportion of missing values and was therefore removed during EDA.

During machine learning, missing-value handling is performed inside Scikit-learn preprocessing pipelines. Numerical variables use median imputation, while categorical variables use most-frequent imputation.

## Classification

The following classification models were trained:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The data was divided into training and testing sets using a stratified 80:20 split.

All preprocessing was fitted using the training data only to reduce data leakage.

### Classification Metrics

Models were evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix
- ROC Curve
- ROC-AUC

## Class Imbalance

Three strategies were compared:

1. Baseline Logistic Regression
2. Logistic Regression with `class_weight="balanced"`
3. Logistic Regression with SMOTE

SMOTE was applied only to the training data. The untouched test set was used for final evaluation.

Precision, recall, and F1-score were compared across the three strategies.

## Random Forest Hyperparameter Tuning

Random Forest was tuned using `GridSearchCV`.

The parameter grid included:

- `n_estimators`
- `max_depth`
- `max_features`

The Random Forest estimator was configured with `oob_score=True`, allowing an out-of-bag score to be reported for the selected estimator.

## Regression

A multivariate Linear Regression model was developed to predict passenger fare.

Predictor variables included:

- Passenger class
- Sex
- Age
- Number of siblings/spouses
- Number of parents/children
- Embarkation location

The regression model was evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R²
- Adjusted R²

A residual plot was generated to inspect residual behavior and possible heteroscedasticity.

## Model Persistence

The selected complete classification pipeline, including preprocessing and the estimator, is saved as:

`models/best_pipeline.joblib`

The model is reloaded using Joblib and tested using a raw passenger record to demonstrate that preprocessing and prediction work together after persistence.

## Running the Module

Run the notebooks in the following order:

1. `01_eda.ipynb`
2. `02_modeling.ipynb`

The first notebook creates `titanic.csv`, which is required by the second notebook.

Start Jupyter Notebook from the project environment:

```bash
jupyter notebook