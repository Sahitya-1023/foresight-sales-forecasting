# ============================================================
# FORESIGHT - SALES FORECASTING DASHBOARD
# COMPLETE ENTRY CODE
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Foresight - Sales Forecasting",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "Raw"
NOTEBOOK_DIR = BASE_DIR / "notebook"

# ============================================================
# LOAD ALL DATA
# ============================================================

@st.cache_data
def load_data():

    # -------------------------
    # Raw datasets
    # -------------------------
    st.write("BASE_DIR:", BASE_DIR)
    st.write("DATA_DIR:", DATA_DIR)
    st.write("DATA EXISTS:", DATA_DIR.exists())
    st.write("FILES:", list(DATA_DIR.iterdir()) if DATA_DIR.exists() else "DATA FOLDER NOT FOUND")
    calendar = pd.read_csv(
        DATA_DIR / "calendar.csv"
    )

    sales = pd.read_csv(
        DATA_DIR / "sales_train_validation.csv"
    )

    prices = pd.read_csv(
        DATA_DIR / "sell_prices.csv"
    )

    # -------------------------
    # Forecasting results
    # -------------------------

    final_forecast = pd.read_csv(
        NOTEBOOK_DIR / "final_sales_forecast.csv"
    )

    future_forecast = pd.read_csv(
        NOTEBOOK_DIR / "future_30_day_sales_forecast.csv"
    )

    model_results = pd.read_csv(
        NOTEBOOK_DIR / "model_comparison_results.csv"
    )

    return (
        calendar,
        sales,
        prices,
        final_forecast,
        future_forecast,
        model_results
    )


# ============================================================
# LOAD DATA SAFELY
# ============================================================

try:

    (
        calendar,
        sales,
        prices,
        final_forecast,
        future_forecast,
        model_results
    ) = load_data()

    data_loaded = True

except Exception as e:

    data_loaded = False

    st.error("❌ Error loading project data")
    st.exception(e)



# ============================================================
# CREATE DAILY SALES DATA
# ============================================================

if data_loaded:

    try:

        # Get all daily sales columns from the sales dataset
        day_columns = [
            col for col in sales.columns
            if str(col).startswith("d_")
        ]

        # Calculate total sales for each day
        daily_totals = sales[day_columns].sum(axis=0)

        # Create daily sales dataframe
        daily_sales = pd.DataFrame({
            "d": daily_totals.index,
            "daily_sales": daily_totals.values
        })

        # ----------------------------------------------------
        # CONNECT SALES DAYS WITH CALENDAR BY POSITION
        # ----------------------------------------------------

        # The calendar does not contain a 'd' column.
        # The rows correspond to d_1, d_2, d_3, ...
        calendar_part = calendar.iloc[
            :len(daily_sales)
        ].copy()

        # Add calendar information by position
        daily_sales["date"] = pd.to_datetime(
            calendar_part["date"].values
        )

        # Add other calendar columns if available
        if "year" in calendar_part.columns:
            daily_sales["year"] = calendar_part["year"].values

        if "month" in calendar_part.columns:
            daily_sales["month"] = calendar_part["month"].values

        if "wday" in calendar_part.columns:
            daily_sales["wday"] = calendar_part["wday"].values

        if "weekday" in calendar_part.columns:
            daily_sales["weekday"] = calendar_part["weekday"].values

        # Make sure sales are numeric
        daily_sales["daily_sales"] = pd.to_numeric(
            daily_sales["daily_sales"],
            errors="coerce"
        )

        # Remove invalid values
        daily_sales = daily_sales.dropna(
            subset=["daily_sales"]
        )

    except Exception as e:

        st.error("❌ Error creating daily sales data")
        st.exception(e)

        daily_sales = pd.DataFrame()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(" FORESIGHT")

st.sidebar.markdown(
    """
    ### Sales Forecasting Dashboard

    **Project:**  
    Retail Sales Forecasting

    """
)

st.sidebar.markdown("---")

# ============================================================
# DASHBOARD PAGE SELECTION
# ============================================================

if data_loaded:

    pages = [
        "1️⃣ Executive Overview",
        "2️⃣ Sales Overview",
        "3️⃣ Sales Trend Analysis",
        "4️⃣ Store Performance",
        "5️⃣ Category Performance",
        "6️⃣ Time & Seasonality",
        "7️⃣ Sales Pattern Analysis",
        "8️⃣ Model Comparison",
        "9️⃣ Feature Importance",
        "🔟 Forecast Accuracy",
        "1️⃣1️⃣ 30-Day Future Forecast",
        "1️⃣2️⃣ Final Forecast & Insights"
    ]

    selected_page = st.sidebar.radio(
        "📑 Dashboard Pages",
        pages
    )

    st.sidebar.markdown("---")

    st.sidebar.info(
        "Foresight is a machine-learning-based "
        "retail sales forecasting dashboard."
    )

