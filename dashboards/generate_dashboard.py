# ============================================================
# FORESIGHT - HTML DASHBOARD GENERATOR
# ============================================================
# This script creates dashboard.html using the SAME actual
# project data used by the Streamlit dashboard.
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np
import json
import html


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "Raw"
NOTEBOOK_DIR = BASE_DIR / "notebook"
DASHBOARD_DIR = BASE_DIR / "dashboards"

OUTPUT_FILE = DASHBOARD_DIR / "dashboard.html"


# ============================================================
# 2. LOAD PROJECT DATA
# ============================================================

print("=" * 60)
print("FORESIGHT HTML DASHBOARD GENERATOR")
print("=" * 60)

print("\nLoading project data...")


calendar = pd.read_csv(
    DATA_DIR / "calendar.csv"
)

sales = pd.read_csv(
    DATA_DIR / "sales_train_validation.csv"
)

prices = pd.read_csv(
    DATA_DIR / "sell_prices.csv"
)

final_forecast = pd.read_csv(
    NOTEBOOK_DIR / "final_sales_forecast.csv"
)

future_forecast = pd.read_csv(
    NOTEBOOK_DIR / "future_30_day_sales_forecast.csv"
)

model_results = pd.read_csv(
    NOTEBOOK_DIR / "model_comparison_results.csv"
)


print("Calendar:", calendar.shape)
print("Sales:", sales.shape)
print("Sell Prices:", prices.shape)
print("Final Forecast:", final_forecast.shape)
print("Future Forecast:", future_forecast.shape)
print("Model Results:", model_results.shape)


# ============================================================
# 3. CREATE DAILY SALES
# ============================================================

print("\nCreating daily sales...")


day_columns = [
    col for col in sales.columns
    if str(col).startswith("d_")
]


daily_totals = sales[day_columns].sum(axis=0)


daily_sales = pd.DataFrame({
    "d": daily_totals.index,
    "daily_sales": daily_totals.values
})


# Calendar corresponds positionally to d_1, d_2, etc.

calendar_part = calendar.iloc[
    :len(daily_sales)
].copy()


daily_sales["date"] = pd.to_datetime(
    calendar_part["date"].values
)


if "year" in calendar_part.columns:
    daily_sales["year"] = calendar_part["year"].values

if "month" in calendar_part.columns:
    daily_sales["month"] = calendar_part["month"].values

if "wday" in calendar_part.columns:
    daily_sales["wday"] = calendar_part["wday"].values

if "weekday" in calendar_part.columns:
    daily_sales["weekday"] = calendar_part["weekday"].values


daily_sales["daily_sales"] = pd.to_numeric(
    daily_sales["daily_sales"],
    errors="coerce"
)

daily_sales = daily_sales.dropna(
    subset=["daily_sales"]
)


print("Daily sales created:", daily_sales.shape)


# ============================================================
# 4. PREPARE DATA FOR JAVASCRIPT
# ============================================================

def records_to_json(df):
    """
    Convert dataframe into JSON-safe records.
    """
    temp = df.copy()

    for col in temp.columns:

        if pd.api.types.is_datetime64_any_dtype(
            temp[col]
        ):
            temp[col] = temp[col].dt.strftime(
                "%Y-%m-%d"
            )

    temp = temp.replace(
        [np.inf, -np.inf],
        np.nan
    )

    temp = temp.where(
        pd.notna(temp),
        None
    )

    return temp.to_dict(
        orient="records"
    )


# ============================================================
# 5. EXECUTIVE OVERVIEW DATA
# ============================================================

sales_records = len(sales)

stores_count = (
    sales["store_id"].nunique()
    if "store_id" in sales.columns
    else None
)

categories_count = (
    sales["cat_id"].nunique()
    if "cat_id" in sales.columns
    else None
)

forecast_days = len(
    future_forecast
)


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


# ============================================================
# 6. SALES OVERVIEW DATA
# ============================================================

total_sales = daily_sales[
    "daily_sales"
].sum()

average_daily_sales = daily_sales[
    "daily_sales"
].mean()

maximum_daily_sales = daily_sales[
    "daily_sales"
].max()


sales_statistics = (
    daily_sales["daily_sales"]
    .describe()
    .reset_index()
)

sales_statistics.columns = [
    "Statistic",
    "Value"
]


