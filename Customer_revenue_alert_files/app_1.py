
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import seaborn as sns



df_pvt = pd.read_csv("simulated_df_with_level.csv", index_col=0)
month_cols = [c for c in df_pvt.columns if c != 'decline_level']

# -------- Streamlit page config ----------
st.set_page_config(layout="wide")
st.markdown("<span style='font-size:48px; font-weight:bold;'>📉 Customer Revenue Decline Alert System</span>", unsafe_allow_html=True)

#pricture. 1

st.markdown("<span style='font-size:45px'><b>Distribution of Customer Decline Levels</b></span>", unsafe_allow_html=True)
level_counts = df_pvt['decline_level'].value_counts().sort_index()

fig1, ax1 = plt.subplots(figsize=(6,4))  
bars = ax1.bar(level_counts.index, level_counts.values,
               color=['green','yellow','orange','red'], width=0.6)
ax1.set_xlabel("Decline Level", fontsize=10)
ax1.set_ylabel("Number of Customers", fontsize=10)
ax1.set_title("Customer Risk Level Distribution", fontsize=12, weight="bold")
ax1.set_xticks([0,1,2,3])
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + 3,
             f"{int(height)}", ha='center', va='bottom', fontsize=6, weight="bold")
plt.tight_layout()

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.pyplot(fig1, use_container_width=False) 


#pricture. 2
st.markdown("<span style='font-size:45px; font-weight:bold;'>📈 Revenue Trend of Selected Customer</span>", unsafe_allow_html=True)
st.markdown("<span style='font-size:38px'><b>Select Decline Level</b></span>", unsafe_allow_html=True)
sel_level = st.selectbox("", [0,1,2,3], key="sel_level")
cust_list = df_pvt[df_pvt['decline_level']==sel_level].index.astype(str).tolist()
if cust_list:
    st.markdown("<span style='font-size:38px'><b>Select Customer ID</b></span>", unsafe_allow_html=True)
    sel_cust = st.selectbox("", cust_list, key="sel_cust")

    rev = df_pvt.loc[sel_cust, month_cols]
    rev = rev[rev.notna()]

    x = np.arange(len(rev))
    y = rev.values
    slope, intercept, *_ = linregress(x, y)
    trend = intercept + slope*x
    ma3 = rev.rolling(3).mean()

    #monthly decline rate
    monthly_decline = []
    for i in range(1, len(y)):  
        if y[i-1] > 0:  
            decline_pct = ((y[i-1] - y[i]) / y[i-1]) * 100
            monthly_decline.append(decline_pct)
    avg_monthly_decline = np.mean(monthly_decline) if monthly_decline else 0

    fig2, ax2 = plt.subplots(figsize=(11,6))
    ax2.plot(rev.index, y, marker='o', label="Revenue")
    ax2.plot(rev.index, trend, linestyle='--', label="Trend Line")
    ax2.plot(rev.index, ma3, linestyle=':', label="3-mo Moving Avg")
    ax2.set_title(f"Revenue Trend – {sel_cust}", fontsize=14, weight="bold")
    ax2.set_xlabel("Month", fontsize=12); ax2.set_ylabel("Revenue", fontsize=12)
    ax2.set_xticks(np.arange(len(rev.index)))
    ax2.set_xticklabels(rev.index, rotation=45, ha='right',fontsize=10)
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.pyplot(fig2, use_container_width=True)

    # —— Business insights 
    st.markdown(
        f"""
    <div style='font-size:45px; margin-bottom:10px;'>🔎 <b>Business Insights</b></div>
    <ul style='font-size:32px; line-height:1.5;'>
    <li><b>Initial revenue:</b> £{y[0]:.0f}</li>
    <li><b>Latest revenue:</b> £{y[-1]:.0f}</li>
    <li><b>Average monthly decline speed:</b> {avg_monthly_decline:.1f}%</li>
    <li><b>Customer trend:</b> <b>{"⬇️ Consistently declining" if slope<0 else "⬆️ Growing" if slope>0 else "➖ Stable"}</b></li>
    </ul>
    </div>
        """, unsafe_allow_html=True)

else:
    st.warning("No customers found for the selected risk level.")

#pricture. 3

st.markdown("<span style='font-size:45px; font-weight:bold;'>📊 Group Revenue Trend Comparison</span>", unsafe_allow_html=True)
avg_by_level = df_pvt.groupby('decline_level')[month_cols].mean()
fig3, ax3 = plt.subplots(figsize=(11,6))
for lv in avg_by_level.index:
    ax3.plot(avg_by_level.columns, avg_by_level.loc[lv],
             label=f"Level {lv}", linewidth=2)
ax3.set_title("Average Monthly Revenue by Decline Level", fontsize=14, weight="bold")
ax3.set_xlabel("Month", fontsize=12); ax3.set_ylabel("Avg Revenue", fontsize=12)
ax3.set_xticklabels(avg_by_level.columns, rotation=45, ha='right',fontsize=10)
ax3.legend()
ax3.grid(True)
plt.tight_layout()
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.pyplot(fig3, use_container_width=True)

#pricture. 4
st.markdown("<h3 style='font-size:45px; font-weight:bold;'>🔥 Heatmap of Avg Monthly Revenue by Decline Level</h3>", unsafe_allow_html=True)
st.markdown(
"""
<div style='font-size:32px ; line-height:1.6'>
The numbers in each cell represent the **average monthly revenue (£)** for all customers within the selected decline level.  
Darker colours indicate higher revenue; lighter colours indicate lower revenue.
</small>
""", unsafe_allow_html=True)

heatmap_data = avg_by_level  
fig4, ax4 = plt.subplots(figsize=(10,6))
sns.heatmap(heatmap_data, cmap='YlOrRd', linewidths=.5,
            annot=True, fmt='.0f', ax=ax4, cbar_kws={'label':'Avg £'})
ax4.set_xlabel("Month", fontsize=10)
ax4.set_ylabel("Decline Level", fontsize=10)
plt.tight_layout()
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.pyplot(fig4, use_container_width=True)