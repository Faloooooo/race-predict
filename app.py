import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V62.4 - Full Recovery", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=2)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_data()

# العداد العلوي - مثبت
if not df.empty:
    st.markdown(f"""<div style='text-align: center; background-color: #0E1117; padding: 10px; border-radius: 10px; border: 1px solid #444;'>
    <h2 style='margin:0; color: #00FFCC;'>📊 إجمالي الجولات في الشيت: {len(df)}</h2></div>""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 العمليات والترحيل", "🔬 المختبر المتقدم"])

with tab1:
    with st.form("master_form"):
        st.subheader("🏁 مدخلات الجولة الحالية")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=0)
        v2 = c2.selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1)
        v3 = c3.selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2)
        
        ci = st.columns([1, 2])
        vp = ci[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        st.divider()
        st.subheader("📥 نتائج الجولة للترحيل")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_cols = st.columns(2)
        lp = f_cols[0].radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        submit_btn = st.form_submit_button("🚀 حفظ الجولة واستخراج التوقعات", use_container_width=True)

    if submit_btn:
        # حساب التوقعات بناءً على النمط
        pos_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
        
        if not matches.empty:
            counts = matches.iloc[:, 8].value_counts()
            p1 = counts.index[0] if len(counts) > 0 else v1
            p2 = counts.index[1] if len(counts) > 1 else v2
            p3 = counts.index[2] if len(counts) > 2 else v3
            
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <div style="flex:1; text-align:center; border:2px solid #00FFCC; border-radius:10px; padding:10px;">🥇 1: {p1}</div>
                <div style="flex:1; text-align:center; border:2px solid #FFCC00; border-radius:10px; padding:10px;">🥈 2: {p2}</div>
                <div style="flex:1; text-align:center; border:2px solid #FF4B4B; border-radius:10px; padding:10px;">🥉 3: {p3}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # تنفيذ الترحيل
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1 if not matches.empty else v1
        }
        
        try:
            r = requests.post(FORM_URL, data=payload)
            if r.ok:
                st.balloons()
                st.success("✅ تم الترحيل بنجاح! العداد سيتحدث الآن.")
                time.sleep(1)
                st.rerun()
        except:
            st.error("❌ فشل الاتصال بالسيرفر.")

with tab2:
    st.header("🔬 مختبر التحليل")
    if not df.empty:
        # واجهة المختبر بسيطة وثابتة
        sf = st.columns(3)
        sv1 = sf[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='s1')
        sv2 = sf[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='s2')
        sv3 = sf[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='s3')
        
        res = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3)]
        st.dataframe(res.iloc[:, [0, 4, 5, 6, 7, 8]], use_container_width=True)
