import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# --- إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="Race Master V36.5", layout="wide", initial_sidebar_state="collapsed")

# روابط البيانات (ثابتة)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

# وظيفة الصوت
def play_beep():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}")
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = load_data()

# --- محرك التحليل الديناميكي ---
def get_prediction(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "جاري التحميل..", False
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # التركيز على آخر 60 جولة فقط (النمط الحي)
    recent = data.tail(60)
    scores = {v: 0.0 for v in cars}
    
    for c in cars:
        # وزن النمط الحديث
        scores[c] += len(recent[(recent.iloc[:, pos_map[vp]] == vt) & (recent.iloc[:, 8] == c)]) * 100
        # وزن التاريخ العام
        scores[c] += len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)]) * 0.5

    sorted_cars = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_cars[0][0], sorted_cars[1][0]
    
    # فحص حالة "التبديل العكسي"
    last_winners = data.tail(12).iloc[:, 8].tolist()
    if last_winners.count(p2) > last_winners.count(p1):
        p1, p2 = p2, p1
        msg = "🔄 تحذير: السيرفر يعكس التوقعات الآن"
    else: msg = "🎯 النمط مستقر"
    
    is_bait = True if vt in ["bumpy", "potholes"] and ("Atv" in cars or "Moto" in cars) else False
    return p1, p2, msg, is_bait

# --- الواجهة الرسومية (UI) ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🏆 رادار السباق الذكي V36.5</h1>", unsafe_allow_allow_html=True)

# 1. شريط الإحصائيات الثابت
if not df.empty:
    recent_30 = df.tail(30)
    accuracy = (len(recent_30[recent_30.iloc[:, 8] == recent_30.iloc[:, 9]]) / 30) * 100
    st.divider()
    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("📊 إجمالي الجولات", len(df))
    stat2.metric("📈 الدقة (آخر 30)", f"{accuracy:.1f}%")
    stat3.metric("🟢 الحالة", "مباشر")

st.divider()

# 2. منطقة إدخال السباق
with st.container(border=True):
    st.subheader("📍 بيانات السباق الحالي")
    c1, c2, c3 = st.columns(3)
    v1 = c1.selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='l')
    v2 = c2.selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='c')
    v3 = c3.selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='r')
    
    cx, cy = st.columns([1, 2])
    vp = cx.radio("موقع الطريق المعروف", ["L", "C", "R"], horizontal=True)
    vt = cy.selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status_msg, bait = get_prediction(v1, v2, v3, vp, vt, df)
    
    if bait: play_beep()
    
    st.info(status_msg)
    res_l, res_r = st.columns(2)
    res_l.success(f"🥇 التوقع الأول: {p1}")
    res_r.warning(f"🥈 التوقع الثاني: {p2}")

st.divider()

# 3. خانات الترحيل الثابتة (التغذية)
st.subheader("📥 ترحيل النتيجة لتحديث المفاعل")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.button("🚀 ترحيل وحفظ البيانات", use_container_width=True):
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الحفظ بنجاح! جاري تحديث الأوزان...")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
