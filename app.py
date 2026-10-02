import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Restaurant Sales Analysis", layout="wide")
st.title("Restaurant Sales Analysis Dashboard")

DATASET_PATH = Path(__file__).resolve().parents[1] / "9. Sales-Data-Analysis.csv"

if not DATASET_PATH.exists():
    st.error(f"Dataset not found at {DATASET_PATH}")
    st.stop()

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df["Revenue"] = df["Price"] * df["Quantity"]
    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year
    df["Day"] = df["Date"].dt.day_name()
    df = df.drop_duplicates().reset_index(drop=True)
    return df


df = load_data(str(DATASET_PATH))

with st.sidebar:
    st.header("Filters")
    selected_city = st.multiselect("City", options=sorted(df["City"].dropna().unique().tolist()))
    selected_product = st.multiselect("Product", options=sorted(df["Product"].dropna().unique().tolist()))
    selected_year = st.multiselect("Year", options=sorted(df["Year"].dropna().astype(int).unique().tolist()))

    if selected_city:
        df = df[df["City"].isin(selected_city)]
    if selected_product:
        df = df[df["Product"].isin(selected_product)]
    if selected_year:
        df = df[df["Year"].isin(selected_year)]

st.subheader("Dataset Preview")
st.dataframe(df.head())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${df['Revenue'].sum():,.2f}")
col2.metric("Total Orders", f"{df['Order ID'].nunique()}")
col3.metric("Average Order Value", f"${df['Revenue'].mean():,.2f}")
col4.metric("Cities Covered", f"{df['City'].nunique()}")

st.subheader("Sales Trend")
monthly = df.groupby("Month")["Revenue"].sum().reset_index()
fig_line = px.line(monthly, x="Month", y="Revenue", title="Monthly Revenue")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Top Selling Products")
product_sales = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False).reset_index()
fig_bar = px.bar(product_sales.head(10), x="Product", y="Revenue", title="Revenue by Product")
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("City Analysis")
city_sales = df.groupby("City")["Revenue"].sum().sort_values(ascending=False).reset_index()
fig_city = px.bar(city_sales, x="City", y="Revenue", title="Revenue by City")
st.plotly_chart(fig_city, use_container_width=True)

st.subheader("Insights")
st.write("- Revenue is driven by the highest-volume products and cities.")
st.write("- The dashboard can be extended with customer segmentation and monthly forecasting.")
