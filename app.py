import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V36.0 - Reset Edition", layout="wide")

def play_alert():
    components.html("<audio autoplay><source src='https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3' type='audio/mpeg'></audio>", height=0)

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

def logic_v36_0(v1, v2, v3, vp, vt, data):
    current_cars = [v1, v2, v3]
    if data.empty: return v1, v2, "إعادة ضبط..", False
    
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # السر هنا: الفلترة القاسية (آخر 70 جولة فقط لفهم "مزاج" السيرفر الآن)
    fresh_data = data.tail(70)
    old_data = data.iloc[:-70]
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن ذهبي للبيانات الحديثة جداً
        fresh_wins = len(fresh_data[(fresh_data.iloc[:, pos_map[vp]] == vt) & (fresh_data.iloc[:, 8] == car)])
        scores[car] += fresh_wins * 100.0 
        
        # وزن ضئيل للبيانات القديمة لعدم التضليل
        old_wins = len(old_data[(old_data.iloc[:, pos_map[vp]] == vt) & (old_data.iloc[:, 8] == car)])
        scores[car] += old_wins * 1.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    # فحص "الانعطاف": هل p2 فاز مؤخراً أكثر من p1؟
    last_10 = data.tail(10).iloc[:, 8].tolist()
    if last_10.count(p2) > last_10.count(p1):
        p1, p2 = p2, p1 # تبديل تكتيكي لإنقاذ الجولة
        status = "🔄 تم التبديل: النمط الحالي يفضل الخيار الثاني"
    else:
        status = "🎯 نمط حديث مستقر"

    is_bait = True if vt in ["bumpy", "potholes"] and ("Atv" in current_cars or "Moto" in current_cars) else False
    return p1, p2, status, is_bait

# --- الواجهة ---
st.title("⚖️ كونسول إعادة الضبط V36.0")

if not df.empty:
    # حساب الدقة لآخر 30 جولة فقط (المقياس الحقيقي الحالي)
    recent_eval = df.tail(30)
    acc = (len(recent_eval[recent_eval.iloc[:, 8] == recent_eval.iloc[:, 9]]) / 30) * 100
    st.metric("دقة الذاكرة القصيرة (آخر 30 جولة)", f"{acc:.1f}%", delta="تنبيه: الخوارزمية تغيرت")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    cp = st.columns([1, 2])
    vp = cp[0].radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = cp[1].selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = logic_v3_0(v1, v2, v3, vp, vt, df)
    
    st.warning(status) if "تبديل" in status else st.success(status)
    if bait: play_alert()

    res = st.columns(2)
    res[0].info(f"🥇 المقترح الأول: **{p1}**")
    res[1].info(f"🥈 المقترح الثاني: **{p2}**")

# الترحيل
with st.expander("📥 ترحيل عاجل (لتصحيح المسار)"):
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    if st.button("🚀 تحديث المفاعل الآن"):
        payload = {"entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3, "entry.1625798960": aw, "entry.1007263974": p1, "entry.1719787271": lp}
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.cache_data.clear()
            st.rerun()
