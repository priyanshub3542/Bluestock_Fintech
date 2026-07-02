import streamlit as st
import pandas as pd
import numpy as np
import scipy.optimize as sco
import plotly.express as px
import os

# Page config
st.set_page_config(page_title="Bluestock MF Dashboard", page_icon="📈", layout="wide")

# Custom CSS for Premium UI
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
        color: rgb(30, 103, 119);
        overflow-wrap: break-word;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Bluestock Mutual Fund Analytics")
st.markdown("Interactive, high-performance dashboard for tracking AUM, SIP inflows, and advanced fund analytics.")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = os.path.join(base_dir, "data", "processed")
    aum = pd.read_csv(os.path.join(proc, "03_aum_by_fund_house.csv"))
    sip = pd.read_csv(os.path.join(proc, "04_monthly_sip_inflows.csv"))
    perf = pd.read_csv(os.path.join(proc, "07_scheme_performance.csv"))
    nav = pd.read_csv(os.path.join(proc, "02_nav_history.csv"), parse_dates=['date'])
    fund_master = pd.read_csv(os.path.join(proc, "01_fund_master.csv"))
    return aum, sip, perf, nav, fund_master

try:
    aum_df, sip_df, perf_df, nav_df, fund_master = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure you are running this from the project root.")
    st.stop()

# ---------------------------------------------------------
# Sidebar Slicers
# ---------------------------------------------------------
st.sidebar.header("Interactive Filters")

all_amcs = ["All"] + list(perf_df['fund_house'].unique())
selected_amc = st.sidebar.selectbox("Select Fund House (AMC):", options=all_amcs, index=0)

selected_category = st.sidebar.multiselect("Filter by Category:", options=perf_df['category'].unique(), default=perf_df['category'].unique())
selected_risk = st.sidebar.multiselect("Filter by Risk Grade:", options=perf_df['risk_grade'].unique(), default=perf_df['risk_grade'].unique())

min_return = float(perf_df['return_3yr_pct'].min())
max_return = float(perf_df['return_3yr_pct'].max())
return_range = st.sidebar.slider("3Yr Return Range (%)", min_value=min_return, max_value=max_return, value=(min_return, max_return))

min_exp = float(perf_df['expense_ratio_pct'].min())
max_exp = float(perf_df['expense_ratio_pct'].max())
exp_range = st.sidebar.slider("Expense Ratio Range (%)", min_value=min_exp, max_value=max_exp, value=(min_exp, max_exp))

filtered_perf = perf_df[
    (perf_df['category'].isin(selected_category)) & 
    (perf_df['risk_grade'].isin(selected_risk)) &
    (perf_df['return_3yr_pct'] >= return_range[0]) & 
    (perf_df['return_3yr_pct'] <= return_range[1]) &
    (perf_df['expense_ratio_pct'] >= exp_range[0]) & 
    (perf_df['expense_ratio_pct'] <= exp_range[1])
]

if selected_amc != "All":
    filtered_perf = filtered_perf[filtered_perf['fund_house'] == selected_amc]

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total AMC AUM", f"₹{aum_df['aum_lakh_crore'].sum():.1f} L Cr")
col2.metric("Total SIP Inflows", f"₹{sip_df['sip_inflow_crore'].sum():,.0f} Cr")
col3.metric("Schemes Tracked (Filtered)", f"{len(filtered_perf)}")

avg_return = filtered_perf['return_3yr_pct'].mean()
benchmark = 10.0
delta_val = avg_return - benchmark if pd.notnull(avg_return) else 0
col4.metric(
    "Avg 3Yr Return", 
    f"{avg_return:.1f}%" if pd.notnull(avg_return) else "N/A",
    f"{delta_val:.1f}% vs Benchmark" if pd.notnull(avg_return) else None
)

st.markdown("---")

# ---------------------------------------------------------
# Tabbed Layout
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Fund Performance", "🏦 AUM Overview", "📈 SIP Trends", "🤖 Fund Recommender", "🧮 Portfolio Optimizer"
])