# ============================================================
# 7. SALES TREND DATA
# ============================================================

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


# ============================================================
# 8. STORE PERFORMANCE
# ============================================================

if "store_id" in sales.columns:

    store_sales = sales.copy()

    store_sales["total_sales"] = (
        store_sales[day_columns]
        .sum(axis=1)
    )

    store_result = (
        store_sales
        .groupby("store_id")["total_sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

else:

    store_result = pd.DataFrame()


# ============================================================
# 9. CATEGORY PERFORMANCE
# ============================================================

if "cat_id" in sales.columns:

    category_sales = sales.copy()

    category_sales["total_sales"] = (
        category_sales[day_columns]
        .sum(axis=1)
    )

    category_result = (
        category_sales
        .groupby("cat_id")["total_sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

else:

    category_result = pd.DataFrame()


# ============================================================
# 10. TIME & SEASONALITY
# ============================================================

seasonality = daily_sales.copy()

seasonality["day_of_week"] = (
    seasonality["date"]
    .dt.day_name()
)

seasonality["month_number"] = (
    seasonality["date"]
    .dt.month
)


weekday_sales = (
    seasonality
    .groupby("day_of_week")[
        "daily_sales"
    ]
    .mean()
)


# Keep natural Monday-Sunday order

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_sales = weekday_sales.reindex(
    weekday_order
)


monthly_sales = (
    seasonality
    .groupby("month_number")[
        "daily_sales"
    ]
    .mean()
)


# ============================================================
# 11. SALES PATTERN ANALYSIS
# ============================================================

pattern_data = daily_sales.copy()

pattern_data["lag_1"] = (
    pattern_data["daily_sales"]
    .shift(1)
)

pattern_data["lag_7"] = (
    pattern_data["daily_sales"]
    .shift(7)
)

pattern_data["rolling_mean_7"] = (
    pattern_data["daily_sales"]
    .rolling(7)
    .mean()
)

pattern_tail = pattern_data.tail(
    30
).copy()


# ============================================================
# 12. MODEL COMPARISON
# ============================================================

numeric_model_columns = (
    model_results
    .select_dtypes(
        include=np.number
    )
    .columns
    .tolist()
)


if len(numeric_model_columns) > 0:

    default_metric = (
        "RMSE"
        if "RMSE" in numeric_model_columns
        else numeric_model_columns[0]
    )

else:

    default_metric = None


# ============================================================
# 13. CONVERT DATA TO JSON
# ============================================================

daily_json = records_to_json(
    daily_sales[
        ["date", "daily_sales"]
    ]
)

trend_json = records_to_json(
    trend[
        [
            "date",
            "daily_sales",
            "rolling_7",
            "rolling_30"
        ]
    ]
)

store_json = records_to_json(
    store_result
)

category_json = records_to_json(
    category_result
)

weekday_json = [
    {
        "name": str(index),
        "value": (
            None
            if pd.isna(value)
            else float(value)
        )
    }
    for index, value in weekday_sales.items()
]

monthly_json = [
    {
        "name": str(index),
        "value": (
            None
            if pd.isna(value)
            else float(value)
        )
    }
    for index, value in monthly_sales.items()
]


pattern_json = records_to_json(
    pattern_tail
)

model_json = records_to_json(
    model_results
)

final_forecast_json = records_to_json(
    final_forecast
)

future_forecast_json = records_to_json(
    future_forecast
)

dataset_json = records_to_json(
    dataset_info
)

statistics_json = records_to_json(
    sales_statistics
)


# ============================================================
# 14. HTML HELPER FUNCTIONS
# ============================================================

def js_json(data):
    return json.dumps(
        data,
        ensure_ascii=False
    )


def create_table(records):
    """
    Create an HTML table from records.
    """

    if not records:
        return "<p>No data available.</p>"

    columns = list(
        records[0].keys()
    )

    header = "".join(
        f"<th>{html.escape(str(col))}</th>"
        for col in columns
    )

    rows = []

    for row in records:

        cells = []

        for col in columns:

            value = row.get(col)

            if value is None:
                value = ""

            elif isinstance(
                value,
                float
            ):
                value = (
                    f"{value:,.2f}"
                )

            cells.append(
                f"<td>{html.escape(str(value))}</td>"
            )

        rows.append(
            "<tr>"
            + "".join(cells)
            + "</tr>"
        )

    return f"""
    <div class="table-container">
        <table>
            <thead>
                <tr>{header}</tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """


# ============================================================
# 15. HTML PAGE
# ============================================================

html_content = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
               initial-scale=1.0">

<title>
Foresight - Sales Forecasting Dashboard
</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #f5f7fb;

    color:
        #1f2937;
}}

.sidebar {{
    position: fixed;
    left: 0;
    top: 0;

    width: 270px;
    height: 100vh;

    background:
        #111827;

    color: white;

    padding: 25px 15px;

    overflow-y: auto;
}}

.logo {{
    font-size: 27px;
    font-weight: bold;

    margin-bottom: 5px;
}}

.subtitle {{
    color: #cbd5e1;
    font-size: 14px;

    margin-bottom: 25px;
}}

.nav-button {{
    width: 100%;

    border: none;

    background:
        transparent;

    color: #d1d5db;

    padding: 11px 10px;

    margin: 3px 0;

    border-radius: 7px;

    text-align: left;

    cursor: pointer;

    font-size: 14px;
}}

.nav-button:hover {{
    background:
        #374151;

    color: white;
}}

.nav-button.active {{
    background:
        #2563eb;

    color: white;
}}

.main {{
    margin-left: 270px;

    padding: 35px;

    min-height: 100vh;
}}

.page {{
    display: none;
}}

.page.active {{
    display: block;
}}

h1 {{
    margin-top: 0;

    font-size: 32px;
}}

h2 {{
    margin-top: 30px;
}}

.card-grid {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(200px, 1fr)
        );

    gap: 18px;

    margin: 20px 0;
}}

