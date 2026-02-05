import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# --- إعدادات الصفحة الصارمة ---
st.set_page_config(page_title="Race Master V36.7", layout="wide")

# الروابط
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

# صوت التنبيه
def play_sound():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def load_db():
    try:
        data = pd.read_csv(f"{SHEET_READ_URL}&cache_buster={time.time()}")
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_db()

# --- المحرك الصامت (لا يطبع أي نص) ---
def get_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "جاري المزامنة..", False
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
        msg = "🔄 تحذير: السيرفر يعكس الأنماط"
    else: msg = "🎯 النمط مستقر"
    
    bait = True if vt in ["bumpy", "potholes"] and ("Atv" in cars or "Moto" in cars) else False
    return p1, p2, msg, bait

# --- بناء الواجهة (UI) ---
st.title("🏆 نظام التحليل الاحترافي V36.7")

# القسم 1: العدادات (ثابتة في الأعلى)
if not df.empty:
    r_30 = df.tail(30)
    acc = (len(r_30[r_30.iloc[:, 8] == r_30.iloc[:, 9]]) / 30) * 100
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 عداد الجولات", len(df))
    m2.metric("📈 الدقة الحالية", f"{acc:.1f}%")
    m3.metric("🟢 المفاعل", "نشط")

st.divider()

# القسم 2: منطقة المدخلات والتوقع (محمية داخل Container)
with st.container(border=True):
    st.subheader("📍 مدخلات السباق الحالي")
    c_cars = st.columns(3)
    v1 = c_cars[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c_cars[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c_cars[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    c_info = st.columns([1, 2])
    vp = c_info[0].radio("الموقع", ["L", "C", "R"], horizontal=True)
    vt = c_info[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # استدعاء المنطق
    p1, p2, status, bait = get_logic(v1, v2, v3, vp, vt, df)
    
    if bait: play_sound()

    # عرض النتيجة بوضوح منعاً لظهور الكود
    st.info(status)
    res_cols = st.columns(2)
    res_cols[0].success(f"🥇 الأول: {p1}")
    res_cols[1].warning(f"🥈 الثاني: {p2}")

st.divider()

# القسم 3: الترحيل (ثابت في الأسفل)
st.subheader("📥 ترحيل النتيجة")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_cols = st.columns(2)
    h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_cols = st.columns(2)
    lp = f_cols[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True)
    aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3], key='aw')
    
    if st.button("🚀 ترحيل فوري", use_container_width=True):
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الحفظ وتحديث العدادات!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
