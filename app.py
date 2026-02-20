import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الواجهة
st.set_page_config(page_title="Race Master V63.1", layout="wide")

FORM_URL = "https://docs.google.com/forms/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_data()

tab1, tab2 = st.tabs(["🚀 غرفة العمليات", "🔬 مختبر التحليل"])

# --- الغرفة الأولى: غرفة العمليات ---
with tab1:
    if not df.empty:
        total = len(df)
        recent = df.tail(100)
        acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / len(recent) * 100) if not recent.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 الرصيد", total)
        m2.metric("📈 الدقة الحالية", f"{acc:.1f}%")
        m3.progress(min(total/10000, 1.0))

    st.divider()

    # 1. قسم الإدخال السريع (السيارات والطريق الظاهر فقط)
    with st.container(border=True):
        st.subheader("🏁 مدخلات السباق اللحظي")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        st.write("---")
        ir1, ir2 = st.columns([1, 2])
        vp = ir1.radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir2.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # 2. منطقة التوقع (منفصلة تماماً لثبات الصفحة)
    with st.empty():
        if v1 and v2 and v3:
            recent_600 = df.tail(600)
            pos_map = {"L": 4, "C": 5, "R": 6}
            match = recent_600[(recent_600.iloc[:, 1] == v1) & (recent_600.iloc[:, 2] == v2) & (recent_600.iloc[:, 3] == v3) & (recent_600.iloc[:, pos_map[vp]] == vt)]
            p1 = match.iloc[-1, 8] if not match.empty else "توقع تلقائي"
            st.success(f"🥇 التوقع المقترح بناءً على النمط: **{p1}**")

    # 3. قسم الترحيل (إضافة المسار الأطول هنا)
    with st.container(border=True):
        st.subheader("📥 إكمال البيانات والترحيل")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_col = st.columns(2)
        h1 = h_col[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
        h2 = h_col[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
        
        st.write("---")
        f_col = st.columns(2)
        lp = f_col[0].radio("المسار الأطول (Longer Path)", ["L", "C", "R"], horizontal=True, key='lp') # نُقل إلى هنا
        aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3], key='aw')

        if st.button("🚀 ترحيل وحفظ الجولة", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                msg = st.success("✅ تم حفظ الجولة بنجاح!")
                time.sleep(2)
                msg.empty()
                st.cache_data.clear()
                st.rerun()

# --- الغرفة الثانية: مختبر التحليل ---
with tab2:
    st.header("🔬 مختبر الهندسة العكسية")
    with st.container(border=True):
        st.subheader("🔍 معايير البحث")
        f_c = st.columns(3)
        fv1 = f_c[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = f_c[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = f_c[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
        
        f_r = st.columns(2)
        f_vp = f_r[0].radio("موقع الظاهر", ["L", "C", "R"], key='f_vp', horizontal=True)
        f_vt = f_r[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='f_vt')

    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        final_res = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, pos_map[f_vp]] == f_vt)]
        if not final_res.empty:
            view_df = final_res.iloc[:, [0, 4, 5, 6, 7, 8]]
            view_df.columns = ['التاريخ', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز']
            st.dataframe(view_df, use_container_width=True)
