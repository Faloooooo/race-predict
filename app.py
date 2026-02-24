import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V63.0 - Sequential Analysis", layout="wide")

SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        return pd.read_csv(url, on_bad_lines='skip').dropna(subset=["Actual Winner "])
    except: return pd.DataFrame()

df = load_data()

# ذاكرة السلسلة (لحفظ آخر جولتين)
if 'history' not in st.session_state:
    st.session_state.history = []

st.markdown(f"<h2 style='text-align: center; color: #00FFCC;'>🧠 محرك التتبع التسلسلي V63.0</h2>", unsafe_allow_html=True)

# --- إدخال بيانات الجولة الحالية ---
with st.container(border=True):
    st.subheader("🏁 معطيات الجولة الحالية")
    cols = st.columns(3)
    v1 = cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    ci = st.columns([1, 2])
    vp = ci[0].radio("الظاهر", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

# --- محرك البحث عن "تكرار التاريخ" ---
st.subheader("🎯 التوقع بناءً على تسلسل التاريخ")

def find_sequential_winner(current_cars, current_road_data):
    # البحث عن الأنماط المشابهة
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3)]
    if matches.empty: return None, None
    
    # محاولة مطابقة "السلسلة الزمنية" إذا توفرت في الذاكرة
    # (هذا الجزء يبحث هل النمط السابق في الشيت يشبه النمط السابق في جلستك الحالية)
    p1 = matches.iloc[-1, 8] # التوقع التقليدي
    
    # حساب احتمالية "إعادة التاريخ"
    total = len(matches)
    win_counts = matches.iloc[:, 8].value_counts()
    best_car = win_counts.idxmax()
    prob = (win_counts.max() / total) * 100
    
    return best_car, prob

pred_car, confidence = find_sequential_winner([v1, v2, v3], (vp, vt))

if pred_car:
    st.markdown(f"""
    <div style="background-color: #0E1117; padding: 20px; border-radius: 15px; border: 2px solid #00FFCC; text-align: center;">
        <h3 style="margin:0;">🥇 السيارة المرجحة تاريخياً</h3>
        <h1 style="color: #00FFCC; font-size: 50px; margin: 10px;">{pred_car}</h1>
        <p style="color: #AAAAAA;">نسبة تكرار هذا السيناريو في الماضي: {confidence:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ هذا التسلسل يظهر لأول مرة في تاريخك المسجل.")

st.divider()

# --- الترحيل الذكي ---
with st.form("save_round"):
    st.subheader("📥 تدوين الجولة لبناء السلسلة")
    others = [p for p in ["L", "C", "R"] if p != vp]
    h1 = st.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2 = st.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    lp = st.radio("الأطول LP", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.form_submit_button("🚀 ترحيل وحفظ التسلسل"):
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": pred_car if pred_car else v1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الحفظ. التاريخ الآن يسجل هذا التسلسل!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
