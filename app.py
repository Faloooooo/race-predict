import streamlit as st
import pandas as pd  # تم إصلاح الخطأ هنا
import requests
import time
import streamlit.components.v1 as components

# --- 1. إعدادات الصفحة الشاملة ---
st.set_page_config(page_title="Race Master V50.1 - Final Fixed", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_full_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url)
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_full_db()

# --- 2. محرك التحليل الذكي ---
def analyze_engine(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # فحص قوة النمط (كم مرة تكرر هذا الموقف بدقة)
    exact_matches = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 1:4].isin(cars).all(axis=1))]
    strength = len(exact_matches)
    
    scores = {v: 0.0 for v in cars}
    for c in cars:
        total_hits = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)])
        scores[c] += total_hits * 1.0
        recent = data.tail(60)
        recent_hits = len(recent[(recent.iloc[:, pos_map[vp]] == vt) & (recent.iloc[:, 8] == c)])
        scores[c] += recent_hits * 50.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    return p1, p2, strength

# --- 3. عداد الجولات والهدف ونسبة الربح ---
st.markdown("<h2 style='text-align: center;'>🛡️ نظام الاستحواذ الكامل V50.1</h2>", unsafe_allow_html=True)
if not df.empty:
    total = len(df)
    r30 = df.tail(30)
    # حساب النسبة بمقارنة العمود 8 (Actual) مع العمود 9 (Prediction)
    acc = (len(r30[r30.iloc[:, 8] == r30.iloc[:, 9]]) / 30 * 100) if len(r30) >= 30 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 إجمالي الجولات", f"{total} / 10,000")
    m2.metric("📈 نسبة الربح (آخر 30)", f"{acc:.1f}%")
    with m3:
        st.write("🏁 هدف الـ 10,000 جولة")
        st.progress(min(total/10000, 1.0))

st.divider()

# --- 4. إدخال السيارات والتحليل اللحظي ---
with st.container(border=True):
    st.subheader("📍 مدخلات السباق والتحليل")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c_v[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c_v[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    st.write("---")
    ci = st.columns([1, 2])
    vp = ci[0].radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # استخراج التوقع
    p1, p2, strength = analyze_engine(v1, v2, v3, vp, vt, df)

    st.markdown(f"#### 🧩 قوة النمط (تكرر): `{strength}` مرة")
    res_c = st.columns(2)
    res_c[0].success(f"🥇 التوقع الأول: {p1}")
    res_c[1].warning(f"🥈 التوقع الثاني: {p2}")

st.divider()

# --- 5. الطرق المخفية والترحيل النهائي ---
with st.container(border=True):
    st.subheader("📥 تكملة البيانات وحفظ الجولة")
    others = [p for p in ["L", "C", "R"] if p != vp]
    
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    st.write("---")
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول فعلياً", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي في السباق", [v1, v2, v3])

    if st.button("🚀 ترحيل وحفظ البيانات", use_container_width=True):
        # مابينغ الطرق لضمان الترتيب الصحيح L, C, R في الشيت
        all_roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": all_roads["L"], "entry.658789827": all_roads["C"], "entry.1738752946": all_roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تم حفظ الجولة كاملة بنجاح!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("خطأ في الاتصال، تأكد من الإنترنت.")
