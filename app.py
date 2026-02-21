import streamlit as st
import pandas as pd
import requests
import time

# 1. إعدادات الصفحة (ثبات الواجهة)
st.set_page_config(page_title="Race Master V64.0", layout="wide")

# منع القفز عبر تخصيص الحالة
if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = True

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        return pd.read_csv(url, on_bad_lines='skip', engine='c').dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_db()

# --- الهيكل الرئيسي (الألسنة) ---
tab1, tab2 = st.tabs(["🚀 غرفة العمليات", "🔬 مختبر التحليل"])

# --- الغرفة الأولى: غرفة العمليات (الإدخال السريع) ---
with tab1:
    if not df.empty:
        st.caption(f"📊 إجمالي الداتا: {len(df)} جولة")
    
    # قسم اختيار النمط (ثابت)
    with st.container(border=True):
        st.subheader("🏁 النمط الحالي")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ir1, ir2 = st.columns([1, 2])
        vp = ir1.radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir2.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # حساب التوقع (يظهر فوراً دون حركة)
    p1_res = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        match = df.tail(600)[(df.tail(600).iloc[:, 1] == v1) & (df.tail(600).iloc[:, 2] == v2) & (df.tail(600).iloc[:, 3] == v3) & (df.tail(600).iloc[:, pos_map[vp]] == vt)]
        if not match.empty: p1_res = match.iloc[-1, 8]
    
    st.info(f"💡 التوقع: **{p1_res}**")

    # نموذج الترحيل (هنا نمنع القفز باستخدام Form)
    with st.form("input_form"):
        st.subheader("📥 ترحيل البيانات")
        others = [p for p in ["L", "C", "R"] if p != vp]
        
        ch = st.columns(2)
        h1 = ch[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = ch[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        cf = st.columns(2)
        lp = cf[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True) # المسار الأطول هنا عند الترحيل
        aw = cf[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        submit = st.form_submit_button("🚀 حفظ الجولة والترحيل", use_container_width=True)
        
        if submit:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1_res
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("تم الحفظ!")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()

# --- الغرفة الثانية: مختبر التحليل (التي فقدناها) ---
with tab2:
    st.header("🔬 مختبر الهندسة العكسية")
    with st.container(border=True):
        st.subheader("🔎 فلترة النمط الكامل")
        fx = st.columns(3)
        fv1 = fx[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = fx[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = fx[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
        
        fr = st.columns(2)
        fvp = fr[0].radio("موقع الطريق الظاهر", ["L", "C", "R"], key='fvp_lab', horizontal=True)
        fvt = fr[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='fvt_lab')

    if not df.empty:
        pos_m = {"L": 4, "C": 5, "R": 6}
        results = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, pos_m[fvp]] == fvt)]
        
        st.write(f"📊 عدد المرات المكتشفة: {len(results)}")
        if not results.empty:
            # عرض البيانات: الطرق المخفية، المسار الأطول، الفائز
            view = results.iloc[:, [0, 4, 5, 6, 7, 8]]
            view.columns = ['التاريخ', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز']
            st.dataframe(view, use_container_width=True)
            
            # كشف التناقض
            winners = results.iloc[:, 8].unique()
            if len(winners) > 1:
                st.error(f"⚠️ تناقض: الفائز يتغير بين {list(winners)}")
            else:
                st.success(f"💎 نمط ثابت: الفائز دائماً هو {winners[0]}")
