import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V64.3 - Bronze Wave", layout="wide")

# الروابط الثابتة
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_data()

# --- 1. عدادات القمة (المسامير العلوية) ---
if not df.empty:
    total = len(df)
    success = len(df[df.iloc[:, 8] == df.iloc[:, 9]])
    rate = (success / total) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 إجمالي الجولات", total)
    c2.metric("🎯 نسبة الربح (الفعالية)", f"{rate:.1f}%")
    c3.info(f"📡 الموجة الحالية: برونزية مستقرة")

st.divider()

# --- 2. منطقة العمل (ثبات كامل) ---
tab1, tab2 = st.tabs(["🚀 التوقع والترحيل اللحظي", "🔬 مختبر البحث المطور"])

with tab1:
    # استخدام Form لضمان عدم تحرك الشاشة
    with st.form("main_work_form"):
        st.subheader("🏁 مدخلات النمط الحالي")
        cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
        
        ca, cb, cc = st.columns(3)
        v1 = ca.selectbox("L", cars, index=0)
        v2 = cb.selectbox("C", cars, index=1)
        v3 = cc.selectbox("R", cars, index=2)
        
        cd, ce = st.columns([1, 2])
        vp = cd.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = ce.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        st.write("---")
        st.subheader("📥 تسجيل النتائج (المخفي والـ LP)")
        
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_col1, h_col2 = st.columns(2)
        h1 = h_col1.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_col2.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        r_col1, r_col2 = st.columns(2)
        lp = r_col1.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = r_col2.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        submit = st.form_submit_button("🚀 ترحيل الجولة وتحديث الرادار", use_container_width=True)

    # حساب التوقع اللحظي (يظهر خارج الفورم ليكون واضحاً)
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    if not matches.empty:
        p_winner = matches.iloc[:, 8].value_counts().index[0]
        st.markdown(f"""<div style='text-align:center; padding:20px; border:2px solid #00FFCC; border-radius:15px; background-color:#1a1c24;'>
        <h3 style='margin:0;'>🥇 التوقع المقترح (بناءً على تاريخك)</h3>
        <h1 style='color:#00FFCC; margin:0;'>{p_winner}</h1></div>""", unsafe_allow_html=True)
    else:
        p_winner = v1 # افتراضي
        st.info("🆕 نمط جديد تماماً")

    if submit:
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p_winner
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم تثبيت الجولة في السجل بنجاح!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()

with tab2:
    st.subheader("🔬 البحث المشتق (فلترة المواقع والطرق)")
    sc1, sc2, sc3 = st.columns(3)
    s1 = sc1.selectbox("L", cars, key="s1")
    s2 = sc2.selectbox("C", cars, key="s2")
    s3 = sc3.selectbox("R", cars, key="s3")
    
    sc4, sc5 = st.columns(2)
    s_pos = sc4.multiselect("فلترة حسب موقع الطريق", ["L", "C", "R"], default=["L", "C", "R"])
    s_road = sc5.multiselect("فلترة حسب نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], default=["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    # محرك البحث المشتق
    search_df = df[(df.iloc[:, 1] == s1) & (df.iloc[:, 2] == s2) & (df.iloc[:, 3] == s3)]
    # إضافة فلاتر الـ LCR والطرق
    search_df = search_df[search_df.iloc[:, 7].isin(s_pos)] # فلترة حسب الـ LP أو الموقع (اختياري)
    
    st.write(f"🔍 النتائج المطابقة: {len(search_df)}")
    st.dataframe(search_res := search_df, use_container_width=True)
