import os, json
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
import base64

engine=create_engine("mysql+pymysql://root:paapa1105@127.0.0.1:3306/phonepe")


def run_query(query):
    with engine.connect() as con:
        return pd.read_sql(query, con=engine)



st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
st.sidebar.title("📊 PhonePe Dashboard")


background_image_url = "https://i.imgur.com/example.jpg"

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{background_image_url}");
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
}}

[data-testid="stSidebar"] > div:first-child {{
    background: rgba(255, 255, 255, 0.8);
}}

.block-container {{
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 10px;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)



page = st.sidebar.selectbox("Navigate", [
    "Home", "Transactions", "Insurance",
    "User Registrations", "Engagement & Growth", "Device Dominance"
])

years = run_query("SELECT DISTINCT Years FROM aggre_transaction ORDER BY Years")["Years"].tolist()
quarters = run_query("SELECT DISTINCT Quarter FROM aggre_transaction ORDER BY Quarter")["Quarter"].tolist()

year_filter = st.sidebar.selectbox("Year", years, index=len(years)-1)
quarter_filter = st.sidebar.selectbox("Quarter", quarters)

def render_empty_warning(df):
    if df.empty:
        st.warning("No data available for the selected Year and Quarter.")
        return True
    return False

if page == "Home":
    st.markdown("<h1>PhonePe Pulse Insights</h1>", unsafe_allow_html=True)
    with st.spinner("Loading map data..."):
        df = run_query(f"""
            SELECT States, SUM(Transaction_amount) AS TotalAmount
            FROM aggre_transaction
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY States
        """)
    if not render_empty_warning(df):
        # state mapping for GeoJSON compatibility
        state_mapping = { "andaman-&-nicobar-islands": "Andaman & Nicobar",
    "andhra-pradesh": "Andhra Pradesh",
    "arunachal-pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra-&-nagar-haveli-&-daman-&-diu": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "NCT of Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal-pradesh": "Himachal Pradesh",
    "jammu-&-kashmir": "Jammu & Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya-pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "puducherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil-nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar-pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west-bengal": "West Bengal" } 
        df = df.replace(state_mapping)

        fig = px.choropleth(
            df, geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM', locations='States', color='TotalAmount',
            color_continuous_scale='Reds'
        )
        fig.update_geos(fitbounds="locations", visible=True)
        st.plotly_chart(fig)

        st.dataframe(df)

elif page == "Transactions":
    st.markdown("<h2>Transaction Dynamics</h2>", unsafe_allow_html=True)
    with st.spinner("Loading transaction data..."):
        df = run_query(f"""
            SELECT Transaction_type,
                   SUM(Transaction_count) AS TxnCount,
                   SUM(Transaction_amount) AS TxnAmount
            FROM aggre_transaction
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY Transaction_type
        """)
    if not render_empty_warning(df):
        total_amount = df["TxnAmount"].sum()
        st.metric("Total Transaction Amount", f"₹{total_amount:,.0f}")
        fig_line = px.line(df, x="Transaction_type", y="TxnAmount", markers=True,
                           title="Transaction Amount by Type")
        fig_bar = px.bar(df, x="Transaction_type", y="TxnCount", color="Transaction_type",
                         title="Transaction Count by Type")
        st.plotly_chart(fig_line, use_container_width=True)
        st.plotly_chart(fig_bar, use_container_width=True)

elif page == "Insurance":
    st.markdown("<h2>Insurance Transactions</h2>", unsafe_allow_html=True)
    with st.spinner("Loading insurance data..."):
        df = run_query(f"""
            SELECT States, SUM(Transaction_count) AS TxnCount,
                   SUM(Transaction_amount) AS TxnAmount
            FROM aggre_insurance
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY States
        """)
    if not render_empty_warning(df):
        fig = px.bar(df, x="States", y="TxnAmount", color="TxnCount",
                     title="Insurance Amount & Count by State")
        st.plotly_chart(fig, use_container_width=True)

elif page == "User Registrations":
    st.markdown("<h2>User Registrations</h2>", unsafe_allow_html=True)
    with st.spinner("Loading registration data..."):
        df = run_query(f"""
            SELECT States, SUM(RegisteredUser) AS Users
            FROM top_user
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY States
        """)
    if not render_empty_warning(df):
        fig = px.bar(df.sort_values("Users", ascending=False), x="Users", y="States",
                     orientation="h", title="Top States by User Registrations")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Engagement & Growth":
    st.markdown("<h2>Engagement & Growth</h2>", unsafe_allow_html=True)
    with st.spinner("Loading engagement data..."):
        df = run_query(f"""
            SELECT States, SUM(RegisteredUser) AS Users,
                   SUM(AppOpens) AS Opens
            FROM map_user
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY States
        """)
    if not render_empty_warning(df):
        fig = px.scatter(df, x="Users", y="Opens", color="States", size="Users",
                         title="User Engagement (App Opens vs Registrations)")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Device Dominance":
    st.markdown("<h2>Device Dominance</h2>", unsafe_allow_html=True)
    with st.spinner("Loading device data..."):
        df = run_query(f"""
            SELECT Brands, SUM(Transaction_count) AS Users
            FROM aggre_user
            WHERE Years={year_filter} AND Quarter={quarter_filter}
            GROUP BY Brands
        """)
    if not render_empty_warning(df):
        fig_pie = px.pie(df, values="Users", names="Brands", hole=0.4,
                         title="Market Share by Device Brands")
        fig_line = px.line(df, x="Brands", y="Users", markers=True,
                           title="Device-wise User Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
        st.plotly_chart(fig_line, use_container_width=True)

