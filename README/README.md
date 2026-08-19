# FORESIGHT – Retail Sales Forecasting & Demand Risk Analysis

## Project Overview

FORESIGHT is a retail sales forecasting and demand risk analysis project
developed using the M5 Retail Sales Forecasting Dataset.

The project analyzes historical retail sales data, identifies sales trends
and seasonal patterns, prepares the data through a reusable data pipeline,
builds machine learning forecasting models, performs demand risk analysis,
and presents the results through an interactive dashboard.

The project covers:

- Exploratory Data Analysis (EDA)
- Data Cleaning
- Data Pipeline Development
- Feature Engineering
- Sales Forecasting
- Model Evaluation
- Risk Analysis
- Dashboard Development

---

## Problem Statement

Retail businesses need accurate sales forecasts to make better decisions
about inventory management, stock planning, and resource allocation.

Variations in customer demand, seasonal patterns, and sales trends can make
future demand difficult to predict. Incorrect forecasts may result in
stockouts during high-demand periods or excess inventory during low-demand
periods.

FORESIGHT addresses this problem by analyzing historical retail sales data,
identifying important demand patterns, developing machine learning-based
forecasting models, and performing demand risk analysis.

---

## Objectives

- Analyze historical retail sales data from the M5 dataset.
- Perform exploratory data analysis to identify sales trends and patterns.
- Analyze category, store, monthly, and seasonal sales behavior.
- Develop a reusable data preprocessing and transformation pipeline.
- Engineer relevant time-based features for forecasting.
- Develop and evaluate machine learning forecasting models.
- Compare model performance using MAE, RMSE, and MAPE.
- Perform demand risk analysis.
- Generate future sales forecasts.
- Present forecasting results and business insights through an interactive
  Streamlit dashboard.

---

## Dataset

This project uses the **M5 Retail Sales Forecasting Dataset**.

The dataset contains historical retail sales information along with
calendar and product pricing information.

### Dataset Files

| File | Description |
|---|---|
| `calendar.csv` | Contains dates, weekdays, weeks, months, years, and event information. |
| `sales_train_validation.csv` | Contains historical daily sales for products across stores. |
| `sell_prices.csv` | Contains product selling price information for different stores and weeks. |

### Dataset Dimensions

| Dataset | Rows | Columns |
|---|---:|---:|
| Calendar | 1,969 | 13 |
| Sales Training | 30,490 | 1,918 |
| Sell Prices | 6,841,121 | 4 |

### Sales Data

The sales dataset contains daily sales columns represented as:

`d_1`, `d_2`, `d_3`, ..., `d_1913`

These daily sales values are transformed during the data pipeline into a
structured time-series format for analysis and forecasting.

---

## Project Structure

```text
Foresight 1/
│
├── dashboards/
│   └── app.py
│
├── data/
│   ├── Raw/
│   │   ├── calendar.csv
│   │   ├── sales_train_validation.csv
│   │   └── sell_prices.csv
│   │
│   └── Processed/
│
├── models/
│
├── notebook/
│   ├── 01_EDA.ipynb
│   ├── 02_Forecasting.ipynb
│   ├── final_sales_forecast.csv
│   ├── future_30_day_sales.csv
│   └── model_comparison.csv
│
├── outputs/
│
├── README/
│   └── README.md
│
└── src/
    ├── 01_Datapipeline.ipynb
    └── 02_Risk.ipynb
    ## Data Pipeline

The data pipeline prepares the raw M5 datasets for exploratory data analysis,
forecasting, and risk analysis.

### Pipeline Workflow

```text
Raw M5 Dataset
      ↓
Dataset Loading
      ↓
Data Quality Check
      ↓
Calendar Cleaning
      ↓
Sales Data Transformation
      ↓
Daily Sales Aggregation
      ↓
Calendar Integration
      ↓
Feature Engineering
      ↓
