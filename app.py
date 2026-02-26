import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Race Master V66 - The Truth Test", layout="wide")

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

# --- الرأس والعدادات ---
with st.container():
    if not df.empty:
        total = len(df)
        # دقة آخر 50 جولة (مقياس كفاءة الموجة الحالية)
        recent_df = df.tail(50)
        recent_acc = (len(recent_df[recent_df.iloc[:, 8] == recent_df.iloc[:, 9]]) / 50) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 السجل الإجمالي", f"{total} جولة")
        c2.metric("🌊 دقة الموجة الأخيرة", f"{recent_acc:.1f}%")
        c3.info("🎯 الحالة: مراقبة الأنماط النشطة")

st.divider()

tab_radar, tab_search = st.tabs(["🎯 رادار الحسم", "🔬 مختبر التحليل"])

with tab_radar:
    # 1. إدخال المعطيات الظاهرة
    with st.container():
        st.subheader("🏁 مدخلات ما قبل السباق")
        cars_list = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
        
        ca, cb, cc = st.columns(3)
        v1 = ca.selectbox("السيارة L", cars_list, index=0, key="v1")
        v2 = cb.selectbox("السيارة C", cars_list, index=1, key="v2")
        v3 = cc.selectbox("السيارة R", cars_list, index=2, key="v3")
        
        cd, ce = st.columns([1, 2])
        vp = cd.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key="vp")
        vt = ce.selectbox("طريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="vt")

    # 2. محرك التوقع (المخ الرقمي)
    pos_map = {"L": 4, "C": 5, "R": 6}
    # فلترة البيانات بناءً على النمط
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    st.write("---")
    if not matches.empty:
        # إعطاء ثقل أكبر لآخر 5 جولات ظهر فيها هذا النمط
        recent_matches = matches.tail(5)
        p1 = matches.iloc[:, 8].value_counts().index[0] # الأكثر تكراراً تاريخياً
        p2 = recent_matches.iloc[-1, 8] if not recent_matches.empty else v2 # آخر فائز في هذا النمط
        
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='text-align:center; border:3px solid #00FFCC; padding:15px; border-radius:15px;'><h4 style='margin:0;'>🥇 الاستراتيجية التاريخية</h4><h2 style='color:#00FFCC;'>{p1}</h2><small>بناءً على تكرار الـ 1853 جولة</small></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='text-align:center; border:3px solid #FFCC00; padding:15px; border-radius:15px;'><h4 style='margin:0;'>🥈 استراتيجية الموجة</h4><h2 style='color:#FFCC00;'>{p2}</h2><small>بناءً على آخر سلوك للسيرفر</small></div>", unsafe_allow_html=True)
        
        if p1 == p2:
            st.success(f"🔥 **تطابق كامل:** الاستراتيجيتان تتفقان على {p1}. نسبة الثقة عالية.")
        else:
            st.warning(f"⚠️ **تذبذب في الموجة:** التاريخ يرجح {p1} ولكن السيرفر اتجه مؤخراً لـ {p2}.")
    else:
        p1 = v1
        st.info("🆕 نمط غير مسجل مسبقاً. بانتظار تدوينك لبناء الذاكرة.")

    st.write("")
    
    # 3. ترحيل البيانات (البراغي المثبتة)
    with st.form("save_race"):
        st.subheader("📥 تسجيل النتيجة النهائية")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_a, h_b = st.columns(2)
        h1 = h_a.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_b.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_a, f_b = st.columns(2)
        lp = f_a.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f_b.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل وتحديث الذكاء", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.cache_data.clear()
                st.rerun()

with tab_search:
    st.subheader("🔬 مختبر تحليل الأنماط")
    # أدوات بحث مستقلة تماماً
    s_col = st.columns(3)
    s1 = s_col[0].selectbox("سيارة L", cars_list, key="s1")
    s2 = s_col[1].selectbox("سيارة C", cars_list, key="s2")
    s3 = s_col[2].selectbox("سيارة R", cars_list, key="s3")
    
    res_df = df[(df.iloc[:, 1] == s1) & (df.iloc[:, 2] == s2) & (df.iloc[:, 3] == s3)]
    st.write(f"🔍 تم العثور على {len(res_df)} جولة مشابهة")
    st.dataframe(res_df, use_container_width=True)