# TAB 1: Fund Performance
with tab1:
    st.subheader("Fund Risk vs Return Scatter")
    if not filtered_perf.empty:
        fig_scatter = px.scatter(
            filtered_perf, x='std_dev_ann_pct', y='return_3yr_pct', 
            color='category', size='expense_ratio_pct', hover_name='scheme_name',
            title="3Yr Return vs Standard Deviation",
            labels={'std_dev_ann_pct': 'Risk (Std Dev)', 'return_3yr_pct': '3Yr Return %'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.markdown("### Filtered Fund Data Grid")
        display_df = filtered_perf[['scheme_name', 'fund_house', 'category', 'risk_grade', 'return_3yr_pct', 'expense_ratio_pct', 'sharpe_ratio']].sort_values('sharpe_ratio', ascending=False)
        st.dataframe(
            display_df,
            column_config={
                "scheme_name": st.column_config.TextColumn("Scheme Name", width="large"),
                "fund_house": st.column_config.TextColumn("Fund House", width="medium"),
                "category": st.column_config.TextColumn("Category"),
                "risk_grade": st.column_config.TextColumn("Risk Grade"),
                "return_3yr_pct": st.column_config.ProgressColumn("3Yr Return (%)", format="%.1f%%", min_value=0, max_value=max_return),
                "expense_ratio_pct": st.column_config.ProgressColumn("Expense Ratio (%)", format="%.2f%%", min_value=0, max_value=max_exp),
                "sharpe_ratio": st.column_config.NumberColumn("Sharpe Ratio", format="%.2f")
            },
            use_container_width=True, hide_index=True
        )
        with st.expander("🛠️ Advanced Data Operations"):
            st.download_button("⬇️ Download Filtered Data as CSV", data=filtered_perf.to_csv(index=False).encode('utf-8'), file_name='filtered_fund_performance.csv', mime='text/csv')
    else:
        st.warning("No funds match the current filter criteria.")

# TAB 2: AUM Overview
with tab2:
    col_t1, col_t2 = st.columns([1, 4])
    with col_t1:
        aum_chart_type = st.radio("AUM View Type:", ["Bar Chart", "Treemap", "Pie Chart"])
    with col_t2:
        latest_aum = aum_df.groupby('fund_house')['aum_lakh_crore'].sum().reset_index()
        if aum_chart_type == "Bar Chart":
            fig_aum = px.bar(latest_aum.sort_values('aum_lakh_crore', ascending=False), x='fund_house', y='aum_lakh_crore', color='fund_house', title="Total AUM (Lakh Crore)")
        elif aum_chart_type == "Treemap":
            fig_aum = px.treemap(latest_aum, path=['fund_house'], values='aum_lakh_crore', color='fund_house', title="AUM Market Share (Treemap)")
        else:
            fig_aum = px.pie(latest_aum, names='fund_house', values='aum_lakh_crore', title="AUM Market Share (Pie)")
        st.plotly_chart(fig_aum, use_container_width=True)

# TAB 3: SIP Trends & Forecasting
with tab3:
    col_s1, col_s2 = st.columns([1, 4])
    with col_s1:
        sip_chart_type = st.radio("SIP Trend View Type:", ["Line Chart (with Forecast)", "Bar Chart"])
    with col_s2:
        sip_df['month'] = pd.to_datetime(sip_df['month'])
        sip_sorted = sip_df.sort_values('month')
        
        if sip_chart_type == "Line Chart (with Forecast)":
            fig_sip = px.line(sip_sorted, x='month', y='sip_inflow_crore', title="SIP Inflows Over Time (Crores) with 12-Month Forecast", markers=True)
            
            # Simple Linear Forecast
            x = np.arange(len(sip_sorted))
            y = sip_sorted['sip_inflow_crore'].values
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            future_x = np.arange(len(sip_sorted), len(sip_sorted) + 12)
            future_y = p(future_x)
            
            last_date = sip_sorted['month'].iloc[-1]
            future_dates = pd.date_range(start=last_date, periods=13, freq='ME')[1:]
            
            fig_sip.add_scatter(x=future_dates, y=future_y, mode='lines', line=dict(dash='dash', color='red'), name='12-Month Forecast')
        else:
            fig_sip = px.bar(sip_sorted, x='month', y='sip_inflow_crore', title="SIP Inflows Over Time (Crores)", color='sip_inflow_crore')
        st.plotly_chart(fig_sip, use_container_width=True)

# TAB 4: AI Fund Recommender
with tab4:
    st.subheader("🤖 AI Fund Recommender")
    st.markdown("Acts as a Robo-Advisor by analyzing your risk profile and recommending the top 3 optimal mutual funds based on the Sharpe Ratio.")
    
    risk_appetite = st.radio("Select your Risk Appetite:", ["Low", "Moderate", "High"], horizontal=True)
    if risk_appetite == 'Low': target_grades = ['Low']
    elif risk_appetite == 'Moderate': target_grades = ['Moderate', 'Moderately High']
    else: target_grades = ['High', 'Very High']
    
    rec_funds = perf_df[perf_df['risk_grade'].isin(target_grades)].sort_values('sharpe_ratio', ascending=False).head(3)
    
    if not rec_funds.empty:
        rcols = st.columns(3)
        for i, (col, (_, row)) in enumerate(zip(rcols, rec_funds.iterrows())):
            with col:
                st.info(f"**Top Choice {i+1}**")
                st.markdown(f"#### {row['scheme_name']}")
                st.metric("Sharpe Ratio (Risk-Adjusted Return)", f"{row['sharpe_ratio']:.2f}")
                st.metric("3-Year Return", f"{row['return_3yr_pct']}%")
                st.caption(f"Category: {row['category']} | Expense: {row['expense_ratio_pct']}%")
    else:
        st.warning("No funds found matching this risk profile.")

# TAB 5: Markowitz Optimizer
with tab5:
    st.subheader("🧮 Markowitz Portfolio Optimizer")
    st.markdown("Uses the `scipy.optimize` SLSQP minimization algorithm to calculate the mathematically optimal capital allocation (Efficient Frontier) across a basket of top funds.")
    
    if st.button("Run Optimization Engine"):
        with st.spinner("Calculating Covariance Matrix and running SLSQP minimization..."):
            target_amfis = [119551, 120503, 118632, 119092, 120841]
            df_nav = nav_df[nav_df['amfi_code'].isin(target_amfis)].pivot(index='date', columns='amfi_code', values='nav').dropna()
            
            returns = df_nav.pct_change().dropna()
            num_assets = len(returns.columns)
            mean_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252
            risk_free_rate = 0.065
            
            def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
                ret = np.sum(mean_returns * weights)
                std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return std, ret
                
            def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
                p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
                return - (p_ret - risk_free_rate) / p_var
                
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0.0, 1.0) for asset in range(num_assets))
            
            result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=(mean_returns, cov_matrix, risk_free_rate), method='SLSQP', bounds=bounds, constraints=constraints)
            sdp, rp = portfolio_annualised_performance(result.x, mean_returns, cov_matrix)
            
            amfi_to_name = dict(zip(fund_master['amfi_code'], fund_master['scheme_name']))
            allocations = [{"Fund": amfi_to_name.get(amfi, str(amfi)), "Weight": weight * 100} for amfi, weight in zip(df_nav.columns, result.x) if weight > 0.01]
            alloc_df = pd.DataFrame(allocations)
            
            o1, o2 = st.columns([1, 2])
            with o1:
                st.success("Optimization Complete!")
                st.metric("Expected Annual Return", f"{rp*100:.2f}%")
                st.metric("Portfolio Volatility (Risk)", f"{sdp*100:.2f}%")
                st.metric("Optimal Sharpe Ratio", f"{(rp - risk_free_rate)/sdp:.2f}")
            with o2:
                fig_opt = px.pie(alloc_df, names='Fund', values='Weight', title="Optimal Capital Allocation (Max Sharpe)", hole=0.4)
                fig_opt.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_opt, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.success("✅ Advanced Analytics Module Active")