.card {{
    background: white;

    padding: 22px;

    border-radius: 12px;

    box-shadow:
        0 2px 10px
        rgba(0,0,0,0.06);
}}

.card-title {{
    color: #64748b;

    font-size: 14px;

    margin-bottom: 8px;
}}

.card-value {{
    font-size: 27px;

    font-weight: bold;
}}

.section {{
    background: white;

    padding: 25px;

    border-radius: 12px;

    margin-top: 20px;

    box-shadow:
        0 2px 10px
        rgba(0,0,0,0.05);
}}

.success {{
    background: #dcfce7;

    color: #166534;

    padding: 15px;

    border-radius: 8px;

    margin: 20px 0;
}}

.info {{
    background: #dbeafe;

    color: #1e40af;

    padding: 15px;

    border-radius: 8px;

    margin: 20px 0;
}}

.chart-box {{
    position: relative;

    height: 430px;

    width: 100%;
}}

.small-chart {{
    height: 350px;
}}

.table-container {{
    overflow-x: auto;

    max-height: 600px;
}}

table {{
    border-collapse: collapse;

    width: 100%;

    background: white;
}}

th {{
    background: #f1f5f9;

    padding: 11px;

    text-align: left;

    position: sticky;

    top: 0;

    z-index: 1;
}}

td {{
    padding: 9px 11px;

    border-bottom:
        1px solid #e5e7eb;
}}

tr:hover {{
    background: #f8fafc;
}}

select {{
    padding: 10px;

    border-radius: 7px;

    border: 1px solid #cbd5e1;

    margin: 10px 0;

    min-width: 180px;
}}

.insights li {{
    margin: 10px 0;
}}

.footer {{
    margin-top: 40px;

    text-align: center;

    color: #64748b;

    padding: 20px;
}}

@media(max-width: 800px) {{

    .sidebar {{
        position: relative;

        width: 100%;

        height: auto;
    }}

    .main {{
        margin-left: 0;

        padding: 20px;
    }}

}}

</style>

</head>


<body>


<!-- =====================================================
     SIDEBAR
===================================================== -->

