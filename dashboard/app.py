import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from openai import OpenAI
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Dynamic gradient background ── */
    .stApp {
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f4ff 30%, #faf5ff 60%, #fff0f9 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        background: transparent;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #2563eb 60%, #7c3aed 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stDateInput label {
        color: rgba(255,255,255,0.85) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.6);
        border-radius: 12px;
        padding: 4px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.8);
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.88rem;
        font-weight: 500;
        border-radius: 8px;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        color: white !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.75);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        border: 1px solid rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(99,102,241,0.08);
    }

    /* ── Insight box ── */
    .insight-box {
        background: linear-gradient(135deg, rgba(239,246,255,0.9), rgba(245,243,255,0.9));
        border-left: 4px solid #7c3aed;
        padding: 0.8rem 1rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0 1rem 0;
        font-size: 0.9rem;
        color: #4c1d95;
        backdrop-filter: blur(8px);
        border-top: 1px solid rgba(124,58,237,0.15);
        border-right: 1px solid rgba(124,58,237,0.15);
        border-bottom: 1px solid rgba(124,58,237,0.15);
    }

    /* ── Section descriptions ── */
    .section-desc {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        margin-top: -0.5rem;
    }

    /* ── Headings ── */
    h1 { background: linear-gradient(135deg, #1e3a8a, #7c3aed);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         background-clip: text; }
    h2 { color: #1e293b; }
    h3 { color: #334155; }

    /* ── Chart containers ── */
    [data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,0.7);
        border-radius: 14px;
        padding: 0.5rem;
        border: 1px solid rgba(255,255,255,0.9);
        backdrop-filter: blur(8px);
        box-shadow: 0 2px 12px rgba(99,102,241,0.07);
    }

    /* ── Dataframes ── */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.8);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.9);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
        box-shadow: 0 2px 8px rgba(37,99,235,0.25);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(37,99,235,0.35);
        background: linear-gradient(135deg, #1d4ed8, #6d28d9);
    }

    /* ── Chat input ── */
    .stChatInput > div {
        background: rgba(255,255,255,0.8) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(124,58,237,0.2) !important;
        backdrop-filter: blur(8px);
    }

    /* Floating AI button */
    .floating-btn {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 9999;
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.75rem 1.4rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(37,99,235,0.4);
        transition: all 0.2s;
    }
    .floating-btn:hover {
        background: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37,99,235,0.5);
    }
    .chat-panel {
        position: fixed;
        bottom: 5.5rem;
        right: 2rem;
        width: 400px;
        max-height: 520px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.18);
        z-index: 9998;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    .chat-header {
        background: #2563eb;
        color: white;
        padding: 1rem 1.2rem;
        font-weight: 600;
        font-size: 0.95rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        background: #f8fafc;
        max-height: 340px;
    }
    .msg-user {
        background: #2563eb;
        color: white;
        padding: 0.6rem 0.9rem;
        border-radius: 12px 12px 2px 12px;
        font-size: 0.88rem;
        align-self: flex-end;
        max-width: 85%;
        line-height: 1.4;
    }
    .msg-ai {
        background: white;
        color: #1e293b;
        padding: 0.6rem 0.9rem;
        border-radius: 12px 12px 12px 2px;
        font-size: 0.88rem;
        align-self: flex-start;
        max-width: 90%;
        line-height: 1.5;
        border: 1px solid #e2e8f0;
    }
    .chat-input-row {
        display: flex;
        padding: 0.75rem;
        gap: 0.5rem;
        border-top: 1px solid #e2e8f0;
        background: white;
    }
    .chat-input-row input {
        flex: 1;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-size: 0.88rem;
        outline: none;
    }
    .chat-input-row input:focus {
        border-color: #2563eb;
    }
    .send-btn {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .tab-badge {
        background: rgba(255,255,255,0.25);
        padding: 0.15rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)


# ── DATABASE CONNECTION ───────────────────────────────────────
@st.cache_data
def load_data():
    engine = create_engine('mysql+pymysql://root:@localhost/retail_analytics')
    df = pd.read_sql('SELECT * FROM transactions', engine)
    rfm = pd.read_sql('SELECT * FROM rfm_segments', engine)
    forecast = pd.read_sql('SELECT * FROM revenue_forecast', engine)
    basket = pd.read_sql('SELECT * FROM basket_rules', engine)
    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    return df, rfm, forecast, basket

df, rfm, forecast, basket = load_data()


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Retail Analytics")
    st.markdown("*Online Retail II — UK Wholesaler (2009–2011)*")
    st.markdown("---")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("**Built by:** Harsh Shah")
    st.markdown("**Dataset:** UCI Online Retail II")
    st.markdown("**Tools:** Python · MySQL · Streamlit")
    st.markdown("**Records:** 805,549 transactions")


# ── USE FULL DATASET ─────────────────────────────────────────
filtered_df = df.copy()


# ── HEADER ────────────────────────────────────────────────────
st.title("🛒 Retail Analytics Dashboard")
st.markdown("A complete end-to-end analysis of a UK-based wholesale retailer — covering sales trends, customer behaviour, machine learning forecasts, and product insights.")
st.markdown("---")


# ── KPI CARDS ─────────────────────────────────────────────────
total_revenue = filtered_df['total_amount'].sum()
total_orders = filtered_df['invoice'].nunique()
total_customers = filtered_df['customer_id'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
total_items = filtered_df['quantity'].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("👥 Unique Customers", f"{total_customers:,}")
col4.metric("🧾 Avg Order Value", f"£{avg_order_value:,.2f}")
col5.metric("📦 Items Sold", f"{total_items:,}")

st.markdown("---")


# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Sales Trends",
    "🌍 Geographic",
    "👥 RFM Segments",
    "🔄 Cohort Retention",
    "🔮 Forecast",
    "🛒 Basket Analysis",
    "🤖 AI Business Analyst"
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — SALES TRENDS
# ══════════════════════════════════════════════════════════════
with tab1:
    st.header("Sales Trends")
    st.markdown('<p class="section-desc">How has revenue and order volume changed over time? This section reveals seasonality patterns and growth trends.</p>', unsafe_allow_html=True)

    # Monthly Revenue
    st.subheader("Monthly Revenue Trend")
    st.markdown('<p class="section-desc">Each point represents one month of total sales. Look for recurring peaks — they reveal the business\'s seasonal rhythm.</p>', unsafe_allow_html=True)

    monthly = filtered_df.copy()
    monthly['year_month'] = monthly['invoice_date'].dt.to_period('M').astype(str)
    monthly_rev = monthly.groupby('year_month').agg(
        revenue=('total_amount', 'sum'),
        orders=('invoice', 'nunique'),
        customers=('customer_id', 'nunique')
    ).reset_index()

    fig1 = px.area(monthly_rev, x='year_month', y='revenue',
                   labels={'revenue': 'Revenue (£)', 'year_month': 'Month'},
                   color_discrete_sequence=['#6366f1'])
    fig1.update_traces(fill='tozeroy', fillcolor='rgba(99,102,241,0.1)', line_width=2.5)
    fig1.update_layout(hovermode='x unified', plot_bgcolor='rgba(255,255,255,0.0)',
                       paper_bgcolor='rgba(255,255,255,0.0)', height=350)
    fig1.update_xaxes(showgrid=False)
    fig1.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.15)')
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Revenue spikes every September–November, driven by early Christmas gift ordering. 
    This business is highly seasonal — Q4 (Oct–Nov) consistently generates 40–60% more revenue than other months.
    Jan–Feb are the slowest months as the post-Christmas slowdown kicks in.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orders vs Customers per Month")
        st.markdown('<p class="section-desc">Comparing order volume to unique customers shows whether growth comes from new customers or repeat buyers.</p>', unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly_rev['year_month'], y=monthly_rev['orders'],
                              name='Orders', marker_color='#818cf8', opacity=0.8))
        fig2.add_trace(go.Scatter(x=monthly_rev['year_month'], y=monthly_rev['customers'],
                                  name='Customers', line=dict(color='#f472b6', width=2.5),
                                  mode='lines+markers', yaxis='y2'))
        fig2.update_layout(
            yaxis=dict(title='Orders', showgrid=True, gridcolor='rgba(148,163,184,0.15)'),
            yaxis2=dict(title='Customers', overlaying='y', side='right'),
            plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
            hovermode='x unified', height=350,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Revenue by Day of Week")
        st.markdown('<p class="section-desc">Which days generate the most sales? This reveals whether customers are businesses (weekdays) or consumers (weekends).</p>', unsafe_allow_html=True)

        filtered_df['day_of_week'] = filtered_df['invoice_date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_rev = filtered_df.groupby('day_of_week')['total_amount'].sum().reindex(day_order).reset_index()
        day_rev.columns = ['day', 'revenue']

        fig3 = px.bar(day_rev, x='day', y='revenue',
                      labels={'revenue': 'Revenue (£)', 'day': ''},
                      text=day_rev['revenue'].apply(lambda x: f'£{x:,.0f}'))
        fig3.update_traces(textposition='outside', textfont_size=10,
                           textfont_color='#1e293b', marker_color='#818cf8')
        fig3.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=350)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Thursday is the busiest day by far. Saturday is almost completely dead (only 30 orders vs 7,773 on Thursday). 
    This confirms this is a B2B wholesale business — companies place orders mid-week, not on weekends.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Top 10 Products by Revenue")
    st.markdown('<p class="section-desc">Which products generate the most revenue? Non-product entries like postage have been excluded for accuracy.</p>', unsafe_allow_html=True)

    top_products = filtered_df[~filtered_df['stock_code'].isin(['M', 'POST'])]
    top_products = top_products.groupby('description').agg(
        revenue=('total_amount', 'sum'),
        quantity=('quantity', 'sum'),
        orders=('invoice', 'nunique')
    ).sort_values('revenue', ascending=False).head(10).reset_index()
    top_products['description'] = top_products['description'].str[:35]
    top_products['avg_per_order'] = (top_products['revenue'] / top_products['orders']).round(2)

    fig4 = px.bar(top_products, x='revenue', y='description',
                  orientation='h',
                  hover_data=['quantity', 'orders', 'avg_per_order'],
                  labels={'revenue': 'Total Revenue (£)', 'description': '',
                          'quantity': 'Units Sold', 'orders': 'Orders',
                          'avg_per_order': 'Avg £/Order'},
                  color='revenue', color_continuous_scale=[[0,'#99f6e4'],[0.4,'#2dd4bf'],[1,'#0f766e']],
                  text=top_products['revenue'].apply(lambda x: f'£{x:,.0f}'))
    fig4.update_traces(textposition='outside', textfont_size=10, textfont_color='#1e293b')
    fig4.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                       coloraxis_showscale=False, height=420,
                       yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> The REGENCY CAKESTAND 3 TIER is the top revenue product despite selling far fewer units — it has a higher price per unit. 
    Home décor and gifting items dominate the top 10, confirming this is a gift/home wholesale company.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC
# ══════════════════════════════════════════════════════════════
with tab2:
    st.header("Geographic Analysis")
    st.markdown('<p class="section-desc">Where in the world do customers come from, and how much do they spend? This section shows the global spread of the business.</p>', unsafe_allow_html=True)

    country_rev = filtered_df.groupby('country').agg(
        revenue=('total_amount', 'sum'),
        orders=('invoice', 'nunique'),
        customers=('customer_id', 'nunique')
    ).reset_index().sort_values('revenue', ascending=False)
    country_rev['avg_order_value'] = (country_rev['revenue'] / country_rev['orders']).round(2)
    country_rev['revenue_pct'] = (country_rev['revenue'] / country_rev['revenue'].sum() * 100).round(1)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Top 10 Countries by Revenue")
        st.markdown('<p class="section-desc">Total revenue generated per country. The UK dominates as this is a UK-based business.</p>', unsafe_allow_html=True)

        top_countries = country_rev.head(10)
        fig5 = px.bar(top_countries, x='revenue', y='country',
                      orientation='h',
                      hover_data=['orders', 'customers', 'revenue_pct'],
                      labels={'revenue': 'Total Revenue (£)', 'country': '',
                              'orders': 'Orders', 'customers': 'Customers',
                              'revenue_pct': '% of Total Revenue'},
                      color='revenue', color_continuous_scale=[[0,'#c7d2fe'],[0.4,'#818cf8'],[1,'#3730a3']],
                      text=top_countries['revenue'].apply(lambda x: f'£{x:,.0f}'))
        fig5.update_traces(textposition='outside', textfont_size=9, textfont_color='#1e293b')
        fig5.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                           coloraxis_showscale=False, height=400,
                           yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Revenue Share — UK vs International")
        st.markdown('<p class="section-desc">How much of total revenue comes from the UK vs all other countries combined?</p>', unsafe_allow_html=True)

        uk_rev = country_rev[country_rev['country'] == 'United Kingdom']['revenue'].values[0]
        intl_rev = country_rev[country_rev['country'] != 'United Kingdom']['revenue'].sum()

        fig6 = px.pie(
            values=[uk_rev, intl_rev],
            names=['United Kingdom', 'International'],
            color_discrete_sequence=['#6366f1', '#f59e0b'],
            hole=0.5
        )
        fig6.update_traces(textposition='outside', textinfo='percent+label',
                           pull=[0.03, 0])
        fig6.update_layout(height=400, showlegend=True,
                           annotations=[dict(text='Revenue<br>Share', x=0.5, y=0.5,
                                            font_size=13, showarrow=False)])
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> The UK accounts for ~83% of all revenue. However, international customers are 
    strategically important — they place fewer but much larger orders, making them high-value targets for growth.
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Average Order Value by Country")
        st.markdown('<p class="section-desc">How much does each country spend per order on average? (Countries with at least 10 orders only, to avoid misleading averages.)</p>', unsafe_allow_html=True)

        avg_order = country_rev[country_rev['orders'] >= 10].sort_values('avg_order_value', ascending=False).head(10)
        fig7 = px.bar(avg_order, x='avg_order_value', y='country',
                      orientation='h',
                      labels={'avg_order_value': 'Avg Order Value (£)', 'country': ''},
                      color='avg_order_value', color_continuous_scale=[[0,'#fde68a'],[0.4,'#fb923c'],[1,'#be123c']],
                      text=avg_order['avg_order_value'].apply(lambda x: f'£{x:,.0f}'))
        fig7.update_traces(textposition='outside', textfont_size=10, textfont_color='#1e293b')
        fig7.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                           coloraxis_showscale=False, height=400,
                           yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig7, use_container_width=True)

    with col4:
        st.subheader("International Markets — Customers vs Revenue")
        st.markdown('<p class="section-desc">Bubble chart showing each country\'s customer count vs revenue. Bigger bubbles = higher average order value. Ideal targets are bottom-right (few customers, high revenue).</p>', unsafe_allow_html=True)

        intl = country_rev[(country_rev['country'] != 'United Kingdom') &
                           (country_rev['orders'] >= 5)].head(20)
        fig8 = px.scatter(intl, x='customers', y='revenue',
                          size='avg_order_value', color='avg_order_value',
                          hover_name='country',
                          hover_data={'orders': True, 'avg_order_value': ':.0f'},
                          labels={'customers': 'Number of Customers',
                                  'revenue': 'Total Revenue (£)',
                                  'avg_order_value': 'Avg Order Value'},
                          color_continuous_scale=[[0,'#c7d2fe'],[0.4,'#818cf8'],[1,'#3730a3']],
                          size_max=50)
        fig8.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=400)
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Netherlands and EIRE (Ireland) are standout international markets — 
    very few customers but enormous revenue per order (£2,430 avg for Netherlands). 
    Singapore has only 11 orders but £2,301 avg order value — a huge untapped growth opportunity.
    </div>
    """, unsafe_allow_html=True)

    # Full country table
    with st.expander("📊 View Full Country Data Table"):
        st.dataframe(country_rev.round(2), use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — RFM SEGMENTS
# ══════════════════════════════════════════════════════════════
with tab3:
    st.header("RFM Customer Segmentation")
    st.markdown("""
    <p class="section-desc">
    RFM stands for <strong>Recency</strong> (how recently a customer bought), 
    <strong>Frequency</strong> (how often they buy), and 
    <strong>Monetary</strong> (how much they spend). 
    Each customer is scored 1–5 on each dimension and grouped into actionable segments.
    </p>
    """, unsafe_allow_html=True)

    # Segment summary table
    seg_summary = rfm.groupby('segment').agg(
        customers=('customer_id', 'count'),
        avg_recency=('recency', 'mean'),
        avg_frequency=('frequency', 'mean'),
        avg_monetary=('monetary', 'mean'),
        total_revenue=('monetary', 'sum')
    ).round(2).reset_index().sort_values('total_revenue', ascending=False)
    seg_summary['revenue_share'] = (seg_summary['total_revenue'] / seg_summary['total_revenue'].sum() * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Count per Segment")
        st.markdown('<p class="section-desc">How many customers fall into each segment?</p>', unsafe_allow_html=True)

        seg_counts = rfm['segment'].value_counts().reset_index()
        seg_counts.columns = ['segment', 'count']
        colors = {'Champions': '#6366f1', 'Loyal Customers': '#22d3ee',
                  'Potential Loyalists': '#a78bfa', 'Recent Customers': '#34d399',
                  'At Risk': '#fb7185', 'Needs Attention': '#fbbf24',
                  'Lost': '#94a3b8', 'Others': '#cbd5e1'}
        fig9 = px.pie(seg_counts, values='count', names='segment',
                      color='segment', color_discrete_map=colors,
                      hole=0.45)
        fig9.update_traces(textposition='outside', textinfo='percent+label')
        fig9.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        st.subheader("Revenue Contribution per Segment")
        st.markdown('<p class="section-desc">How much total revenue does each segment generate? This is the most important chart for business decisions.</p>', unsafe_allow_html=True)

        seg_rev = seg_summary.copy()
        fig10 = px.bar(seg_rev, x='total_revenue', y='segment',
                       orientation='h',
                       color='segment', color_discrete_map=colors,
                       text=seg_rev['total_revenue'].apply(lambda x: f'£{x:,.0f}'),
                       labels={'total_revenue': 'Total Revenue (£)', 'segment': ''})
        fig10.update_traces(textposition='outside', textfont_size=10, textfont_color='#1e293b')
        fig10.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                            showlegend=False, height=400,
                            yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig10, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Champions make up only 22% of customers but generate <strong>68% of total revenue (£12.1M)</strong> — 
    a textbook example of the 80/20 Pareto Principle. The 227 "At Risk" customers average £4,488 each — 
    losing them means losing £1M+ in revenue. Urgent win-back campaigns are needed for this group.
    </div>
    """, unsafe_allow_html=True)

    # RFM Scatter Plot
    st.subheader("RFM Score Distribution — Recency vs Monetary")
    st.markdown('<p class="section-desc">Each dot is a customer. Position shows recency (x) vs total spend (y). Colour shows their segment. Ideal customers are top-right — recent AND high spending.</p>', unsafe_allow_html=True)

    rfm_sample = rfm.sample(min(1000, len(rfm)), random_state=42)
    fig11 = px.scatter(rfm_sample, x='recency', y='monetary',
                       color='segment', color_discrete_map=colors,
                       size='frequency', size_max=15,
                       hover_data=['customer_id', 'frequency', 'r_score', 'f_score', 'm_score'],
                       labels={'recency': 'Days Since Last Purchase (lower = more recent)',
                               'monetary': 'Total Spend (£)',
                               'frequency': 'Number of Orders'})
    fig11.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=450)
    st.plotly_chart(fig11, use_container_width=True)

    # Segment detail table
    st.subheader("Segment Summary Table")
    st.markdown('<p class="section-desc">Full breakdown of each segment — use this to decide where to focus marketing and retention efforts.</p>', unsafe_allow_html=True)

    seg_display = seg_summary.rename(columns={
        'customers': 'Customers', 'avg_recency': 'Avg Days Since Purchase',
        'avg_frequency': 'Avg Orders', 'avg_monetary': 'Avg Spend (£)',
        'total_revenue': 'Total Revenue (£)', 'revenue_share': 'Revenue Share (%)'
    })
    st.dataframe(seg_display, use_container_width=True, hide_index=True)

    # Recommended actions
    st.subheader("Recommended Actions by Segment")
    actions = {
        "🏆 Champions": "Reward them with exclusive deals. Ask for reviews. Make them brand ambassadors.",
        "💚 Loyal Customers": "Upsell premium products. Offer loyalty rewards. Keep them engaged.",
        "🌱 Potential Loyalists": "Offer a membership program. Encourage second and third purchases.",
        "🆕 Recent Customers": "Onboard well with a welcome series. Encourage repeat purchase within 30 days.",
        "⚠️ At Risk": "URGENT — Send personalised win-back emails. Offer special discounts immediately.",
        "🔍 Needs Attention": "Re-engage with targeted campaigns. Remind them of products they liked.",
        "😴 Lost": "Low priority — send a final re-engagement offer. Accept some are gone.",
    }
    cols = st.columns(2)
    for i, (seg, action) in enumerate(actions.items()):
        with cols[i % 2]:
            st.markdown(f"**{seg}**  \n{action}")


