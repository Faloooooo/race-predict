import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# الروابط الرسمية (لا تتغير)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V36.2 - Fixed Console", layout="wide")

# نغمة التنبيه الهادئة
def play_chime():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك التحليل ---
def logic_v36_2(v1, v2, v3, vp, vt, data):
    current_cars = [v1, v2, v3]
    if data.empty: return v1, v2, "بانتظار البيانات..", False
    
    pos_map = {"L": 4, "C": 5, "R": 6}
    recent_df = data.tail(70) # الاعتماد على الذاكرة القصيرة لكسر النحس
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        match = len(recent_df[(recent_df.iloc[:, pos_map[vp]] == vt) & (recent_df.iloc[:, 8] == car)])
        scores[car] += match * 100.0
        total = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)])
        scores[car] += total * 1.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # كاشف النمط العكسي
    last_15 = data.tail(15).iloc[:, 8].tolist()
    if last_15.count(p2) > last_15.count(p1):
        p1, p2 = p2, p1
        status = "🔄 نمط عكسي نشط"
    else:
        status = "🎯 نمط طبيعي"

    is_bait = True if vt in ["bumpy", "potholes"] and ("Atv" in current_cars or "Moto" in current_cars) else False
    return p1, p2, status, is_bait

# --- عرض الإحصائيات (ثابت في الأعلى) ---
st.title("🏆 منصة السباق الاحترافية V36.2")

if not df.empty:
    recent_eval = df.tail(30)
    acc = (len(recent_eval[recent_eval.iloc[:, 8] == recent_eval.iloc[:, 9]]) / 30) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 عداد الجولات", f"{len(df)}")
    c2.metric("📈 نسبة الربح (آخر 30)", f"{acc:.1f}%")
    c3.metric("📡 حالة السيرفر", "متصل")

st.divider()

# --- مدخلات التوقع ---
with st.container(border=True):
    st.subheader("🏁 1. مدخلات الجولة الحالية")
    col1 = st.columns(3)
    v1 = col1[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col1[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col1[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col2 = st.columns([1, 2])
    vp = col2[0].radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = col2[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = logic_v36_2(v1, v2, v3, vp, vt, df)
    
    if bait: play_chime()
    
    res = st.columns(2)
    res[0].success(f"🥇 الخيار الأول: {p1}")
    res[1].warning(f"🥈 الخيار الثاني: {p2}")
    st.caption(f"الحالة: {status}")

st.divider()

# --- خانات ترحيل الداتا (ثابتة ومفتوحة) ---
st.subheader("📥 2. خانات ترحيل الداتا (التغذية)")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    
    c_f = st.columns(2)
    lp = c_f[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = c_f[1].selectbox("الفائز الفعلي في الجولة", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل البيانات الآن (حفظ واستمرار)", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": r_map["L"], "entry.658789827": r_map["C"], "entry.1738752946": r_map["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تـم تـرحـيـل الـداتـا بـنـجـاح!") # العلامة الخضراء المطلوبة
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("فشل الاتصال، يرجى المحاولة مرة أخرى.")
