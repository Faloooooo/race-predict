import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الواجهة الاحترافية
st.set_page_config(page_title="Race Master V63.0 - Stability & Lab", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_data()

# التنقل بين الغرف (Tabs)
tab1, tab2 = st.tabs(["🚀 غرفة العمليات (ترحيل سريع)", "🔬 مختبر التحليل (هندسة عكسية)"])

# --- الغرفة الأولى: غرفة العمليات ---
with tab1:
    # عدادات القمة
    if not df.empty:
        total = len(df)
        recent = df.tail(100)
        acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / len(recent) * 100) if not recent.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 الرصيد", total)
        m2.metric("📈 الدقة الحالية", f"{acc:.1f}%")
        m3.progress(min(total/10000, 1.0))

    st.divider()

    # قسم الإدخال الثابت (Input Area)
    with st.container(border=True):
        st.subheader("🏁 إدخال بيانات السباق اللحظي")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        st.write("---")
        # الطرق والمسار الأطول
        r_col = st.columns(3)
        vp = r_col[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = r_col[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')
        lp = r_col[2].radio("المسار الأطول", ["L", "C", "R"], horizontal=True, key='lp')

    # منطقة التوقع المنفصلة (لا تؤثر على ثبات الصفحة)
    if v1 and v2 and v3:
        recent_600 = df.tail(600)
        pos_map = {"L": 4, "C": 5, "R": 6}
        match = recent_600[(recent_600.iloc[:, 1] == v1) & (recent_600.iloc[:, 2] == v2) & (recent_600.iloc[:, 3] == v3) & (recent_600.iloc[:, pos_map[vp]] == vt)]
        p1 = match.iloc[-1, 8] if not match.empty else "توقع تلقائي"
        st.info(f"💡 التوقع المقترح: **{p1}** (بناءً على النمط)")

    # قسم الترحيل
    with st.container(border=True):
        st.subheader("📥 ترحيل وحفظ")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_col = st.columns(2)
        h1 = h_col[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
        h2 = h_col[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
        aw = st.selectbox("الفائز الفعلي (Actual Winner)", [v1, v2, v3], key='aw')

        if st.button("🚀 ترحيل الجولة الآن", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                msg_box = st.success("✅ تم حفظ الجولة بنجاح في قاعدة البيانات!")
                time.sleep(2) # البقاء لثانيتين كما طلبت
                msg_box.empty()
                st.cache_data.clear()
                st.rerun()

# --- الغرفة الثانية: مختبر التحليل المتطور ---
with tab2:
    st.header("🔬 مختبر الهندسة العكسية (الفلترة الشاملة)")
    with st.container(border=True):
        st.subheader("🔍 معايير البحث الدقيق")
        f_c = st.columns(3)
        fv1 = f_c[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = f_c[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = f_c[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
        
        f_r = st.columns(2)
        f_vp = f_r[0].radio("موقع الطريق الظاهر", ["L", "C", "R"], key='f_vp', horizontal=True)
        f_vt = f_r[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='f_vt')

    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        # الفلترة بناءً على السيارات + موقع الطريق الظاهر + نوع الطريق الظاهر
        final_res = df[
            (df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) &
            (df.iloc[:, pos_map[f_vp]] == f_vt)
        ]

        st.subheader(f"📊 النتائج المطابقة للظروف: ({len(final_res)})")
        if not final_res.empty:
            # عرض الطرق المخفية والمسار الأطول والفائز كما طلبت
            view_df = final_res.iloc[:, [0, 4, 5, 6, 7, 8]]
            view_df.columns = ['التاريخ', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز']
            st.dataframe(view_df, use_container_width=True)
            
            # كشف التناقض
            winners = final_res.iloc[:, 8].unique()
            if len(winners) > 1:
                st.warning(f"⚠️ تنبيه: بنفس الظروف الظاهرة، تغير الفائز بين: {list(winners)}")
            else:
                st.success(f"💎 نمط ثابت: الفائز دائماً {winners[0]}")
        else:
            st.info("لم يتم العثور على هذا النمط الدقيق (سيارات + طريق ظاهر) سابقاً.")
