import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# --- الإعدادات اللوجستية ---
st.set_page_config(page_title="Race Master V40.0 - Big Data", layout="wide")
GOAL = 10000
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_massive_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url)
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_massive_db()

# --- محرك التحليل فائق السرعة ---
def heavy_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "جاري المزامنة..", 0, False
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # فلترة المواقف المشابهة بدقة
    matches = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 1:4].isin(cars).all(axis=1))]
    
    scores = {v: 0.0 for v in cars}
    for c in cars:
        # وزن الأنماط التاريخية العميقة
        total_hits = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)])
        scores[c] += total_hits * 0.5
        # وزن الأنماط الحديثة جداً (آخر 100 جولة)
        recent_hits = len(data.tail(100)[(data.tail(100).iloc[:, pos_map[vp]] == vt) & (data.tail(100).iloc[:, 8] == c)])
        scores[c] += recent_hits * 50.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # حساب قوة النمط (كم مرة تكرر هذا الموقف؟)
    pattern_strength = len(matches)
    
    # كاشف الانعكاس
    last_15 = data.tail(15).iloc[:, 8].tolist()
    if last_15.count(p2) > last_15.count(p1):
        p1, p2 = p2, p1
        msg = "🔄 تحذير: السيرفر يتبع النمط العكسي حالياً"
    else: msg = "🎯 النمط التاريخي مستقر"
    
    bait = True if vt in ["bumpy", "potholes"] and ("Atv" in cars or "Moto" in cars) else False
    return p1, p2, msg, pattern_strength, bait

# --- واجهة المستخدم ---
st.markdown(f"<h1 style='text-align: center;'>👑 طريق العشرة آلاف V40.0</h1>", unsafe_allow_html=True)

if not df.empty:
    total = len(df)
    progress = min(total / GOAL, 1.0)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"📊 التقدم الحالي: **{total}** جولة")
        st.progress(progress)
    with col2:
        st.metric("باقي للهدف", f"{GOAL - total}")

st.divider()

# منطقة التوقعات
with st.container(border=True):
    st.subheader("🏁 مدخلات السباق")
    c_cars = st.columns(3)
    v1 = c_cars[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c_cars[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c_cars[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    c_info = st.columns([1, 2])
    vp = c_info[0].radio("الموقع", ["L", "C", "R"], horizontal=True)
    vt = c_info[1].selectbox("الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, strength, bait = heavy_logic(v1, v2, v3, vp, vt, df)
    
    st.info(f"{status} | 🧩 تكرار النمط تاريخياً: {strength} مرات")
    
    res = st.columns(2)
    res[0].success(f"🥇 المقترح الأول: {p1}")
    res[1].warning(f"🥈 المقترح الثاني: {p2}")

st.divider()

# منطقة الترحيل
st.subheader("📥 ترحيل الداتا")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_cols = st.columns(2)
    h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_cols = st.columns(2)
    lp = f_cols[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.button("🚀 ترحيل وحفظ", use_container_width=True):
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الترحيل بنجاح!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
