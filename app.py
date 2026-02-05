import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="Race Master V36.6", layout="wide")

# روابط البيانات
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

# وظيفة التنبيه الصوتي
def play_chime():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = load_data()

# --- المحرك الذكي ---
def core_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "جاري التحميل..", False
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    recent = data.tail(60)
    
    scores = {v: 0.0 for v in cars}
    for c in cars:
        scores[c] += len(recent[(recent.iloc[:, pos_map[vp]] == vt) & (recent.iloc[:, 8] == c)]) * 100
        scores[c] += len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)]) * 0.5

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    last_12 = data.tail(12).iloc[:, 8].tolist()
    if last_12.count(p2) > last_12.count(p1):
        p1, p2 = p2, p1
        status = "🔄 نمط عكسي اكتشفه الرادار"
    else: status = "🎯 نمط مستقر"
    
    is_bait = True if vt in ["bumpy", "potholes"] and ("Atv" in cars or "Moto" in cars) else False
    return p1, p2, status, is_bait

# --- الواجهة الثابتة ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🏆 رادار السباق الذكي V36.6</h1>", unsafe_allow_html=True)

# 1. عداد الجولات والنسبة (ثابت في الأعلى)
if not df.empty:
    recent_eval = df.tail(30)
    acc = (len(recent_eval[recent_eval.iloc[:, 8] == recent_eval.iloc[:, 9]]) / 30) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 إجمالي الجولات", f"{len(df)}")
    c2.metric("📈 نسبة الربح (آخر 30)", f"{acc:.1f}%")
    c3.metric("📡 حالة السيرفر", "متصل ومستقر")

st.divider()

# 2. منطقة التوقع
with st.container(border=True):
    st.subheader("🏁 بيانات الجولة الحالية")
    col_cars = st.columns(3)
    v1 = col_cars[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='l')
    v2 = col_cars[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='c')
    v3 = col_cars[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='r')
    
    col_road = st.columns([1, 2])
    vp = col_road[0].radio("الموقع المعروف", ["L", "C", "R"], horizontal=True)
    vt = col_road[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status_msg, bait = core_logic(v1, v2, v3, vp, vt, df)
    if bait: play_chime()

    st.warning(status_msg) if "🔄" in status_msg else st.success(status_msg)
    
    res_col = st.columns(2)
    res_col[0].info(f"🥇 التوقع الأول: **{p1}**")
    res_col[1].info(f"🥈 التوقع الثاني: **{p2}**")

st.divider()

# 3. خانات الترحيل (ثابتة في الأسفل)
st.subheader("📥 ترحيل النتيجة (تحديث فوري)")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.button("🚀 ترحيل البيانات الآن", use_container_width=True):
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تـم تـرحـيـل الـداتـا بـنـجـاح!")
            time.sleep(1.5)
            st.cache_data.clear()
            st.rerun()
