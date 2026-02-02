import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V34.1 - Audio Alert", layout="wide")

# دالة التنبيه الصوتي (JavaScript)
def play_alarm():
    components.html(
        """
        <audio autoplay>
          <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
        </audio>
        """,
        height=0,
    )

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

def logic_v34_1(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "تحليل..", False
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    recent_df = data.tail(120)
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        match_count = len(recent_df[(recent_df.iloc[:, pos_map[vp]] == vt) & (recent_df.iloc[:, 8] == car)])
        scores[car] += match_count * 45.0
        total_match = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)])
        scores[car] += total_match * 2.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # رادار الغدر المطور
    traitors = ["Atv", "Moto", "Car", "Orv"]
    p3 = [v for v in current_cars if v not in [p1, p2]][0]
    is_bait = True if p3 in traitors and vt in ["potholes", "bumpy", "dirt"] else False
    
    status = "🚨 إنذار: نمط غدر مكتشف!" if is_bait else "✅ النمط يبدو آمناً"
    return p1, p2, status, is_bait

# --- الواجهة ---
st.title("🔔 مفاعل التنبيه الصوتي V34.1")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    st.metric("دقة السيطرة", f"{rate:.1f}%")

st.divider()

with st.container(border=True):
    col1 = st.columns(3)
    v1 = col1[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col1[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col1[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col2 = st.columns([1, 2])
    vp = col2[0].radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = col2[1].selectbox("الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = logic_v34_1(v1, v2, v3, vp, vt, df)
    
    if bait:
        st.error(status)
        play_alarm() # تشغيل الصوت عند وجود غدر
    else:
        st.success(status)

    res = st.columns(2)
    res[0].markdown(f"### 🥇 الأول: {p1}")
    res[1].markdown(f"### 🥈 الثاني: {p2}")

# ترحيل النتيجة
st.divider()
with st.expander("📥 ترحيل النتيجة وتحديث الداتا", expanded=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    
    c_f = st.columns(2)
    lp = c_f[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True, key="lp")
    aw = c_f[1].selectbox("من فاز فعلياً؟", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل البيانات", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {"entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3, "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1}
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
