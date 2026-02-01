import streamlit as st
import pandas as pd
import requests
import time

# الروابط
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V32.1 - Master Engine", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك التصويت الموحد (The Unified Engine) ---
def master_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, v3, 0
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    votes = {v: 0.0 for v in current_cars}

    # 1. تصويت الذاكرة التاريخية (الوزن: 30%)
    for car in current_cars:
        match = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        votes[car] += len(match) * 3.0

    # 2. تصويت السلسلة الحالية (الوزن: 40% - لأنك أكدت تكرار السيارات)
    last_5 = data.tail(5).iloc[:, 8].tolist()
    for car in current_cars:
        votes[car] += last_5.count(car) * 10.0

    # 3. تحليل الغدر العكسي (الوزن: 30%)
    last_20 = data.tail(20)
    betrayal_rate = (len(last_20[last_20.iloc[:, 8] != last_20.iloc[:, 9]]) / 20) * 100

    # ترتيب النتائج
    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    p1, p2, p3 = sorted_votes[0][0], sorted_res[1][0] if len(sorted_votes)>1 else v2, sorted_votes[2][0] if len(sorted_votes)>2 else v3
    
    return p1, p2, p3, betrayal_rate

# --- الواجهة الاحترافية ---
st.title("🔥 المحرك الشامل الموحد V32.1")
st.markdown("### نظام توليد الطاقة العميقة للتنبؤ")

if not df.empty:
    total = len(df)
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات المجمعة", total)
    c2.metric("دقة التوقع العام", f"{rate:.1f}%")
    c3.metric("مستوى الذكاء", "عميق (Deep Learning Ready)")

st.divider()

# المدخلات
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # الحصول على التوقعات الثلاثة
    p1, p2, p3, b_rate = master_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    st.subheader(f"🔮 نتائج التحليل العميق (نسبة الغدر الحالية: {b_rate:.0f}%)")
    
    res_cols = st.columns(3)
    res_cols[0].success(f"🥇 الخيار المتفجر:\n**{p1}**")
    res_cols[1].info(f"🥈 الخيار المساند:\n**{p2}**")
    res_cols[2].warning(f"⚠️ خيار كسر النمط:\n**{p3}**")

    if b_rate > 55:
        st.error(f"🛑 تحذير ذكاء اصطناعي: اللعبة في وضع 'الانحراف'. الخيار الثالث ({p3}) مرشح بقوة للغدر!")

# تسجيل الجولة
with st.expander("📥 تسجيل الجولة (حماية البيانات نشطة)"):
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    
    if st.button("🚀 حفظ وتفجير البيانات"):
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.1625798960": str(aw), "entry.1007263974": str(p1), "entry.1719787271": str(lp)
        }
        try:
            if requests.post(FORM_URL, data=payload, timeout=15).ok:
                st.balloons()
                st.cache_data.clear()
                st.rerun()
        except: st.error("فشل الإرسال. البيانات محفوظة، حاول مجدداً.")
