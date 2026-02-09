import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V40.2 - Anti-Gap", layout="wide")

# الروابط
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_data()

# --- واجهة الإدخال المحسنة ---
st.title("🛡️ إصدار المزامنة الكاملة V40.2")
st.info(f"إجمالي الجولات المسجلة حالياً: {len(df)}")

with st.container(border=True):
    col_cars = st.columns(3)
    v1 = col_cars[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = col_cars[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = col_cars[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    col_road = st.columns(3)
    rl = col_road[0].selectbox("طريق L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='rl')
    rc = col_road[1].selectbox("طريق C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], index=1, key='rc')
    rr = col_road[2].selectbox("طريق R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], index=2, key='rr')
    
    col_fin = st.columns(2)
    lp = col_fin[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = col_fin[1].selectbox("الفائز الفعلي", [v1, v2, v3])

    if st.button("🚀 ترحيل وحفظ (بدون فراغات)", use_container_width=True):
        # تجميع البيانات بدقة متناهية
        payload = {
            "entry.159051415": str(v1),
            "entry.1682422047": str(v2),
            "entry.918899545": str(v3),
            "entry.401576858": str(rl), # التأكد من إرسال الطرق يدوياً
            "entry.658789827": str(rc),
            "entry.1738752946": str(rr),
            "entry.1719787271": str(lp),
            "entry.1625798960": str(aw)
        }
        
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                st.balloons()
                st.success("✅ تم الإرسال بنجاح! العلامة الخضراء: الداتا كاملة.")
                time.sleep(2) # مهلة لضمان وصول البيانات للسيرفر
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"خطأ في السيرفر: {response.status_code}")
        except Exception as e:
            st.error(f"فشل الاتصال: {e}")
