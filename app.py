import streamlit as st
import pandas as pd
import requests
import time

# 1. إعدادات الصفحة (يجب أن تكون أول سطر)
st.set_page_config(page_title="Race Master V63.3", layout="wide")

# منع إعادة التحميل العشوائي للواجهة
if 'data_sent' not in st.session_state:
    st.session_state.data_sent = False

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_db()

# --- واجهة الألسنة ---
tab1, tab2 = st.tabs(["🚀 غرفة العمليات", "🔬 مختبر التحليل"])

with tab1:
    # عدادات ثابتة
    if not df.empty:
        total = len(df)
        m1, m2 = st.columns(2)
        m1.metric("📊 الرصيد الحالي", total)
        m2.progress(min(total/10000, 1.0))
    
    st.divider()

    # --- منطقة الإدخال المستقلة ---
    # استخدمنا حاوية واحدة ثابتة لمنع القفز
    with st.container():
        st.subheader("🏁 مدخلات الجولة")
        col_v = st.columns(3)
        v1 = col_v[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = col_v[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = col_v[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        col_r = st.columns([1, 2])
        vp = col_r[0].radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = col_r[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # حساب التوقع داخلياً (بدون تحديث الواجهة)
    p1_val = v1 # قيمة افتراضية
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        match = df.tail(600)[(df.tail(600).iloc[:, 1] == v1) & (df.tail(600).iloc[:, 2] == v2) & (df.tail(600).iloc[:, 3] == v3) & (df.tail(600).iloc[:, pos_map[vp]] == vt)]
        if not match.empty: p1_val = match.iloc[-1, 8]
    
    st.info(f"💡 التوقع المقترح: **{p1_val}**")

    st.divider()

    # --- نموذج الترحيل (Form) لمنع القفز نهائياً ---
    with st.form("main_form"):
        st.subheader("📥 إكمال البيانات والحفظ")
        others = [p for p in ["L", "C", "R"] if p != vp]
        
        c_h = st.columns(2)
        h1 = c_h[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = c_h[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        c_f = st.columns(2)
        lp = c_f[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
        aw = c_f[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        btn = st.form_submit_button("🚀 ترحيل وحفظ الجولة", use_container_width=True)

        if btn:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1_val
            }
            res = requests.post(FORM_URL, data=payload)
            if res.ok:
                st.balloons()
                st.success("✅ تم الحفظ بنجاح!")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ فشل الإرسال، تحقق من الإنترنت")

with tab2:
    st.header("🔬 مختبر التحليل")
    # تم تبسيط المختبر ليعمل كمرجع بحث فقط
    if not df.empty:
        st.dataframe(df.tail(20).iloc[:, [0,1,2,3,4,5,6,7,8]], use_container_width=True)