else:

    selected_page = "1️⃣ Executive Overview"


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if selected_page == "1️⃣ Executive Overview":

    st.title(" Foresight Sales Forecasting Dashboard")

    st.markdown(
        """
        ### Welcome to the Foresight Dashboard

        This dashboard provides interactive analysis of retail
        sales, historical trends, model performance and future
        sales predictions.
        """
    )

    st.markdown("---")

    if data_loaded:

        st.success(
            "✅ All project datasets loaded successfully!"
        )

        # ====================================================
        # KEY METRICS
        # ====================================================

        st.subheader(" Dataset Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Sales Records",
                f"{len(sales):,}"
            )

        with col2:
            if "store_id" in sales.columns:
                st.metric(
                    "Stores",
                    sales["store_id"].nunique()
                )
            else:
                st.metric("Stores", "N/A")

        with col3:
            if "cat_id" in sales.columns:
                st.metric(
                    "Categories",
                    sales["cat_id"].nunique()
                )
            else:
                st.metric("Categories", "N/A")

        with col4:
            st.metric(
                "Forecast Days",
                len(future_forecast)
            )

        st.markdown("---")

        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        st.subheader(" Loaded Project Data")

        dataset_info = pd.DataFrame({
            "Dataset": [
                "Calendar",
                "Sales Training",
                "Sell Prices",
                "Final Sales Forecast",
                "30-Day Future Forecast",
                "Model Comparison"
            ],

            "Rows": [
                len(calendar),
                len(sales),
                len(prices),
                len(final_forecast),
                len(future_forecast),
                len(model_results)
            ],

            "Columns": [
                len(calendar.columns),
                len(sales.columns),
                len(prices.columns),
                len(final_forecast.columns),
                len(future_forecast.columns),
                len(model_results.columns)
            ]
        })

        st.dataframe(
            dataset_info,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # ====================================================
        # PROJECT INFORMATION
        # ====================================================

        st.subheader(" Project Information")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                """
                **Objective**

                Develop a machine-learning-based retail sales
                forecasting system capable of analyzing
                historical sales patterns and generating
                future sales forecasts.
                """
            )

        with col2:

            st.markdown(
                """
                **Models Used**

                - Random Forest
                - Gradient Boosting
                - XGBoost

                The final model is selected based on forecasting
                performance using MAE and RMSE.
                """
            )

        st.markdown("---")

        # ====================================================
        # DAILY SALES CHART
        # ====================================================

        if not daily_sales.empty:

            st.subheader("📈 Historical Daily Sales")

            chart_data = daily_sales[
                ["date", "daily_sales"]
            ].copy()

            chart_data = chart_data.set_index("date")

            st.line_chart(
                chart_data,
                use_container_width=True
            )


# ============================================================
# SALES OVERVIEW
# ============================================================

elif selected_page == "2️⃣ Sales Overview":

    st.title(" Sales Overview")

    if not daily_sales.empty:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Sales",
                f"{daily_sales['daily_sales'].sum():,.0f}"
            )

        with col2:
            st.metric(
                "Average Daily Sales",
                f"{daily_sales['daily_sales'].mean():,.2f}"
            )

        with col3:
            st.metric(
                "Maximum Daily Sales",
                f"{daily_sales['daily_sales'].max():,.0f}"
            )

        st.markdown("---")

        st.subheader("Daily Sales")

        chart = daily_sales[
            ["date", "daily_sales"]
        ].set_index("date")

        st.line_chart(chart)

        st.subheader("Sales Statistics")

        st.dataframe(
            daily_sales["daily_sales"].describe(),
            use_container_width=True
        )


# ============================================================
# SALES TREND ANALYSIS
# ============================================================

elif selected_page == "3️⃣ Sales Trend Analysis":

    st.title(" Sales Trend Analysis")

    if not daily_sales.empty:

        trend = daily_sales.copy()

        trend["rolling_7"] = (
            trend["daily_sales"]
            .rolling(7)
            .mean()
        )

        trend["rolling_30"] = (
            trend["daily_sales"]
            .rolling(30)
            .mean()
        )

        chart = trend[
            ["date", "daily_sales",
             "rolling_7", "rolling_30"]
        ].set_index("date")

        st.line_chart(chart)


# ============================================================
# STORE PERFORMANCE
# ============================================================

