import streamlit as st
import pandas as pd
import requests
import time

# --- إعدادات الواجهة الأصلية ---
st.set_page_config(page_title="Race Master V40.4 - Classic", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_db():
    try:
        data = pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}")
        # تنظيف الداتا من الأسطر الفارغة تماماً
        return data.dropna(subset=[data.columns[1]]) 
    except: return pd.DataFrame()

df = load_db()

# --- الهيدر الثابت (العدادات) ---
st.markdown("<h2 style='text-align: center;'>🏆 منصة الاستحواذ - الواجهة الكلاسيكية</h2>", unsafe_allow_html=True)

if not df.empty:
    total_rounds = len(df)
    st.metric("📊 إجمالي الجولات في القاعدة", f"{total_rounds} / 10,000")
    st.progress(min(total_rounds/
