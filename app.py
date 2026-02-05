import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="Race Master V36.8", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

def play_sound():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def load_db():
    try:
        data = pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}")
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_db()

# --- المحرك الذكي مع خاصية التجاهل ---
def get_logic(v1, v2, v3, vp, vt, data, emergency_mode):
    if data.empty: return v1, v2, "تحميل..", False
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # إذا تم تفعيل الطوارئ، نركز فقط على آخر 30 جولة
    limit = 30 if emergency_mode else 70
    recent = data.tail(limit)
    
    scores = {v: 0.0 for v in cars}
    for c in cars:
        scores[c] += len(recent[(recent.iloc[:, pos_map[vp]] == vt) & (recent.iloc[:, 8] == c)]) * 100
        if not emergency_mode:
            scores[c] += len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)]) * 0.5

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # كاشف الانعكاس
    last_15 = data.tail(15).iloc[:, 8].tolist()
    if last_15.count(p2) > last_15.count(p1):
        p1, p2 = p2, p1
        msg = "🔄 وضع التبديل نشط (عكس التوقعات)"
    else: msg = "🎯 نمط مستقر"
    
    bait = True if vt in ["bumpy", "potholes"] and ("Atv" in cars or "Moto" in cars) else False
    return p1, p2, msg, bait

# --- الواجهة ---
st.title("🏆 منصة التحكم V36.8")

# 1. العدادات والزر السحري
if not df.empty:
    r_30 = df.tail(30)
    acc = (len(r_30[r_30.iloc[:, 8] == r_30.iloc[:, 9]]) / 30) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 عداد الجولات", len(df))
    c2.metric("📈 الدقة (آخر 30)", f"{acc:.1f}%")
    
    with c3:
        emergency = st.toggle("🚨 وضع النمط الطارئ (تجاهل التاريخ)", value=False)
        if emergency: st.caption("⚠️ المفاعل يركز على اللحظة الحالية فقط")

st.divider()

# 2. منطقة التوقع
with st.container(border=True):
    st.subheader("🏁 تحليل الجولة")
    cv = st.columns(3)
    v1 = cv[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = cv[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = cv[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    ci = st.columns([1, 2])
    vp = ci[0].radio("الموقع المعروف", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("الطريق المعروف", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = get_logic(v1, v2, v3, vp, vt, df, emergency)
    if bait: play_sound()

    st.info(status)
    res_c = st.columns(2)
    res_c[0].success(f"🥇 التوقع الأول: {p1}")
    res_c[1].warning(f"🥈 التوقع الثاني: {p2}")

st.divider()

# 3. ترحيل الداتا (ثابت ومفتوح)
st.subheader("📥 ترحيل البيانات")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    hc = st.columns(2)
    h1 = hc[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = hc[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    fc = st.columns(2)
    lp = fc[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True)
    aw = fc[1].selectbox("الفائز الفعلي", [v1, v2, v3], key='aw')
    
    if st.button("🚀 ترحيل وحفظ", use_container_width=True):
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تـم الـتـرحـيـل بـنـجـاح!")
            time.sleep(1.2)
            st.cache_data.clear()
            st.rerun()