# ══════════════════════════════════════════════════════════════
# TAB 4 — COHORT RETENTION
# ══════════════════════════════════════════════════════════════
with tab4:
    st.header("Cohort Retention Analysis")
    st.markdown("""
    <p class="section-desc">
    A cohort is a group of customers who made their <strong>first purchase in the same month</strong>. 
    We then track what percentage of them return in the following months. 
    This tells us how good the business is at <strong>keeping customers coming back</strong>.
    </p>
    """, unsafe_allow_html=True)

    # Rebuild cohort data
    df_cohort = df.copy()
    df_cohort['order_month'] = df_cohort['invoice_date'].dt.to_period('M')
    cohort_min = df_cohort.groupby('customer_id')['order_month'].min().reset_index()
    cohort_min.columns = ['customer_id', 'cohort_month']
    df_cohort = df_cohort.merge(cohort_min, on='customer_id')
    df_cohort['cohort_index'] = (df_cohort['order_month'] - df_cohort['cohort_month']).apply(lambda x: x.n)

    cohort_data = df_cohort.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']
    cohort_pivot = cohort_data.pivot_table(index='cohort_month', columns='cohort_index', values='customers')
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0).round(3) * 100
    retention.index = retention.index.astype(str)

    # Show first 12 months only
    retention_12 = retention.iloc[:, :12]

    st.subheader("Retention Heatmap — % of Customers Returning Each Month")
    st.markdown('<p class="section-desc">Each row = a group of customers who first bought that month. Each column = months after their first purchase. Darker colour = more customers came back. Month 0 is always 100% (their first purchase).</p>', unsafe_allow_html=True)

    fig12 = px.imshow(
        retention_12,
        color_continuous_scale='YlOrRd',
        aspect='auto',
        labels=dict(x='Months Since First Purchase', y='Cohort (First Purchase Month)', color='Retention %'),
        zmin=0, zmax=50,
        text_auto='.0f'
    )
    fig12.update_layout(height=600, plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)')
    fig12.update_coloraxes(colorbar_title='Retention %')
    st.plotly_chart(fig12, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Retention drops sharply after month 0 — from 100% to roughly 15–35% in month 1. 
    This means 65–85% of new customers don't come back the very next month, which is a big opportunity. 
    The December 2009 cohort shows the strongest retention (35.3% in month 1) — Christmas-season buyers tend to be the most loyal.
    Late 2010 cohorts (Oct–Dec) had the weakest retention — likely one-time holiday buyers who never returned.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Average Retention by Month Number")
        st.markdown('<p class="section-desc">What % of customers typically return at each month after their first purchase, averaged across all cohorts?</p>', unsafe_allow_html=True)

        avg_retention = retention_12.mean().reset_index()
        avg_retention.columns = ['month', 'avg_retention']
        avg_retention = avg_retention[avg_retention['month'] > 0]

        fig13 = px.line(avg_retention, x='month', y='avg_retention',
                        markers=True, color_discrete_sequence=['#6366f1'],
                        labels={'month': 'Months After First Purchase',
                                'avg_retention': 'Avg Retention (%)'})
        fig13.update_traces(line_width=2.5, marker_size=8)
        fig13.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=300)
        fig13.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.15)')
        st.plotly_chart(fig13, use_container_width=True)

    with col2:
        st.subheader("Month 1 Retention by Cohort")
        st.markdown('<p class="section-desc">How many customers came back the very next month after their first purchase? A higher bar means that cohort was more loyal from the start.</p>', unsafe_allow_html=True)

        month1 = retention_12[[1]].reset_index()
        month1.columns = ['cohort', 'retention_m1']
        month1 = month1.dropna()

        fig14 = px.bar(month1, x='cohort', y='retention_m1',
                       labels={'cohort': 'Cohort Month', 'retention_m1': 'Month 1 Retention (%)'},
                       text=month1['retention_m1'].apply(lambda x: f'{x:.0f}%'))
        fig14.update_traces(textposition='outside', textfont_size=9,
                            textfont_color='#1e293b', marker_color='#6366f1')
        fig14.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=300)
        fig14.update_xaxes(tickangle=45)
        st.plotly_chart(fig14, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 5 — FORECAST
# ══════════════════════════════════════════════════════════════
with tab5:
    st.header("ML Revenue Forecast")
    st.markdown("""
    <p class="section-desc">
    Using a <strong>Random Forest machine learning model</strong> trained on 24 months of historical data, 
    we predict the next 6 months of revenue. The model uses seasonality patterns, recent trends, 
    and lag features (past months' revenue) to make predictions.
    </p>
    """, unsafe_allow_html=True)

    # Model performance metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Model R² Score", "0.707", help="How much of revenue variance the model explains. 1.0 = perfect.")
    col2.metric("📏 Mean Abs Error", "£93,750", help="On average, predictions are off by this amount.")
    col3.metric("📐 RMSE", "£117,576", help="Root Mean Squared Error — penalises large errors more.")

    st.markdown("""
    <div class="insight-box">
    📌 <strong>About the model:</strong> An R² of 0.707 means the model explains ~71% of revenue variance — decent for a dataset with only 24 months. 
    The main driver is seasonality (month of year accounts for 53% of predictions), followed by Q4 indicator (20%). 
    With more historical data (3–5 years), accuracy would improve significantly.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Historical Revenue + 6 Month Forecast (2012)")
    st.markdown('<p class="section-desc">Blue line = actual historical revenue. Orange dashed line = ML model predictions for Jan–Jun 2012. Hover over points to see exact values.</p>', unsafe_allow_html=True)

    monthly_hist = df.copy()
    monthly_hist['year_month'] = monthly_hist['invoice_date'].dt.to_period('M').astype(str)
    hist_rev = monthly_hist.groupby('year_month')['total_amount'].sum().reset_index()
    hist_rev.columns = ['month', 'revenue']
    hist_rev['type'] = 'Historical'
    hist_rev['lower'] = None
    hist_rev['upper'] = None

    forecast_plot = forecast[['month', 'predicted_revenue']].copy()
    forecast_plot.columns = ['month', 'revenue']
    forecast_plot['type'] = 'Forecast'
    # Add confidence interval (±15%)
    forecast_plot['lower'] = forecast_plot['revenue'] * 0.85
    forecast_plot['upper'] = forecast_plot['revenue'] * 1.15

    fig15 = go.Figure()

    # Confidence interval band
    fig15.add_trace(go.Scatter(
        x=forecast_plot['month'].tolist() + forecast_plot['month'].tolist()[::-1],
        y=forecast_plot['upper'].tolist() + forecast_plot['lower'].tolist()[::-1],
        fill='toself', fillcolor='rgba(244,114,182,0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Forecast Range (±15%)', showlegend=True
    ))

    # Historical line
    fig15.add_trace(go.Scatter(
        x=hist_rev['month'], y=hist_rev['revenue'],
        mode='lines+markers', name='Historical Revenue',
        line=dict(color='#6366f1', width=2.5),
        marker=dict(size=5)
    ))

    # Forecast line
    fig15.add_trace(go.Scatter(
        x=forecast_plot['month'], y=forecast_plot['revenue'],
        mode='lines+markers', name='Predicted Revenue',
        line=dict(color='#f472b6', width=2.5, dash='dash'),
        marker=dict(size=8, symbol='square')
    ))

    fig15.update_layout(
        hovermode='x unified', plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
        height=420, legend=dict(orientation='h', yanchor='bottom', y=1.02),
        xaxis=dict(showgrid=False),
        yaxis=dict(title='Revenue (£)', showgrid=True, gridcolor='rgba(148,163,184,0.15)')
    )
    st.plotly_chart(fig15, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Forecast Details")
        forecast_display = forecast[['month', 'predicted_revenue']].copy()
        forecast_display['predicted_revenue'] = forecast_display['predicted_revenue'].apply(lambda x: f'£{x:,.0f}')
        forecast_display.columns = ['Month', 'Predicted Revenue']
        st.dataframe(forecast_display, use_container_width=True, hide_index=True)
        st.metric("Total H1 2012 Forecast", f"£{forecast['predicted_revenue'].sum():,.0f}")

    with col2:
        st.subheader("Feature Importance")
        st.markdown('<p class="section-desc">Which inputs does the model rely on most to make predictions? Higher % = stronger driver of revenue.</p>', unsafe_allow_html=True)

        feature_imp = pd.DataFrame({
            'Feature': ['Month of Year', 'Q4 Indicator', 'Last Month Revenue',
                        '3 Months Ago Revenue', 'Time Trend', '2 Months Ago Revenue', '3-Month Avg'],
            'Importance': [53.2, 20.2, 7.8, 7.5, 4.5, 3.6, 3.3]
        }).sort_values('Importance', ascending=True)

        fig16 = px.bar(feature_imp, x='Importance', y='Feature',
                       orientation='h',
                       color='Importance', color_continuous_scale=[[0,'#fbcfe8'],[0.4,'#e879f9'],[1,'#6b21a8']],
                       text=feature_imp['Importance'].apply(lambda x: f'{x:.1f}%'),
                       labels={'Importance': 'Importance (%)', 'Feature': ''})
        fig16.update_traces(textposition='outside', textfont_size=10, textfont_color='#1e293b')
        fig16.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                            coloraxis_showscale=False, height=300)
        st.plotly_chart(fig16, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> Month of year + Q4 indicator together explain 73% of predictions — confirming this business is 
    primarily seasonal. The model is essentially saying: "Tell me what month it is, and I can predict revenue fairly well." 
    Historical revenue (lag features) contributes only ~19%, meaning momentum matters less than the calendar.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 6 — BASKET ANALYSIS
# ══════════════════════════════════════════════════════════════
with tab6:
    st.header("Market Basket Analysis")
    st.markdown("""
    <p class="section-desc">
    Market Basket Analysis finds which products are <strong>frequently bought together</strong>. 
    Think of Amazon's "Customers who bought this also bought..." feature. 
    We use the <strong>Apriori algorithm</strong> to discover these hidden product relationships from 33,000+ UK orders.
    </p>
    """, unsafe_allow_html=True)

    # Explain the metrics
    with st.expander("📖 How to read these metrics"):
        col1, col2, col3 = st.columns(3)
        col1.markdown("**Support**  \nHow often this product pair appears together. 0.02 = in 2% of all baskets. Higher = more common pair.")
        col2.markdown("**Confidence**  \nIf a customer buys Product A, what % chance do they also buy Product B? 0.88 = 88% chance. Higher = stronger rule.")
        col3.markdown("**Lift**  \nHow much MORE likely are these products bought together vs separately? Lift of 30 = 30x more likely together. Anything above 1 is meaningful.")

    # Filters
    st.markdown("### Filter Rules")
    col1, col2, col3 = st.columns(3)
    min_lift = col1.slider("Minimum Lift Score", 1.0, 30.0, 1.5, 0.5,
                           help="Higher lift = stronger product association")
    min_confidence = col2.slider("Minimum Confidence", 0.0, 1.0, 0.3, 0.05,
                                 help="Probability of buying B given A was bought")
    top_n = col3.slider("Number of Rules to Show", 5, 60, 20,
                        help="How many product pairs to display")

    filtered_rules = basket[
        (basket['lift'] >= min_lift) &
        (basket['confidence'] >= min_confidence)
    ].sort_values('lift', ascending=False).head(top_n)

    st.markdown(f"**{len(filtered_rules)} rules** match your filters out of 60 total rules discovered.")

    # Top pairs bar chart
    st.subheader("Top Product Pairs by Lift Score")
    st.markdown('<p class="section-desc">The higher the lift, the stronger the association. A lift of 30 means these products are 30x more likely to be bought together than by chance.</p>', unsafe_allow_html=True)

    top_pairs = filtered_rules.head(10).copy()
    top_pairs['pair'] = top_pairs['product_a'].str[:22] + ' → ' + top_pairs['product_b'].str[:22]

    fig17 = px.bar(top_pairs, x='lift', y='pair',
                   orientation='h',
                   color='confidence', color_continuous_scale=[[0,'#fbcfe8'],[0.4,'#e879f9'],[1,'#6b21a8']],
                   text=top_pairs['lift'].apply(lambda x: f'{x:.1f}x'),
                   labels={'lift': 'Lift Score', 'pair': '',
                           'confidence': 'Confidence'},
                   hover_data={'product_a': True, 'product_b': True,
                               'support': ':.3f', 'confidence': ':.2f', 'lift': ':.1f'})
    fig17.update_traces(textposition='outside', textfont_size=10, textfont_color='#1e293b')
    fig17.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                        height=420, yaxis=dict(autorange='reversed'),
                        coloraxis_colorbar_title='Confidence')
    st.plotly_chart(fig17, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Support vs Confidence")
        st.markdown('<p class="section-desc">Each bubble is a product pair. Bigger & darker = higher lift (stronger association). Best rules are top-right — common AND reliable.</p>', unsafe_allow_html=True)

        fig18 = px.scatter(filtered_rules,
                           x='support', y='confidence',
                           size='lift', color='lift',
                           hover_data=['product_a', 'product_b'],
                           color_continuous_scale='YlOrRd',
                           size_max=40,
                           labels={'support': 'Support (how common)',
                                   'confidence': 'Confidence (how reliable)',
                                   'lift': 'Lift'})
        fig18.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)', height=380)
        st.plotly_chart(fig18, use_container_width=True)

    with col2:
        st.subheader("Confidence Distribution")
        st.markdown('<p class="section-desc">Distribution of confidence scores across all rules. A peak near 1.0 means most rules are highly reliable — when you buy A, you almost always buy B.</p>', unsafe_allow_html=True)

        fig19 = px.histogram(filtered_rules, x='confidence', nbins=15,
                             color_discrete_sequence=['#6366f1'],
                             labels={'confidence': 'Confidence Score', 'count': 'Number of Rules'})
        fig19.update_layout(plot_bgcolor='rgba(255,255,255,0.0)', paper_bgcolor='rgba(255,255,255,0.0)',
                            bargap=0.1, height=380)
        st.plotly_chart(fig19, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>Key Insight:</strong> The strongest association is Blue & Pink Spotty Party Candles — 88% of customers who buy one also buy the other (lift = 30x). 
    Easter baskets are bought as colour sets (Pink + Blue + Cream together). 
    Bathroom & Toilet metal signs are almost always purchased together. 
    <strong>Business recommendation:</strong> Bundle colour variants as "Collection Packs", create seasonal gift sets, 
    and use these rules to power "Frequently Bought Together" recommendations on the website.
    </div>
    """, unsafe_allow_html=True)

    # Full rules table
    st.subheader("Full Association Rules Table")
    st.markdown('<p class="section-desc">Complete list of all discovered product associations matching your filters.</p>', unsafe_allow_html=True)

    rules_display = filtered_rules[['product_a', 'product_b', 'support', 'confidence', 'lift']].copy()
    rules_display.columns = ['Product A (If bought...)', 'Product B (...also buy)', 'Support', 'Confidence', 'Lift']
    rules_display = rules_display.round(3)
    st.dataframe(rules_display, use_container_width=True, hide_index=True)




# ══════════════════════════════════════════════════════════════
# TAB 7 — AI BUSINESS ANALYST
# ══════════════════════════════════════════════════════════════
with tab7:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e1b4b, #3730a3, #6d28d9);
                border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;
                color: white;'>
        <div style='display:flex; align-items:center; gap:1rem; margin-bottom:0.8rem;'>
            <span style='font-size:2.5rem;'>🤖</span>
            <div>
                <h2 style='margin:0; color:white; font-size:1.6rem;'>AI Business Analyst</h2>
                <p style='margin:0; opacity:0.85; font-size:0.9rem;'>
                    Powered by Gemini 2.0 Flash — your intelligent retail data analyst
                </p>
            </div>
        </div>
        <p style='margin:0; opacity:0.9; font-size:0.9rem; line-height:1.6;'>
            Ask me anything about this retail business — revenue performance, customer behaviour,
            product insights, market opportunities, or strategic recommendations.
            I have full knowledge of all 805,549 transactions, 5,878 customers, and every analysis
            on this dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── BUILD DATA CONTEXT ────────────────────────────────────
    @st.cache_data
    def build_ai_context():
        total_revenue = df['total_amount'].sum()
        total_orders = df['invoice'].nunique()
        total_customers = df['customer_id'].nunique()
        avg_order_value = total_revenue / total_orders

        top_countries = df.groupby('country')['total_amount'].sum()\
                          .sort_values(ascending=False).head(10)
        top_products = df[~df['stock_code'].isin(['M','POST'])]\
                         .groupby('description')['total_amount'].sum()\
                         .sort_values(ascending=False).head(10)

        df_copy = df.copy()
        df_copy['year_month'] = df_copy['invoice_date'].dt.to_period('M').astype(str)
        monthly = df_copy.groupby('year_month')['total_amount'].sum()
        best_month = monthly.idxmax()
        worst_month = monthly.idxmin()

        df_copy['day_of_week'] = df_copy['invoice_date'].dt.day_name()
        day_rev = df_copy.groupby('day_of_week')['total_amount'].sum().sort_values(ascending=False)

        seg_summary = rfm.groupby('segment').agg(
            customers=('customer_id', 'count'),
            total_revenue=('monetary', 'sum'),
            avg_spend=('monetary', 'mean'),
            avg_recency=('recency', 'mean'),
            avg_frequency=('frequency', 'mean')
        ).round(2).sort_values('total_revenue', ascending=False)

        top_rules = basket.sort_values('lift', ascending=False).head(10)

        country_avg = df.groupby('country').agg(
            revenue=('total_amount','sum'),
            orders=('invoice','nunique')
        )
        country_avg['avg_order'] = (country_avg['revenue'] / country_avg['orders']).round(2)
        country_avg = country_avg[country_avg['orders'] >= 10].sort_values('avg_order', ascending=False).head(10)

        return f"""
You are an expert senior retail business analyst and strategic advisor embedded in a live analytics dashboard.
Your role is to:
1. Answer data questions with precise numbers from the dataset
2. Provide business insights and explain what the numbers mean
3. Give strategic recommendations based on the data
4. Suggest next steps or actions the business should take
5. Identify risks, opportunities, and patterns

Always be specific with numbers. Structure longer answers with bullet points.
Be direct and confident — you are the expert. Keep answers concise but complete.
If asked for recommendations, think like a business consultant, not just a data analyst.

=== BUSINESS PROFILE ===
Type: UK-based B2B wholesale gift and home decor company
Dataset period: December 2009 to December 2011 (2 full years)
Total revenue: £{total_revenue:,.0f}
Total orders: {total_orders:,}
Total unique customers: {total_customers:,}
Average order value: £{avg_order_value:,.2f}
Total items sold: {df['quantity'].sum():,}
Total unique products: {df['stock_code'].nunique():,}
Total countries served: {df['country'].nunique():,}

=== REVENUE BY COUNTRY (TOP 10) ===
{top_countries.to_string()}

=== AVERAGE ORDER VALUE BY COUNTRY (TOP 10, min 10 orders) ===
{country_avg[['avg_order']].to_string()}

=== TOP 10 PRODUCTS BY REVENUE ===
{top_products.to_string()}

=== MONTHLY REVENUE (full history) ===
{monthly.to_string()}
Best month: {best_month} — £{monthly[best_month]:,.0f}
Worst month: {worst_month} — £{monthly[worst_month]:,.0f}

=== REVENUE BY DAY OF WEEK ===
{day_rev.to_string()}

=== RFM CUSTOMER SEGMENTS ===
{seg_summary.to_string()}

=== PRODUCT ASSOCIATION RULES (TOP 10 by lift) ===
{top_rules[['product_a','product_b','support','confidence','lift']].to_string()}

=== 6 MONTH REVENUE FORECAST (Jan-Jun 2012) ===
{forecast[['month','predicted_revenue']].to_string()}
Total H1 2012 forecast: £{forecast['predicted_revenue'].sum():,.0f}
ML Model R2 score: 0.707
Main prediction driver: Month of year (53%), Q4 indicator (20%), lag features (19%)

=== COHORT RETENTION SUMMARY ===
Average month-1 retention rate: ~20-25% (75-80% of new customers don't return next month)
Best cohort: December 2009 (35.3% month-1 retention)
Weakest cohorts: October-December 2010 (9-17% month-1 retention)
Pattern: Christmas-season first-time buyers have the best retention

=== KEY BUSINESS INSIGHTS ===
- Champions segment: 1,300 customers (22%) generate £12.1M (68% of revenue) — Pareto principle confirmed
- At Risk customers: 227 customers averaging £4,488 each = £1M+ at immediate risk
- Saturday orders: only 30 (vs 7,773 on Thursday) — confirms pure B2B wholesale model
- Seasonality: Revenue doubles every Sep-Nov vs Jan-Feb — business is highly Christmas-driven
- International opportunity: Netherlands (£2,430 avg order), Singapore (£2,301 avg order)
- UK dominance: 83% of revenue but lowest avg order value (£439) vs international (up to £2,430)
- Product bundling: colour variants bought as sets (party candles, Easter baskets, cutlery sets)
- Lost customers: 779 customers with avg spend of only £246 — not worth heavy win-back investment
- Potential loyalists: 443 customers with £890 avg spend — high growth potential with right nurturing
"""

    ai_context = build_ai_context()

    # ── CAPABILITY CARDS ──────────────────────────────────────
    st.markdown("### What can I help you with?")
    c1, c2, c3, c4 = st.columns(4)
    cap_style = """background:{bg}; border-radius:12px; padding:1rem;
                   border:1px solid {border}; text-align:center;"""
    c1.markdown(f"""<div style='{cap_style.format(bg="#eff6ff", border="#bfdbfe")}'>
        <div style='font-size:1.5rem'>📊</div>
        <div style='font-weight:600; color:#1e40af; font-size:0.85rem; margin-top:0.3rem'>
        Business Performance</div>
        <div style='color:#3b82f6; font-size:0.78rem; margin-top:0.2rem'>
        Revenue, orders, trends</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div style='{cap_style.format(bg="#f0fdf4", border="#bbf7d0")}'>
        <div style='font-size:1.5rem'>👥</div>
        <div style='font-weight:600; color:#166534; font-size:0.85rem; margin-top:0.3rem'>
        Customer Insights</div>
        <div style='color:#16a34a; font-size:0.78rem; margin-top:0.2rem'>
        Segments, retention, RFM</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div style='{cap_style.format(bg="#fff7ed", border="#fed7aa")}'>
        <div style='font-size:1.5rem'>🎯</div>
        <div style='font-weight:600; color:#9a3412; font-size:0.85rem; margin-top:0.3rem'>
        Strategy & Actions</div>
        <div style='color:#ea580c; font-size:0.78rem; margin-top:0.2rem'>
        Recommendations, next steps</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div style='{cap_style.format(bg="#fdf4ff", border="#e9d5ff")}'>
        <div style='font-size:1.5rem'>🔮</div>
        <div style='font-weight:600; color:#6b21a8; font-size:0.85rem; margin-top:0.3rem'>
        Forecasts & Risks</div>
        <div style='color:#7c3aed; font-size:0.78rem; margin-top:0.2rem'>
        Predictions, risk analysis</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── SUGGESTED QUESTIONS ───────────────────────────────────
    st.markdown("**💡 Quick questions to get started:**")

    suggestions = {
        "📈 Performance": [
            "Summarise the overall business performance",
            "Which month had the highest revenue and why?",
            "How has the business grown year over year?",
        ],
        "👥 Customers": [
            "Who are our most valuable customers and what makes them special?",
            "What should we do urgently about at-risk customers?",
            "How can we improve customer retention?",
        ],
        "🎯 Strategy": [
            "What are the top 3 growth opportunities for this business?",
            "Which international market should we expand into next?",
            "How can we reduce revenue seasonality?",
        ],
        "🔮 Forecast": [
            "What does the 2012 revenue forecast look like?",
            "What are the biggest risks to future revenue?",
            "Should we hire more staff for Q4 2012?",
        ]
    }

    for category, qs in suggestions.items():
        st.markdown(f"**{category}**")
        cols = st.columns(3)
        for i, q in enumerate(qs):
            if cols[i].button(q, key=f"sug_{category}_{i}", use_container_width=True):
                st.session_state['pending_question'] = q
                st.rerun()

    st.markdown("---")

    # ── CHAT HISTORY ──────────────────────────────────────────
    if 'ai_messages' not in st.session_state:
        st.session_state.ai_messages = []

    # Display chat history
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg['role'],
                             avatar='🧑‍💼' if msg['role'] == 'user' else '🤖'):
            st.markdown(msg['content'])

    # Handle pending question from suggestion buttons
    pending = st.session_state.pop('pending_question', None)

    # Chat input
    user_input = st.chat_input("Ask anything about the business...")
    active_input = pending or user_input

    if active_input:
        # Show user message
        with st.chat_message('user', avatar='🧑‍💼'):
            st.markdown(active_input)
        st.session_state.ai_messages.append({
            'role': 'user',
            'content': active_input
        })

        # Get and show AI response
        with st.chat_message('assistant', avatar='🤖'):
            with st.spinner('Analysing data...'):
                try:
                    client = OpenAI(
                        api_key=os.getenv('OPENROUTER_API_KEY'),
                        base_url='https://openrouter.ai/api/v1'
                    )
                    response = client.chat.completions.create(
                        model='google/gemini-2.0-flash-001',
                        messages=[
                            {'role': 'system', 'content': ai_context},
                            *[{'role': m['role'], 'content': m['content']}
                              for m in st.session_state.ai_messages[:-1]],
                            {'role': 'user', 'content': active_input}
                        ],
                        max_tokens=600,
                        temperature=0.3
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.ai_messages.append({
                        'role': 'assistant',
                        'content': answer
                    })
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
        st.rerun()

    # ── CLEAR CHAT ────────────────────────────────────────────
    if st.session_state.ai_messages:
        st.markdown("---")
        col1, col2 = st.columns([4, 1])
        col2.button("🗑️ Clear chat", on_click=lambda: st.session_state.update(
            {'ai_messages': []}), use_container_width=True)