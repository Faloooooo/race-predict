import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V63.3 - Decision Maker", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        return pd.read_csv(url, on_bad_lines='skip').dropna(subset=["Car 1 "])
    except: return pd.DataFrame()

df = load_data()

tab1, tab2 = st.tabs(["🎯 محرك الحسم", "🔬 مختبر التحليل"])

with tab1:
    # مدخلات الجولة
    with st.container(border=True):
        cols = st.columns(3)
        v1 = cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ci = st.columns([1, 2])
        vp = ci[0].radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # --- منطق الحسم (The Nerve Center) ---
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]

    if not matches.empty:
        counts = matches.iloc[:, 8].value_counts()
        p1 = counts.index[0]
        p2 = counts.index[1] if len(counts) > 1 else (v2 if v2 != p1 else v1)
        p3 = [c for c in [v1, v2, v3] if c not in [p1, p2]][0]
        
        # تحليل "الاستنزاف" - هل فاز الأول مؤخراً؟
        last_winner = matches.iloc[-1, 8]
        
        st.subheader("🔥 قرار المحرك الاستراتيجي")
        
        # عرض النتائج مع "توصية الحسم"
        res_cols = st.columns(3)
        
        with res_cols[0]:
            st.markdown(f"<div style='text-align:center; border:2px solid #00FFCC; padding:10px; border-radius:10px;'>🥇 <b>أساسي</b><br><span style='font-size:24px;'>{p1}</span></div>", unsafe_allow_html=True)
        with res_cols[1]:
            st.markdown(f"<div style='text-align:center; border:2px solid #FFCC00; padding:10px; border-radius:10px;'>🥈 <b>احتياطي</b><br><span style='font-size:24px;'>{p2}</span></div>", unsafe_allow_html=True)
        with res_cols[2]:
            st.markdown(f"<div style='text-align:center; border:2px solid #555; padding:10px; border-radius:10px;'>🥉 <b>مستبعد</b><br><span style='font-size:24px;'>{p3}</span></div>", unsafe_allow_html=True)

        st.divider()
        
        # نصيحة "المخ والأعصاب"
        if last_winner == p1:
            st.warning(f"⚠️ تنبيه: {p1} فاز في آخر جولة لهذا النمط. السيرفر قد يميل الآن لـ **{p2}** أو المفاجأة من **{p3}**.")
        else:
            st.success(f"✅ النمط مستقر. التركيز العالي على **{p1}** كخيار أول.")

    st.divider()

    # منطقة الترحيل (ثبات كامل)
    with st.form("save_v63"):
        st.subheader("📥 ترحيل وحفظ")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h1 = st.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = st.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp = st.radio("الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل البيانات", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1 if not matches.empty else v1
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.cache_data.clear()
                st.rerun()

with tab2:
    st.header("🔬 مختبر كشف الأنماط")
    if not df.empty:
        st.dataframe(df.tail(20), use_container_width=True)
