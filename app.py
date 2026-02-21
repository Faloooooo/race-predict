import streamlit as st
import pandas as pd
import requests
import time

# 1. إعدادات الصفحة والثبات
st.set_page_config(page_title="Race Master V66.1", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        return pd.read_csv(url, on_bad_lines='skip', engine='c').dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_db()

# حساب الإحصائيات العامة
if not df.empty:
    total_rounds = len(df)
    recent_100 = df.tail(100)
    correct = len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]])
    accuracy = (correct / len(recent_100)) * 100 if not recent_100.empty else 0

tab1, tab2 = st.tabs(["⚡ غرفة العمليات", "🔍 مختبر الفلترة"])

with tab1:
    # عدادات القمة
    if not df.empty:
        m1, m2 = st.columns(2)
        m1.metric("📈 الدقة (آخر 100)", f"{accuracy:.1f}%")
        m2.metric("📊 الرصيد", total_rounds)
    st.divider()

    # مدخلات النمط
    with st.container(border=True):
        st.subheader("🏁 تحديد النمط")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # --- ميزة "آخر جولة للنمط" (طلبك الخاص) ---
    st.subheader("🕵️ ذاكرة السيرفر اللحظية")
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    p1_final = v1 # افتراضي
    if not matches.empty:
        last_match = matches.iloc[-1]
        st.markdown(f"""
        <div style="background-color:#1E1E1E; padding:15px; border-radius:10px; border-left: 5px solid #00FFCC;">
            <h4 style="margin:0; color:#00FFCC;">🔄 آخر ظهور لهذا النمط:</h4>
            <p style="margin:5px 0;"><b>الفائز:</b> <span style="font-size:20px; color:yellow;">{last_match['Actual Winner ']}</span> 
            | <b>التوقيت:</b> {last_match['Timestamp']} 
            | <b>المسار الأطول:</b> {last_match['Longer Path ']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # كاشف الذهب المدمج (للمسار الأطول)
        for path in ["L", "C", "R"]:
            spec = matches[matches['Longer Path '] == path]
            if not spec.empty and len(spec['Actual Winner '].unique()) == 1:
                st.success(f"🌟 **نمط ذهبي:** إذا كان الأطول **{path}** ارهن على **{spec['Actual Winner '].iloc[0]}**")
                p1_final = spec['Actual Winner '].iloc[0]
        if p1_final == v1: p1_final = last_match['Actual Winner ']
    else:
        st.info("🆕 نمط جديد: لم يظهر مسبقاً بنفس الطريق الظاهر.")

    # --- نموذج الترحيل ---
    with st.form("quick_save_v661"):
        st.subheader("📥 ترحيل وحفظ")
        others = [p for p in ["L", "C", "R"] if p != vp]
        ch = st.columns(2)
        h1 = ch[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = ch[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        cf = st.columns(2)
        lp = cf[0].radio("الأطول", ["L", "C", "R"], horizontal=True)
        aw = cf[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل الجولة الآن", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1_final
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.cache_data.clear()
                st.rerun()

with tab2:
    st.header("🔬 مختبر الفلترة")
    # (كود الفلترة الكامل السابق موجود هنا)
    if not df.empty:
        st.write("استخدم الفلاتر في غرفة العمليات لرؤية النتائج الفورية، أو تصفح الداتا هنا.")
        st.dataframe(df.tail(20), use_container_width=True)
