import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الواجهة لمنع القفز
st.set_page_config(page_title="Race Master V63.2 - Absolute Stability", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_data()

# استخدام الألسنة كفواصل رئيسية
tab1, tab2 = st.tabs(["🚀 غرفة العمليات", "🔬 مختبر التحليل"])

with tab1:
    # عدادات القمة (موجودة دائماً)
    if not df.empty:
        total = len(df)
        recent = df.tail(100)
        acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / len(recent) * 100) if not recent.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 الرصيد", total)
        m2.metric("📈 الدقة الحالية", f"{acc:.1f}%")
        m3.progress(min(total/10000, 1.0))
    st.divider()

    # --- الجزء 1: مدخلات التوقع (منفصلة لمنع الاهتزاز) ---
    st.subheader("🏁 تحديد النمط الحالي")
    c1, c2, c3 = st.columns(3)
    v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    st.write("---")
    ir1, ir2 = st.columns([1, 2])
    vp = ir1.radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
    vt = ir2.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # حساب التوقع فوراً وعرضه في مكان ثابت
    p1 = "جاري التحليل.."
    if not df.empty:
        recent_600 = df.tail(600)
        pos_map = {"L": 4, "C": 5, "R": 6}
        match = recent_600[(recent_600.iloc[:, 1] == v1) & (recent_600.iloc[:, 2] == v2) & (recent_600.iloc[:, 3] == v3) & (recent_600.iloc[:, pos_map[vp]] == vt)]
        p1 = match.iloc[-1, 8] if not match.empty else v1
    
    st.info(f"🥇 التوقع المقترح: **{p1}**")

    st.divider()

    # --- الجزء 2: الترحيل (استخدام FORM لمنع التحديث عند كل اختيار) ---
    st.subheader("📥 إكمال البيانات والترحيل النهائي")
    with st.form("entry_form", clear_on_submit=True):
        others = [p for p in ["L", "C", "R"] if p != vp]
        
        col_h = st.columns(2)
        h1 = col_h[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = col_h[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        col_f = st.columns(2)
        lp = col_f[0].radio("المسار الأطول (بعد نهاية السباق)", ["L", "C", "R"], horizontal=True)
        aw = col_f[1].selectbox("من هو الفائز الفعلي؟", [v1, v2, v3])
        
        submit_button = st.form_submit_button("🚀 ترحيل وحفظ الجولة الآن", use_container_width=True)

        if submit_button:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.ok:
                    st.balloons()
                    st.success("✅ تم حفظ الجولة بنجاح!")
                    time.sleep(2)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ فشل في الحفظ، تأكد من إعدادات Google Form")
            except:
                st.error("🔌 خطأ في الاتصال بالسيرفر")

# --- الغرفة الثانية: مختبر التحليل (ثابتة كما هي) ---
with tab2:
    st.header("🔬 مختبر الهندسة العكسية")
    # (كود المختبر يظل كما هو لعدم وجود مشاكل فيه)
    with st.container(border=True):
        f_c = st.columns(3)
        fv1 = f_c[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = f_c[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = f_c[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
        f_r = st.columns(2)
        f_vp = f_r[0].radio("موقع الظاهر", ["L", "C", "R"], key='f_vp', horizontal=True)
        f_vt = f_r[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='f_vt')
    
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        res = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, pos_map[f_vp]] == f_vt)]
        if not res.empty:
            st.dataframe(res.iloc[:, [0, 4, 5, 6, 7, 8]], use_container_width=True)
