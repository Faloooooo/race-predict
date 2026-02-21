import streamlit as st
import pandas as pd
import requests
import time

# 1. إعدادات الصفحة الثابتة لمنع القفز
st.set_page_config(page_title="Race Master V72.0 - Final Stability", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_db()

# --- العدادات السيادية في القمة (مثبتة) ---
if not df.empty:
    total_rounds = len(df)
    recent_100 = df.tail(100)
    correct = len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]])
    accuracy = (correct / len(recent_100)) * 100 if len(recent_100) > 0 else 0
    
    m1, m2, m3 = st.columns([1, 1, 2])
    m1.metric("📊 إجمالي الجولات", total_rounds)
    m2.metric("📈 نسبة الربح %", f"{accuracy:.1f}%")
    m3.success(f"آخر تحديث للسيرفر: {df.iloc[-1]['Timestamp']}")
st.divider()

# --- الألسنة الرئيسية ---
tab1, tab2 = st.tabs(["🚀 غرفة العمليات والتوقع", "🔬 محرك البحث والفلترة"])

with tab1:
    with st.container(border=True):
        st.subheader("🏁 مدخلات النمط")
        c_cols = st.columns(3)
        v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # --- منطقة التوقع وتحليل التناقض ---
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    primary_pred = v1 # افتراضي
    
    if not matches.empty:
        primary_pred = matches.iloc[-1, 8]
        st.markdown(f"""
            <div style="text-align: center; border: 2px solid #00FFCC; border-radius: 10px; padding: 15px; background-color: #0E1117;">
                <h2 style="color:white; margin:0;">🎯 التوقع الأساسي المقترح</h2>
                <h1 style="color:#00FFCC; font-size:45px; margin:10px 0;">{primary_pred}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("⚠️ **تحليل التناقض التاريخي لهذا النمط:**")
        counts = matches.iloc[:, 8].value_counts()
        c_counts_cols = st.columns(len(counts))
        for i, (car, count) in enumerate(counts.items()):
            c_counts_cols[i].warning(f"فاز {car}: **{count} مرة**")
    else:
        st.info("🆕 نمط جديد: لا توجد بيانات مطابقة لهذا الطريق والسيارات.")

    st.divider()

    # --- نموذج الترحيل (مثبت بمسامير برمجية) ---
    with st.form("secure_save_v72"):
        st.subheader("📥 ترحيل وحفظ البيانات")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_cols = st.columns(2)
        lp = f_cols[0].radio("المسار الأطول الفعلي (LP)", ["L", "C", "R"], horizontal=True)
        aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل وحفظ الجولة الآن", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": primary_pred
            }
            response = requests.post(FORM_URL, data=payload)
            if response.ok:
                st.balloons()
                st.toast("✅ تم ترحيل الداتا وحفظها بنجاح!", icon="🚀")
                st.success("🎉 تم الإرسال بنجاح إلى Google Sheets.")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ فشل الترحيل، يرجى التحقق من الاتصال.")

with tab2:
    st.header("🔬 محرك البحث والفلترة الشامل")
    if not df.empty:
        with st.container(border=True):
            sf = st.columns(3)
            sv1 = sf[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sv1_lab')
            sv2 = sf[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sv2_lab')
            sv3 = sf[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sv3_lab')
        
        # فلترة شاملة تظهر كل الأعمدة (الطريق الظاهر وموقعه)
        search_res = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3)]
        
        st.write(f"🔎 الجولات المكتشفة: **{len(search_res)}** جولة.")
        if not search_res.empty:
            # ترتيب الأعمدة لسهولة القراءة بصرية
            view_df = search_res.iloc[:, [0, 4, 5, 6, 7, 8]]
            view_df.columns = ['التاريخ', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز']
            st.dataframe(view_df, use_container_width=True)