<div class="sidebar">

    <div class="logo">
        FORESIGHT
    </div>

    <div class="subtitle">
        Sales Forecasting Dashboard
        <br>
        Retail Sales Forecasting
    </div>

    <hr>

    <button class="nav-button active"
            onclick="showPage('page1', this)">
        1️⃣ Executive Overview
    </button>

    <button class="nav-button"
            onclick="showPage('page2', this)">
        2️⃣ Sales Overview
    </button>

    <button class="nav-button"
            onclick="showPage('page3', this)">
        3️⃣ Sales Trend Analysis
    </button>

    <button class="nav-button"
            onclick="showPage('page4', this)">
        4️⃣ Store Performance
    </button>

    <button class="nav-button"
            onclick="showPage('page5', this)">
        5️⃣ Category Performance
    </button>

    <button class="nav-button"
            onclick="showPage('page6', this)">
        6️⃣ Time & Seasonality
    </button>

    <button class="nav-button"
            onclick="showPage('page7', this)">
        7️⃣ Sales Pattern Analysis
    </button>

    <button class="nav-button"
            onclick="showPage('page8', this)">
        8️⃣ Model Comparison
    </button>

    <button class="nav-button"
            onclick="showPage('page9', this)">
        9️⃣ Feature Importance
    </button>

    <button class="nav-button"
            onclick="showPage('page10', this)">
        🔟 Forecast Accuracy
    </button>

    <button class="nav-button"
            onclick="showPage('page11', this)">
        1️⃣1️⃣ 30-Day Future Forecast
    </button>

    <button class="nav-button"
            onclick="showPage('page12', this)">
        1️⃣2️⃣ Final Forecast & Insights
    </button>

    <hr>

    <p style="font-size:13px;color:#9ca3af;">
        Foresight is a machine-learning-based
        retail sales forecasting dashboard.
    </p>

</div>


<!-- =====================================================
     MAIN CONTENT
===================================================== -->

<div class="main">


<!-- =====================================================
     PAGE 1 - EXECUTIVE OVERVIEW
===================================================== -->

<div id="page1" class="page active">

<h1>
Foresight Sales Forecasting Dashboard
</h1>

<p>
<b>Welcome to the Foresight Dashboard</b>
</p>

<p>
This dashboard provides interactive analysis of retail
sales, historical trends, model performance and future
sales predictions.
</p>

<div class="success">
✅ All project datasets loaded successfully!
</div>

<h2>Dataset Summary</h2>

<div class="card-grid">

<div class="card">
<div class="card-title">
Sales Records
</div>

<div class="card-value">
{sales_records:,}
</div>
</div>


<div class="card">
<div class="card-title">
Stores
</div>

<div class="card-value">
{stores_count if stores_count is not None else "N/A"}
</div>
</div>


<div class="card">
<div class="card-title">
Categories
</div>

<div class="card-value">
{categories_count if categories_count is not None else "N/A"}
</div>
</div>


<div class="card">
<div class="card-title">
Forecast Days
</div>

<div class="card-value">
{forecast_days}
</div>
</div>

</div>


<div class="section">

<h2>Loaded Project Data</h2>

{create_table(dataset_json)}

</div>


<div class="section">

<h2>Project Information</h2>

<div class="card-grid">

<div class="card">

<h3>Objective</h3>

<p>
Develop a machine-learning-based retail sales
forecasting system capable of analyzing historical
sales patterns and generating future sales forecasts.
</p>

</div>


<div class="card">

<h3>Models Used</h3>

<ul>
<li>Random Forest</li>
<li>Gradient Boosting</li>
<li>XGBoost</li>
</ul>

<p>
The final model is selected based on forecasting
performance using MAE and RMSE.
</p>

</div>

</div>

</div>


<div class="section">

<h2>📈 Historical Daily Sales</h2>

<div class="chart-box">

<canvas id="dailySalesChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 2 - SALES OVERVIEW
===================================================== -->

<div id="page2" class="page">

<h1>Sales Overview</h1>

<div class="card-grid">

<div class="card">

<div class="card-title">
Total Sales
</div>

<div class="card-value">
{total_sales:,.0f}
</div>

</div>


<div class="card">

<div class="card-title">
Average Daily Sales
</div>

<div class="card-value">
{average_daily_sales:,.2f}
</div>

</div>


<div class="card">

<div class="card-title">
Maximum Daily Sales
</div>

<div class="card-value">
{maximum_daily_sales:,.0f}
</div>

</div>

</div>


<div class="section">

<h2>Daily Sales</h2>

<div class="chart-box">

<canvas id="salesOverviewChart"></canvas>

</div>

</div>


<div class="section">

<h2>Sales Statistics</h2>

{create_table(statistics_json)}

</div>

</div>


<!-- =====================================================
     PAGE 3 - SALES TREND
===================================================== -->

<div id="page3" class="page">

<h1>Sales Trend Analysis</h1>

