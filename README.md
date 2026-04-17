# 🛒 ShopSense: Market Intelligence Analysis — From 1 Million Rows to a Live AI Dashboard

Most businesses are sitting on data they never actually use.

I wanted to see what happens when you actually dig into it. So I took a real dataset — 1 million+ transactions from a UK wholesale company — and built a complete end-to-end analytics system from scratch. Raw Excel file in. Live AI-powered dashboard out.

**👉 [View the Live Dashboard](https://harsh-retail-analytics-project.streamlit.app)**

---

## 🗺️ What's in here?

This isn't just a notebook with a few charts. It covers the full data analyst workflow — the kind of work you'd actually do on the job:

| Phase | What was done |
|---|---|
| 🧹 Data Cleaning | Processed 1M+ raw rows down to 805K quality records |
| 🗄️ SQL Analytics | Loaded into MySQL, wrote 7 real business queries |
| 📈 EDA & Visualisation | 14 charts exploring trends, behaviour and performance |
| 👥 RFM Segmentation | Scored and segmented 5,878 customers into 8 groups |
| 🔄 Cohort Retention | Tracked customer loyalty across 25 monthly cohorts |
| 🛒 Basket Analysis | Apriori algorithm — discovered 60 product association rules |
| 🔮 ML Forecasting | Random Forest model predicting 6 months of revenue ahead |
| 🤖 GenAI Analyst | Live AI business analyst answering questions about the data |

---

## 💡 What the data actually told us

This is the part I enjoyed most — when the numbers started making real sense.

- **22% of customers generate 68% of revenue** — classic Pareto principle, confirmed with real data
- **The business barely gets orders on Saturdays** — only 30 orders vs 7,773 on Thursday. That single insight confirmed this is a B2B wholesale operation, not a regular retailer
- **Revenue doubles every September–November** — the business runs on Christmas season buying cycles
- **227 customers flagged as "At Risk"** average £4,488 each — that's over £1M in revenue quietly drifting away
- **Netherlands customers spend £2,430 per order** vs UK average of £439 — international buyers place massive bulk orders
- **Blue & Pink Spotty Party Candles** have a lift score of 30x — if someone buys one, there's an 88% chance they buy the other

These aren't just interesting stats — they're the kind of insights that actually change how a business operates.

---

## 🎨 The Dashboard

7 tabs, all interactive, all built with real data:

- **📈 Sales Trends** — monthly revenue, day-of-week patterns, top products
- **🌍 Geographic** — revenue by country, UK vs international breakdown, avg order value map
- **👥 RFM Segments** — customer scoring, segment scatter plot, recommended actions
- **🔄 Cohort Retention** — full triangular heatmap, month-1 retention by cohort
- **🔮 Forecast** — historical + 6-month ML prediction with confidence bands
- **🛒 Basket Analysis** — product association rules, lift scores, interactive filters
- **🤖 AI Business Analyst** — ask anything about the business, get data-backed answers instantly

---

## 🛠️ Tech Stack

```
Python 3.11          — core language
MySQL                — database and SQL analytics
Pandas / NumPy       — data manipulation
Matplotlib / Seaborn — exploratory visualisations
Plotly               — interactive dashboard charts
Scikit-learn         — Random Forest ML model
MLxtend              — Apriori basket analysis
Streamlit            — web dashboard
Gemini 2.0 Flash     — GenAI business analyst (via OpenRouter)
```

---

## 📁 Project Structure

```
retail-analytics/
│
├── data/                        ← raw dataset (not uploaded — too large)
├── deployment_data/             ← cleaned CSV exports for deployment
│   ├── transactions.csv.gz
│   ├── rfm_segments.csv
│   ├── revenue_forecast.csv
│   └── basket_rules.csv
├── notebooks/
│   └── eda_analysis.ipynb       ← full analysis — EDA, RFM, cohort, ML
├── sql/
│   └── analysis.sql             ← all 7 SQL business queries
├── src/
│   └── load_data.py             ← ETL pipeline — Excel → clean → MySQL
├── dashboard/
│   └── app.py                   ← Streamlit dashboard + AI analyst
├── requirements.txt
└── README.md
```

---

## ⚙️ Run it yourself

### 1. Clone the repo
```bash
git clone https://github.com/HarshShah3002/retail-analytics.git
cd retail-analytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get the dataset
Download from [UCI ML Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and drop it in the `data/` folder.

### 4. Set up MySQL (optional — only needed to re-run the analysis)
- Create a database called `retail_analytics`
- Run `python src/load_data.py` to load the data

### 5. Add your OpenRouter API key
Create a `.env` file in the root:
```
OPENROUTER_API_KEY=your_key_here
```
Get a free key at [openrouter.ai](https://openrouter.ai) — costs less than $0.01 for a full day of chatting.

### 6. Run the dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 Key Results

| Metric | Value |
|---|---|
| Total Revenue Analysed | £17,743,429 |
| Total Transactions | 805,549 |
| Unique Customers | 5,878 |
| Countries Served | 40+ |
| ML Model R² Score | 0.707 |
| H1 2012 Revenue Forecast | £3,626,974 |
| Product Association Rules | 60 |
| Strongest Product Lift | 30x |

---

## 🤖 The GenAI Part

The AI Business Analyst tab is powered by Gemini 2.0 Flash via OpenRouter. It has full context of the entire dataset — every revenue number, customer segment, forecast, basket rule and cohort pattern.

You can ask it things like:
- *"Which customers should we focus on retaining right now?"*
- *"What's driving the seasonal revenue spikes?"*
- *"Which international market should we expand into next?"*
- *"What products should we bundle together?"*

It responds like a data analyst, not just a chatbot — with specific numbers and actual recommendations.

---

## 📄 Dataset

[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — real transaction data from a UK-based online wholesale retailer, covering December 2009 to December 2011.

---

## 👤 About

**Harsh Shah** — Master's student graduating May 2026, looking for full-time Data Analyst roles.

- 🌐 [Live Dashboard](https://harsh-retail-analytics-project.streamlit.app)
- 💻 [GitHub](https://github.com/HarshShah3002/retail-analytics)
- 💼 [LinkedIn](https://www.linkedin.com/in/harshtarangshah)

---

*Built with curiosity, a lot of coffee, and genuine interest in what data can tell you when you actually listen to it.*
