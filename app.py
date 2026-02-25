import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الصفحة لمنع القفز وتثبيت العناصر
st.set_page_config(page_title="Race Master V65 - Stable Shield", layout="wide")

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

# --- 1. عدادات القمة الثابتة ---
with st.container():
    if not df.empty:
        total = len(df)
        # مقارنة الفائز الفعلي بالتوقع المسجل في الشيت
        correct = len(df[df.iloc[:, 8] == df.iloc[:, 9]])
        rate = (correct / total) * 100 if total > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 إجمالي الجولات", total)
        c2.metric("🎯 دقة الرادار", f"{rate:.1f}%")
        c3.success(f"📡 الموجة: برونزية مستقرة")

st.divider()

# --- 2. نظام التبويبات (فصل البحث عن العمل) ---
tab_work, tab_search = st.tabs(["🚀 الرادار والترحيل", "🔬 مختبر البحث المستقل"])

with tab_work:
    # منطقة الرادار الاستباقي (ثابتة لا تتحرك)
    st.subheader("🎯 الرادار الاستباقي (توقع لحظي)")
    
    with st.container():
        cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
        
        # مدخلات السيارات - استخدام key ثابت لمنع القفز
        ca, cb, cc = st.columns(3)
        v1 = ca.selectbox("السيارة L", cars, index=0, key="main_v1")
        v2 = cb.selectbox("السيارة C", cars, index=1, key="main_v2")
        v3 = cc.selectbox("السيارة R", cars, index=2, key="main_v3")
        
        cd, ce = st.columns([1, 2])
        vp = cd.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key="main_vp")
        vt = ce.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="main_vt")

    # --- محرك التوقع (يعمل بمجرد التغيير فوق) ---
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    p1, p2 = "N/A", "N/A"
    if not matches.empty:
        counts = matches.iloc[:, 8].value_counts()
        p1 = counts.index[0]
        p2 = counts.index[1] if len(counts) > 1 else (v2 if v2 != p1 else v3)
        
        res_col1, res_col2 = st.columns(2)
        res_col1.markdown(f"<div style='text-align:center; border:2px solid #00FFCC; padding:10px; border-radius:10px; background-color:#1a1c24;'><p style='color:#00FFCC; margin:0;'>🥇 أساسي (تاريخي)</p><h2 style='margin:0;'>{p1}</h2></div>", unsafe_allow_html=True)
        res_col2.markdown(f"<div style='text-align:center; border:2px solid #FFCC00; padding:10px; border-radius:10px; background-color:#1a1c24;'><p style='color:#FFCC00; margin:0;'>🥈 ثانوي (منطقي)</p><h2 style='margin:0;'>{p2}</h2></div>", unsafe_allow_html=True)
    else:
        st.info("🆕 نمط جديد لم يسجل في الـ 1853 جولة")

    st.write("")
    
    # --- نموذج الترحيل (Form) لضمان ثبات الشاشة ---
    with st.form("entry_and_save_form"):
        st.subheader("📥 ترحيل وحفظ البيانات")
        others = [p for p in ["L", "C", "R"] if p != vp]
        
        f1, f2 = st.columns(2)
        h1 = f1.selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = f2.selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f3, f4 = st.columns(2)
        lp = f3.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f4.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        submit = st.form_submit_button("🚀 ترحيل الجولة (تأكيد بالونات)", use_container_width=True)

    if submit:
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الترحيل بنجاح!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()

with tab_search:
    st.subheader("🔬 مختبر البحث المشتق والفرز العميق")
    # مدخلات البحث منفصلة تماماً لمنع أي تداخل
    sa, sb, sc = st.columns(3)
    sv1 = sa.selectbox("سيارة L", cars, key="search_v1")
    sv2 = sb.selectbox("سيارة C", cars, key="search_v2")
    sv3 = sc.selectbox("سيارة R", cars, key="search_v3")
    
    sd, se = st.columns(2)
    s_pos = sd.multiselect("فلترة حسب الموقع (LCR)", ["L", "C", "R"], default=["L", "C", "R"])
    s_road = se.multiselect("فلترة حسب الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], default=["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    # محرك البحث التاريخي
    s_df = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3)]
    st.write(f"🔍 نتائج مطابقة: {len(s_df)}")
    st.dataframe(s_df, use_container_width=True)