<div class="section">

<h2>Daily Sales with Rolling Averages</h2>

<div class="chart-box">

<canvas id="trendChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 4 - STORE PERFORMANCE
===================================================== -->

<div id="page4" class="page">

<h1>Store Performance</h1>

<div class="section">

<h2>Store Sales</h2>

{create_table(store_json)}

<div class="chart-box">

<canvas id="storeChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 5 - CATEGORY PERFORMANCE
===================================================== -->

<div id="page5" class="page">

<h1>Category Performance</h1>

<div class="section">

<h2>Category Sales</h2>

{create_table(category_json)}

<div class="chart-box">

<canvas id="categoryChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 6 - TIME & SEASONALITY
===================================================== -->

<div id="page6" class="page">

<h1>Time & Seasonality</h1>

<div class="section">

<h2>Sales by Day of Week</h2>

<div class="chart-box small-chart">

<canvas id="weekdayChart"></canvas>

</div>

</div>


<div class="section">

<h2>Sales by Month</h2>

<div class="chart-box small-chart">

<canvas id="monthChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 7 - SALES PATTERN
===================================================== -->

<div id="page7" class="page">

<h1>Sales Pattern Analysis</h1>

<div class="info">

This section shows the last 30 observations together
with lag-1 sales, lag-7 sales and the 7-day rolling mean.

</div>

<div class="section">

{create_table(pattern_json)}

</div>

</div>


<!-- =====================================================
     PAGE 8 - MODEL COMPARISON
===================================================== -->

<div id="page8" class="page">

<h1>Model Comparison</h1>

<div class="section">

{create_table(model_json)}

<h3>Select Metric</h3>

<select id="modelMetric"
        onchange="updateModelChart()">

{
''.join(
    f'<option value="{html.escape(str(col))}" '
    f'{"selected" if col == default_metric else ""}>'
    f'{html.escape(str(col))}'
    f'</option>'
    for col in numeric_model_columns
)
}

</select>


<div class="chart-box">

<canvas id="modelChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 9 - FEATURE IMPORTANCE
===================================================== -->

<div id="page9" class="page">

<h1>Feature Importance</h1>

<div class="info">

Feature importance is displayed when feature-importance
results are available from the forecasting notebook.

</div>

<div class="section">

<h3>
Available Model Result Columns
</h3>

<ul>

{
''.join(
    f'<li>{html.escape(str(col))}</li>'
    for col in model_results.columns
)
}

</ul>

</div>

</div>


<!-- =====================================================
     PAGE 10 - FORECAST ACCURACY
===================================================== -->

<div id="page10" class="page">

<h1>Forecast Accuracy</h1>

<div class="section">

{create_table(model_json)}

<h2>Evaluation Metrics</h2>

<p>
<b>MAE</b> – Mean Absolute Error
</p>

<p>
<b>RMSE</b> – Root Mean Squared Error
</p>

<p>
Lower values indicate better forecasting performance.
</p>

</div>

</div>


<!-- =====================================================
     PAGE 11 - FUTURE FORECAST
===================================================== -->

<div id="page11" class="page">

<h1>30-Day Future Sales Forecast</h1>

<div class="section">

{create_table(future_forecast_json)}

<h2>Forecast Value</h2>

<select id="futureMetric"
        onchange="updateFutureChart()">

{
''.join(
    f'<option value="{html.escape(str(col))}">'
    f'{html.escape(str(col))}'
    f'</option>'
    for col in future_forecast.select_dtypes(
        include=np.number
    ).columns
)
}

</select>


<div class="chart-box">

<canvas id="futureChart"></canvas>

</div>

</div>

</div>


<!-- =====================================================
     PAGE 12 - FINAL FORECAST
===================================================== -->

<div id="page12" class="page">

<h1>Final Forecast & Insights</h1>

<div class="section">

<h2>Final Forecast</h2>

{create_table(final_forecast_json)}

</div>


<div class="section">

<h2>Key Insights</h2>

<ul class="insights">

<li>
Historical sales patterns are analyzed using machine
learning features.
</li>

<li>
Multiple forecasting models are compared.
</li>

<li>
MAE and RMSE are used for model evaluation.
</li>

<li>
Future sales are generated using the selected
forecasting model.
</li>

<li>
The dashboard provides both historical analysis and
future sales predictions.
</li>

