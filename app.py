import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V33.5 - Zero Bias", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

def logic_v33_5(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "تحليل.."
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # ميزة: التركيز على آخر 100 جولة فقط للبحث عن النمط الحالي
    recent_data = data.tail(100)
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن الطريق في التاريخ الحديث (وزن مضاعف)
        recent_road_match = recent_data[(recent_data.iloc[:, pos_map[vp]] == vt) & (recent_data.iloc[:, 8] == car)]
        scores[car] += len(recent_road_match) * 15.0
        
        # وزن التاريخ القديم (وزن منخفض لتجنب التضليل)
        old_road_match = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)]
        scores[car] += len(old_road_match) * 2.0

    # رصد السلسلة: إذا فازت نفس السيارة كثيراً مؤخراً، قد يحين وقت "الغدر"
    last_3_winners = data.tail(3).iloc[:, 8].tolist()
    
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1 = sorted_res[0][0]
    p2 = sorted_res[1][0]

    # منطق كسر الغدر: إذا فازت p1 مرتين متتاليتين، p2 يصبح هو الأول
    if last_3_winners.count(p1) >= 2:
        p1, p2 = p2, p1
        status = "🛡️ وضع حماية من الغدر (تبديل التوقع)"
    else:
        status = "⚡ نمط هجومي مستقر"

    return p1, p2, status

# --- الواجهة ---
st.title("🏹 محرك الحسم V33.5 (إصدار كسر الـ 32%)")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2 = st.columns(2)
    c1.metric("الجولات المجمعة", len(df), delta=f"+{len(df)-508} منذ التحديث")
    c2.metric("الدقة الحالية", f"{rate:.1f}%", delta="-1.9%" if rate < 33.9 else "+")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status = logic_v33_5(v1, v2, v3, vp, vt, df)
    
    st.info(f"حالة المحرك: {status}")
    res = st.columns(2)
    res[0].success(f"🥇 التوقع القوي:\n**{p1}**")
    res[1].warning(f"🥈 التوقع الذكي:\n**{p2}**")

# نموذج الترحيل
with st.expander("📝 سجل بياناتك (فتيل القنبلة القادم)"):
    aw = st.selectbox("من فاز فعلاً؟", [v1, v2, v3])
    lp = st.radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True)
    
    if st.button("🚀 تحديث وحفظ"):
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.1625798960": str(aw), "entry.1007263974": str(p1), "entry.1719787271": str(lp)
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("تم التحديث! انظر للنتائج الآن.")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