elif selected_page == "4️⃣ Store Performance":

    st.title(" Store Performance")

    if "store_id" in sales.columns:

        store_columns = [
            col for col in sales.columns
            if col.startswith("d_")
        ]

        store_sales = sales.copy()

        store_sales["total_sales"] = (
            store_sales[store_columns]
            .sum(axis=1)
        )

        result = (
            store_sales
            .groupby("store_id")["total_sales"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            result.set_index("store_id")
        )


# ============================================================
# CATEGORY PERFORMANCE
# ============================================================

elif selected_page == "5️⃣ Category Performance":

    st.title(" Category Performance")

    if "cat_id" in sales.columns:

        day_columns = [
            col for col in sales.columns
            if col.startswith("d_")
        ]

        category_sales = sales.copy()

        category_sales["total_sales"] = (
            category_sales[day_columns]
            .sum(axis=1)
        )

        result = (
            category_sales
            .groupby("cat_id")["total_sales"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            result.set_index("cat_id")
        )


# ============================================================
# TIME & SEASONALITY
# ============================================================

elif selected_page == "6️⃣ Time & Seasonality":

    st.title(" Time & Seasonality")

    if not daily_sales.empty:

        temp = daily_sales.copy()

        if "date" in temp.columns:

            temp["day_of_week"] = (
                temp["date"].dt.day_name()
            )

            temp["month"] = (
                temp["date"].dt.month
            )

            st.subheader("Sales by Day of Week")

            weekday_sales = (
                temp
                .groupby("day_of_week")["daily_sales"]
                .mean()
            )

            st.bar_chart(weekday_sales)

            st.subheader("Sales by Month")

            monthly_sales = (
                temp
                .groupby("month")["daily_sales"]
                .mean()
            )

            st.bar_chart(monthly_sales)


# ============================================================
# SALES PATTERN ANALYSIS
# ============================================================

elif selected_page == "7️⃣ Sales Pattern Analysis":

    st.title(" Sales Pattern Analysis")

    if not daily_sales.empty:

        temp = daily_sales.copy()

        temp["lag_1"] = (
            temp["daily_sales"].shift(1)
        )

        temp["lag_7"] = (
            temp["daily_sales"].shift(7)
        )

        temp["rolling_mean_7"] = (
            temp["daily_sales"]
            .rolling(7)
            .mean()
        )

        st.dataframe(
            temp.tail(30),
            use_container_width=True
        )


# ============================================================
# MODEL COMPARISON
# ============================================================

elif selected_page == "8️⃣ Model Comparison":

    st.title(" Model Comparison")

    st.dataframe(
        model_results,
        use_container_width=True,
        hide_index=True
    )

    # Automatically identify numeric metric columns

    numeric_columns = model_results.select_dtypes(
        include=np.number
    ).columns.tolist()

    if numeric_columns:

        metric = st.selectbox(
            "Select metric",
            numeric_columns
        )

        st.bar_chart(
            model_results.set_index(
                model_results.columns[0]
            )[metric]
        )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

elif selected_page == "9️⃣ Feature Importance":

    st.title(" Feature Importance")

    st.info(
        "Feature importance is displayed when feature-importance "
        "results are available from the forecasting notebook."
    )

    st.write(
        "Available model result columns:"
    )

    st.write(
        model_results.columns.tolist()
    )


# ============================================================
# FORECAST ACCURACY
# ============================================================

elif selected_page == "🔟 Forecast Accuracy":

    st.title(" Forecast Accuracy")

    st.dataframe(
        model_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        ### Evaluation Metrics

        **MAE** – Mean Absolute Error

        **RMSE** – Root Mean Squared Error

        Lower values indicate better forecasting performance.
        """
    )


# ============================================================
# 30-DAY FUTURE FORECAST
# ============================================================

elif selected_page == "1️⃣1️⃣ 30-Day Future Forecast":

    st.title(" 30-Day Future Sales Forecast")

    st.dataframe(
        future_forecast,
        use_container_width=True,
        hide_index=True
    )

    # Automatically detect numeric forecast column

    numeric_columns = future_forecast.select_dtypes(
        include=np.number
    ).columns.tolist()

    if numeric_columns:

        forecast_column = st.selectbox(
            "Forecast Value",
            numeric_columns
        )

        st.line_chart(
            future_forecast[forecast_column]
        )


# ============================================================
# FINAL FORECAST & INSIGHTS
# ============================================================

elif selected_page == "1️⃣2️⃣ Final Forecast & Insights":

    st.title(" Final Forecast & Insights")

    st.subheader("Final Forecast")

    st.dataframe(
        final_forecast,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(" Key Insights")

    st.markdown(
        """
        - Historical sales patterns are analyzed using machine
          learning features.
        - Multiple forecasting models are compared.
        - MAE and RMSE are used for model evaluation.
        - Future sales are generated using the selected
          forecasting model.
        - The dashboard provides both historical analysis and
          future sales predictions.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Foresight | Retail Sales Forecasting Project"
)