Processed Dataset
```

### Data Pipeline Steps

1. **Dataset Loading**
   - Load the M5 calendar, sales, and sell price datasets.

2. **Data Quality Check**
   - Check dataset dimensions.
   - Check missing values.
   - Check duplicate records.
   - Check data consistency.

3. **Calendar Cleaning**
   - Convert date information into the appropriate format.
   - Handle missing event information.

4. **Sales Data Transformation**
   - Identify the daily sales columns (`d_1` to `d_1913`).
   - Transform the sales data into a format suitable for time-series analysis.

5. **Daily Sales Aggregation**
   - Aggregate sales across products and stores for each day.
   - Create a daily sales time series.

6. **Calendar Integration**
   - Merge daily sales with calendar information.
   - Add date, weekday, week, month, year, and event information.

7. **Feature Engineering**
   - Create time-based forecasting features such as:
     - Year
     - Month
     - Week
     - Day of week
     - Day of month
     - Weekend indicator

The processed dataset is used as the input for EDA and forecasting.

---

## Exploratory Data Analysis (EDA)

Exploratory Data Analysis is performed to understand historical sales
behavior and identify important patterns before forecasting.

### EDA Analysis

The following analyses are performed:

1. **Dataset Structure**
   - Examine the number of rows, columns, and data types.

2. **Missing Values**
   - Identify missing values in the datasets.

3. **Duplicates**
   - Check for duplicate records.

4. **Sales Statistics**
   - Analyze descriptive statistics such as mean, median, minimum,
     maximum, and standard deviation.

5. **Zero/Negative Sales**
   - Identify zero and negative sales values.

6. **Overall Sales Trend**
   - Analyze daily sales trends over time.

7. **Category Analysis**
   - Compare sales behavior across product categories.

8. **Store Analysis**
   - Compare sales performance across different stores.

9. **Monthly Seasonality**
   - Analyze recurring monthly sales patterns.

10. **Average Sales by Month**
    - Compare average sales across different months.

The EDA findings help identify demand patterns and provide useful insights
for the forecasting stage.

---

## Forecasting

The forecasting stage uses machine learning techniques to predict future
retail sales.

### Forecasting Workflow

```text
Processed Dataset
       ↓
Feature Selection
       ↓
Train/Test Split
       ↓
Feature Encoding
       ↓
Model Training
       ↓
Prediction
       ↓
Model Evaluation
       ↓
Future Sales Forecast
```

### Forecasting Features

The forecasting process uses time-based features including:

- Year
- Month
- Week
- Day of week
- Day of month
- Weekend indicator

The dataset is divided into training and testing data while maintaining
chronological order to avoid using future information during training.

### Random Forest Regressor

A Random Forest Regressor is used for sales forecasting.

The model configuration includes:

```text
n_estimators = 100
max_depth = 15
min_samples_leaf = 2
random_state = 42
n_jobs = -1
```

### Model Evaluation

The forecasting model is evaluated using:

- **MAE (Mean Absolute Error)**
- **RMSE (Root Mean Squared Error)**
- **MAPE (Mean Absolute Percentage Error)**

Lower values indicate better forecasting performance.

The forecasting process also generates future sales predictions for business
analysis.

---

## Risk Analysis

Risk analysis is performed to identify potential demand-related risks using
historical sales and forecasting results.

The analysis considers:

- Demand variability
- High-demand periods
- Low-demand periods
- Demand fluctuations
- Potential stockout risk
- Potential excess inventory risk
- Unusual sales behavior

Risk analysis provides additional business insights beyond the numerical
sales forecast.

### Forecasting and Risk Connection

Forecasting helps answer:

> What could future demand look like?

Risk analysis helps answer:

> Where could future demand create potential business risk?

Together, forecasting and risk analysis provide a more complete view of
future retail demand.

---

## Dashboard

An interactive dashboard is developed using **Streamlit** to present the
results of the analysis, forecasting, and risk analysis.

### Dashboard Features

The dashboard provides:

- Historical sales trends
- Sales analysis
- Forecasted sales
- Future sales predictions
- Model performance
- Risk information
- Business insights

The dashboard provides an easy-to-understand interface for exploring the
project results without directly working with the underlying Python code.

---

## Technologies Used

### Programming Language

- Python

### Data Analysis

- Pandas
- NumPy

### Data Visualization

- Matplotlib
- Streamlit

### Machine Learning

- Scikit-learn

### Development Environment

- Visual Studio Code
- Jupyter Notebook

### Dataset

- M5 Retail Sales Forecasting Dataset

---

## Conclusion

FORESIGHT provides an end-to-end retail sales analytics and forecasting
solution using the M5 Retail Sales Forecasting Dataset.

The project combines data cleaning, data pipeline development, exploratory
data analysis, feature engineering, machine learning forecasting, model
evaluation, risk analysis, and dashboard visualization.

The forecasting component provides future sales estimates, while the risk
analysis identifies potential demand-related risks.

The interactive dashboard brings the results together and supports
data-driven retail decision-making.