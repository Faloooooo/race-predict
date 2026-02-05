import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# --- الروابط الرسمية ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Master V36.4", layout="wide")

# دالة الصوت الهادئ
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

# --- محرك التحليل الذكي ---
def core_logic(v1, v2, v3, vp, vt, data):
    current_cars = [v1, v2, v3]
    if data.empty: return v1, v2, "بانتظار البيانات", False
    
    pos_map = {"L": 4, "C": 5, "R": 6}
    # التركيز على آخر 50 جولة (قانون الساعة)
    fresh_df = data.tail(50)
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن مرتفع جداً للأنماط الحديثة
        f_match = len(fresh_df[(fresh_df.iloc[:, pos_map[vp]] == vt) & (fresh_df.iloc[:, 8] == car)])
        scores[car] += f_match * 100.0
        # وزن ثانوي للتاريخ
        total_match = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)])
        scores[car] += total_match * 0.5

    res_sorted = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = res_sorted[0][0], res_sorted[1][0]
    
    # كاشف الانعكاس
    last_10 = data.tail(10).iloc[:, 8].tolist()
    if last_10.count(p2) > last_10.count(p1):
        p1, p2 = p2, p1
        status = "🔄 السيرفر يعكس النمط (حالة تبديل)"
    else:
        status = "🎯 نمط حديث مستقر"

    bait = True if vt in ["bumpy", "potholes"] and ("Atv" in current_cars or "Moto" in current_cars) else False
    return p1, p2, status, bait

# --- 📊 الهيدر الثابت (عداد الجولات والنسبة) ---
st.title("🛡️ كونسول السيادة الرقمية V36.4")

if not df.empty:
    recent_eval = df.tail(30)
    acc = (len(recent_eval[recent_eval.iloc[:, 8] == recent_eval.iloc[:, 9]]) / 30) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 عداد الجولات الكلي", f"{len(df)}")
    c2.metric("📈 نسبة الربح (آخر 30 جولة)", f"{acc:.1f}%")
    c3.metric("📡 حالة المفاعل", "يعمل بكفاءة")

st.divider()

# --- 🏁 منطقة التوقع ---
with st.container(border=True):
    st.subheader("تحليل السباق الحالي")
    col_v = st.columns(3)
    v1 = col_v[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_v[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_v[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col_r = st.columns([1, 2])
    vp = col_r[0].radio("الموقع المعروف", ["L", "C", "R"], horizontal=True)
    vt = col_r[1].selectbox("طريق الموقع المعروف", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = core_logic(v1, v2, v3, vp, vt, df)
    
    if bait: play_chime()
    
    st.warning(status) if "🔄" in status else st.success(status)
    
    res = st.columns(2)
    res[0].info(f"🥇 التوقع الأول: **{p1}**")
    res[1].info(f"🥈 التوقع الثاني: **{p2}**")

st.divider()

# --- 📥 منطقة الترحيل الثابتة (لا تختفي) ---
st.subheader("ترحيل البيانات الفوري")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    
    c_extra = st.columns(2)
    lp = c_extra[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = c_extra[1].selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل وحفظ الجولة", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": r_map["L"], "entry.658789827": r_map["C"], "entry.1738752946": r_map["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تـم تـرحـيـل الـداتـا بـنـجـاح!")
            time.sleep(1.5)
            st.cache_data.clear()
            st.rerun()
