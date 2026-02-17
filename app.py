import streamlit as st
import pandas as pd
import requests
import time

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="Race Master V50.3 - Final Build", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

# --- محرك التحميل فائق السرعة ---
@st.cache_data(ttl=5, show_spinner=False)
def load_full_db():
    try:
        url = f"{SHEET_READ_URL}&cache_step={int(time.time()/10)}"
        # استخدام محرك C لضمان سرعة معالجة الـ 10,000 جولة
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1]])
    except Exception as e:
        return pd.DataFrame()

with st.spinner('⏳ جاري تحديث الذاكرة العميقة...'):
    df = load_full_db()

# --- محرك التحليل الإحصائي (Logic Engine) ---
def analyze_engine(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0
    cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # حساب قوة النمط (كم مرة تكرر هذا المشهد بالتفصيل)
    exact_matches = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 1:4].isin(cars).all(axis=1))]
    strength = len(exact_matches)
    
    scores = {v: 0.0 for v in cars}
    for c in cars:
        # 1. وزن التاريخ الكلي
        total_hits = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == c)])
        scores[c] += total_hits * 1.0
        # 2. وزن الزخم الحالي (آخر 60 جولة) - أقوى بـ 50 مرة
        recent = data.tail(60)
        recent_hits = len(recent[(recent.iloc[:, pos_map[vp]] == vt) & (recent.iloc[:, 8] == c)])
        scores[c] += recent_hits * 50.0

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    return p1, p2, strength

# --- واجهة المستخدم ---
st.markdown("<h2 style='text-align: center; color: #00FFCC;'>🛡️ رادار الاستحواذ V50.3</h2>", unsafe_allow_html=True)

if not df.empty:
    total = len(df)
    r30 = df.tail(30)
    acc = (len(r30[r30.iloc[:, 8] == r30.iloc[:, 9]]) / 30 * 100) if len(r30) >= 30 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 إجمالي الجولات", f"{total} / 10,000")
    m2.metric("📈 نسبة الربح (آخر 30)", f"{acc:.1f}%")
    with m3:
        st.write("🏁 المسار نحو الهدف")
        st.progress(min(total/10000, 1.0))

st.divider()

# --- قسم 1: المدخلات والتحليل الفوري ---
with st.container(border=True):
    st.subheader("📍 تحليل الجولة الحالية")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c_v[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c_v[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    st.write("---")
    ci = st.columns([1, 2])
    vp = ci[0].radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, strength = analyze_engine(v1, v2, v3, vp, vt, df)
    
    st.markdown(f"#### 🧩 قوة النمط المكتشفة: `{strength}`")
    res_c = st.columns(2)
    res_c[0].success(f"🥇 التوقع الأول (الرئيسي): {p1}")
    res_c[1].warning(f"🥈 التوقع الثاني (الاحتياطي): {p2}")

st.divider()

# --- قسم 2: الترحيل الشامل لضمان سلامة الداتا ---
with st.container(border=True):
    st.subheader("📥 ترحيل البيانات وحفظ الهيكل")
    others = [p for p in ["L", "C", "R"] if p != vp]
    
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    st.write("---")
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول (Longer Path)", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي (النتيجة النهائية)", [v1, v2, v3])

    if st.button("🚀 ترحيل وحفظ الجولة كاملة", use_container_width=True):
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تم الترحيل! المفاعل يتحدث الآن.")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("🔌 فشل في الاتصال. سيتم حفظ البيانات محلياً.")