</ul>

</div>

</div>


<!-- =====================================================
     FOOTER
===================================================== -->

<div class="footer">

Foresight | Retail Sales Forecasting Project

</div>


</div>


<!-- =====================================================
     JAVASCRIPT DATA
===================================================== -->

<script>

const dailyData =
{js_json(daily_json)};

const trendData =
{js_json(trend_json)};

const storeData =
{js_json(store_json)};

const categoryData =
{js_json(category_json)};

const weekdayData =
{js_json(weekday_json)};

const monthlyData =
{js_json(monthly_json)};

const modelData =
{js_json(model_json)};

const futureData =
{js_json(future_forecast_json)};


let charts = {{}};


// ========================================================
// PAGE NAVIGATION
// ========================================================

function showPage(pageId, button) {{

    document
        .querySelectorAll(".page")
        .forEach(page => {{
            page.classList.remove("active");
        }});

    document
        .getElementById(pageId)
        .classList.add("active");


    document
        .querySelectorAll(".nav-button")
        .forEach(btn => {{
            btn.classList.remove("active");
        }});


    button.classList.add("active");


    window.scrollTo(
        {{
            top: 0,
            behavior: "smooth"
        }}
    );
}}


// ========================================================
// DAILY SALES CHART
// ========================================================

function createDailySalesChart() {{

    const ctx =
        document
        .getElementById(
            "dailySalesChart"
        );

    if (!ctx) return;


    charts.daily =
        new Chart(
            ctx,
            {{
                type: "line",

                data: {{
                    labels:
                        dailyData.map(
                            x => x.date
                        ),

                    datasets: [{{
                        label:
                            "Daily Sales",

                        data:
                            dailyData.map(
                                x =>
                                    x.daily_sales
                            ),

                        borderWidth: 2,

                        pointRadius: 0,

                        tension: 0.2
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {{
                        legend: {{
                            display: true
                        }}
                    }}
                }}
            }}
        );
}}


// ========================================================
// SALES OVERVIEW
// ========================================================

function createSalesOverviewChart() {{

    const ctx =
        document
        .getElementById(
            "salesOverviewChart"
        );

    if (!ctx) return;


    charts.salesOverview =
        new Chart(
            ctx,
            {{
                type: "line",

                data: {{
                    labels:
                        dailyData.map(
                            x => x.date
                        ),

                    datasets: [{{
                        label:
                            "Daily Sales",

                        data:
                            dailyData.map(
                                x =>
                                    x.daily_sales
                            ),

                        borderWidth: 2,

                        pointRadius: 0
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// TREND CHART
// ========================================================

function createTrendChart() {{

    const ctx =
        document
        .getElementById(
            "trendChart"
        );

    if (!ctx) return;


    charts.trend =
        new Chart(
            ctx,
            {{
                type: "line",

                data: {{
                    labels:
                        trendData.map(
                            x => x.date
                        ),

                    datasets: [

                        {{
                            label:
                                "Daily Sales",

                            data:
                                trendData.map(
                                    x =>
                                        x.daily_sales
                                ),

                            borderWidth: 1.5,

                            pointRadius: 0
                        }},

                        {{
                            label:
                                "7-Day Rolling Average",

                            data:
                                trendData.map(
                                    x =>
                                        x.rolling_7
                                ),

                            borderWidth: 2,

                            pointRadius: 0
                        }},

                        {{
                            label:
                                "30-Day Rolling Average",

                            data:
                                trendData.map(
                                    x =>
                                        x.rolling_30
                                ),

                            borderWidth: 2,

                            pointRadius: 0
                        }}

                    ]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// STORE CHART
// ========================================================

function createStoreChart() {{

    const ctx =
        document
        .getElementById(
            "storeChart"
        );

    if (!ctx || !storeData.length)
        return;


    charts.store =
        new Chart(
            ctx,
            {{
                type: "bar",

                data: {{
                    labels:
                        storeData.map(
                            x => x.store_id
                        ),

                    datasets: [{{
                        label:
                            "Total Sales",

                        data:
                            storeData.map(
                                x =>
                                    x.total_sales
                            ),

                        borderWidth: 1
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// CATEGORY CHART
// ========================================================

function createCategoryChart() {{

    const ctx =
        document
        .getElementById(
            "categoryChart"
        );

    if (!ctx || !categoryData.length)
        return;


    charts.category =
        new Chart(
            ctx,
            {{
                type: "bar",

                data: {{
                    labels:
                        categoryData.map(
                            x => x.cat_id
                        ),

                    datasets: [{{
                        label:
                            "Total Sales",

                        data:
                            categoryData.map(
                                x =>
                                    x.total_sales
                            ),

                        borderWidth: 1
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// WEEKDAY CHART
// ========================================================

function createWeekdayChart() {{

    const ctx =
        document
        .getElementById(
            "weekdayChart"
        );

    if (!ctx) return;


    charts.weekday =
        new Chart(
            ctx,
            {{
                type: "bar",

                data: {{
                    labels:
                        weekdayData.map(
                            x => x.name
                        ),

                    datasets: [{{
                        label:
                            "Average Sales",

                        data:
                            weekdayData.map(
                                x => x.value
                            ),

                        borderWidth: 1
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// MONTH CHART
// ========================================================

function createMonthChart() {{

    const ctx =
        document
        .getElementById(
            "monthChart"
        );

    if (!ctx) return;


    charts.month =
        new Chart(
            ctx,
            {{
                type: "bar",

                data: {{
                    labels:
                        monthlyData.map(
                            x => x.name
                        ),

                    datasets: [{{
                        label:
                            "Average Sales",

                        data:
                            monthlyData.map(
                                x => x.value
                            ),

                        borderWidth: 1
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// MODEL COMPARISON CHART
// ========================================================

function updateModelChart() {{

    const metric =
        document
        .getElementById(
            "modelMetric"
        )
        .value;


    if (!metric)
        return;


    const labels =
        modelData.map(
            row => row[
                Object.keys(
                    row
                )[0]
            ]
        );


    const values =
        modelData.map(
            row => row[metric]
        );


    const ctx =
        document
        .getElementById(
            "modelChart"
        );


    if (charts.model)
        charts.model.destroy();


    charts.model =
        new Chart(
            ctx,
            {{
                type: "bar",

                data: {{
                    labels: labels,

                    datasets: [{{
                        label: metric,

                        data: values,

                        borderWidth: 1
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// FUTURE FORECAST CHART
// ========================================================

function updateFutureChart() {{

    const metric =
        document
        .getElementById(
            "futureMetric"
        )
        .value;


    if (!metric)
        return;


    const labels =
        futureData.map(
            (row, index) => {{

                if (
                    row.date !== undefined &&
                    row.date !== null
                ) {{
                    return row.date;
                }}

                if (
                    row.ds !== undefined &&
                    row.ds !== null
                ) {{
                    return row.ds;
                }}

                return "Day " + (index + 1);
            }}
        );


    const values =
        futureData.map(
            row => row[metric]
        );


    const ctx =
        document
        .getElementById(
            "futureChart"
        );


    if (charts.future)
        charts.future.destroy();


    charts.future =
        new Chart(
            ctx,
            {{
                type: "line",

                data: {{
                    labels: labels,

                    datasets: [{{
                        label: metric,

                        data: values,

                        borderWidth: 2,

                        pointRadius: 3
                    }}]
                }},

                options: {{
                    responsive: true,

                    maintainAspectRatio: false
                }}
            }}
        );
}}


// ========================================================
// INITIALIZE
// ========================================================

window.addEventListener(
    "DOMContentLoaded",
    function() {{

        createDailySalesChart();

        createSalesOverviewChart();

        createTrendChart();

        createStoreChart();

        createCategoryChart();

        createWeekdayChart();

        createMonthChart();

        updateModelChart();

        updateFutureChart();

    }}
);

</script>


</body>

</html>
"""


# ============================================================
# 16. WRITE HTML FILE
# ============================================================

print("\nGenerating HTML...")


DASHBOARD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        html_content
    )


# ============================================================
# 17. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("HTML DASHBOARD CREATED SUCCESSFULLY")
print("=" * 60)

print("\nOutput file:")

print(OUTPUT_FILE)

print(
    "\nFile size:",
    round(
        OUTPUT_FILE.stat().st_size / (1024 * 1024),
        2
    ),
    "MB"
)

print("\nYou can now open dashboard.html in your browser.")

print("\n" + "=" * 60)
print("GENERATION COMPLETED")
print("=" * 60)