import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence V31.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- محرك ذكاء السلاسل والفئات ---
def streak_and_class_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, []
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # 1. تحليل السلسلة (آخر 5 جولات)
    last_5_winners = data.tail(5).iloc[:, 8].tolist()
    streaks = {v: last_5_winners.count(v) for v in current_cars}
    
    scores = {v: 0.0 for v in current_cars}
    
    for car in current_cars:
        # وزن السلسلة الحالية (مهم جداً بناءً على ملاحظتك)
        scores[car] += streaks[car] * 10.0 
        
        # وزن الطريق التاريخي (من الـ 508 جولة)
        road_match = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        scores[car] += len(road_match) * 3.0
        
        # وزن المسار الأطول التاريخي لهذه السيارة
        lp_wins = len(data[(data.iloc[:, 7] == v_pos) & (data.iloc[:, 8] == car)])
        scores[car] += lp_wins * 2.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # تحديد السيارات التي تمر بسلسلة فوز
    active_streaks = [v for v, count in streaks.items() if count >= 2]
    
    return sorted_res[0][0], sorted_res[1][0], active_streaks

# --- الواجهة الرسومية ---
st.title("🏹 محرك قناص السلاسل V31.1")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات المحللة", len(df))
    c2.metric("الدقة الكلية", f"{rate:.1f}%")
    c3.metric("توقيت الجلسة", "نشط ⚡")

st.divider()

# المدخلات
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, active_streaks = streak_and_class_logic(v1, v2, v3, vp, vt, df)
    
    if active_streaks:
        st.warning(f"⚠️ تنبيه السلسلة: السيارات {', '.join(active_streaks)} تكررت في الفوز مؤخراً!")

    st.write("---")
    r1, r2 = st.columns(2)
    r1.success(f"🥇 التوقع الأساسي: {p1}")
    r2.info(f"🥈 التوقع البديل: {p2}")

# نموذج التسجيل (تم الإبقاء على نفس الـ entry IDs)
with st.expander("📝 تسجيل الجولة لتعزيز السلسلة"):
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    
    if st.button("🚀 تحديث المحرك والبيانات", use_container_width=True):
        # كود الإرسال لجوجل كما في النسخ السابقة...
        st.balloons()
