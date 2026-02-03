import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V35.0 - 1000+ Master", layout="wide")

def play_sound(sound_type="alert"):
    urls = {
        "alert": "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3", # هادئ
        "success": "https://www.soundjay.com/buttons/button-1.mp3" # ترحيل
    }
    components.html(f"<audio autoplay><source src='{urls[sound_type]}' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

def logic_v35_0(v1, v2, v3, vp, vt, data):
    current_cars = [v1, v2, v3]
    if data.empty: return v1, v2, "تحليل..", False
    
    pos_map = {"L": 4, "C": 5, "R": 6}
    # السر هنا: نركز فقط على آخر 250 جولة لفهم "النمط الحالي" للسيرفر
    recent_df = data.tail(250)
    last_5_winners = data.tail(5).iloc[:, 8].tolist()
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن النمط الحديث (وزن ذهبي)
        m = len(recent_df[(recent_df.iloc[:, pos_map[vp]] == vt) & (recent_df.iloc[:, 8] == car)])
        scores[car] += m * 50.0
        
        # عقوبة التكرار (إذا فازت السيارة مؤخراً جداً، احتمالية فوزها الآن تقل)
        if car in last_5_winners[:2]: scores[car] -= 10.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # رادار الغدر للألف جولة
    p3 = [v for v in current_cars if v not in [p1, p2]][0]
    is_bait = True if p3 in ["Atv", "Moto", "Car"] and vt in ["potholes", "bumpy"] else False
    
    status = "🚨 فخ مكتشف!" if is_bait else "✅ نمط مستقر"
    return p1, p2, status, is_bait

# --- الواجهة ---
st.title("🚀 مفاعل الألف جولة V35.0")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid.tail(100)[valid.tail(100).iloc[:, 8] == valid.tail(100).iloc[:, 9]]) ) # دقة آخر 100 جولة
    c1, c2, c3 = st.columns(3)
    c1.metric("قوة الداتا", f"{len(df)} جولة")
    c2.metric("دقة النمط الحالي", f"{rate}%")
    c3.metric("الوضع", "تحليل ديناميكي")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    cp = st.columns([1, 2])
    vp = cp[0].radio("موقع الطريق", ["L", "C", "R"], horizontal=True)
    vt = cp[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = logic_v35_0(v1, v2, v3, vp, vt, df)
    
    if bait:
        st.error(status)
        play_sound("alert")
    else: st.success(status)

    res = st.columns(2)
    res[0].success(f"🥇 التوقع الأول: **{p1}**")
    res[1].warning(f"🥈 التوقع الثاني: **{p2}**")

st.divider()
st.subheader("📥 ترحيل النتيجة (تحديث المفاعل)")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.button("🚀 ترحيل وحفظ", use_container_width=True):
        payload = {"entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3, "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1}
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم التحديث بنجاح")
            time.sleep(1.5)
            st.cache_data.clear()
            st.rerun()
