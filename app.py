import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V60.1 - Win Rate Fix", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5, show_spinner=False)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_data()

# --- محرك الفلترة العميقة ---
def deep_filter_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0, "انتظار البيانات"
    recent_600 = data.tail(600)
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # البحث عن تطابق النمط (السيارات + الطريق الظاهر)
    matches = recent_600[
        (recent_600.iloc[:, 1] == v1) & 
        (recent_600.iloc[:, 2] == v2) & 
        (recent_600.iloc[:, 3] == v3) &
        (recent_600.iloc[:, pos_map[vp]] == vt)
    ]
    
    strength = len(matches)
    if strength > 0:
        winners = matches.iloc[:, 8].tolist()
        p1 = winners[-1] 
        p2 = winners[-2] if len(winners) > 1 else (v2 if p1 == v1 else v1)
        msg = "🎯 نمط مكرر في الـ 8 ساعات الأخيرة"
    else:
        p1, p2 = v1, v2
        msg = "🆕 نمط جديد (توقع افتراضي)"
    return p1, p2, strength, msg

# --- الواجهة البرمجية ---
st.markdown("<h2 style='text-align: center; color: #00FFCC;'>🛡️ رادار الاستحواذ V60.1</h2>", unsafe_allow_html=True)

# حساب نسبة الربح (الأهم!)
if not df.empty:
    total = len(df)
    # نأخذ آخر 100 جولة لنرى مدى دقة التوقعات الحالية
    recent_eval = df.tail(100)
    # مقارنة الفائز الفعلي (العمود 8) بالتوقع المسجل (العمود 9)
    # تأكد أن العمود 9 في الشيت هو الذي سجلت فيه التوقعات
    correct_preds = len(recent_eval[recent_eval.iloc[:, 8] == recent_eval.iloc[:, 9]])
    accuracy = (correct_preds / len(recent_eval)) * 100 if len(recent_eval) > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("📊 إجمالي الجولات", total)
    m2.metric("📈 نسبة الربح (آخر 100)", f"{accuracy:.1f}%")
    with m3:
        st.write("🏁 التقدم نحو الـ 10,000")
        st.progress(min(total/10000, 1.0))

st.divider()

# --- قسم المدخلات ---
with st.container(border=True):
    st.subheader("📍 تحليل الجولة")
    c1, c2, c3 = st.columns(3)
    v1 = c1.selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c2.selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c3.selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    ci = st.columns([1, 2])
    vp = ci[0].radio("الموقع", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, strength, msg = deep_filter_logic(v1, v2, v3, vp, vt, df)
    
    st.info(f"{msg} | قوة التكرار: {strength}")
    res = st.columns(2)
    res[0].success(f"🥇 التوقع الأول: {p1}")
    res[1].warning(f"🥈 التوقع الثاني: {p2}")

st.divider()

# --- قسم الترحيل ---
with st.container(border=True):
    st.subheader("📥 ترحيل النمط الكامل")
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3])

    if st.button("🚀 حفظ الجولة", use_container_width=True):
        full_roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": full_roads["L"], "entry.658789827": full_roads["C"], "entry.1738752946": full_roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.cache_data.clear()
            st.rerun()
