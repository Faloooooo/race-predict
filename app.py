import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V64.4 - Pro Radar", layout="wide")

# الروابط الثابتة
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

# --- 1. عدادات الأداء (أعلى الصفحة) ---
if not df.empty:
    total = len(df)
    correct = len(df[df.iloc[:, 8] == df.iloc[:, 9]])
    rate = (correct / total) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 إجمالي الجولات", total)
    c2.metric("🎯 دقة الرادار العامة", f"{rate:.1f}%")
    c3.success(f"📡 الحالة: رادار حيّ (Active)")

st.divider()

# --- 2. مدخلات المعطيات الظاهرة (تحديث لحظي) ---
st.subheader("🏁 رادار المعطيات الظاهرة (الآن)")
cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]

col_v1, col_v2, col_v3 = st.columns(3)
v1 = col_v1.selectbox("السيارة L", cars, index=0)
v2 = col_v2.selectbox("السيارة C", cars, index=1)
v3 = col_v3.selectbox("السيارة R", cars, index=2)

col_vp, col_vt = st.columns([1, 2])
vp = col_vp.radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
vt = col_vt.selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

# --- 3. محرك التوقع الاستباقي (المخ والأعصاب) ---
pos_map = {"L": 4, "C": 5, "R": 6}
matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]

st.write("### 🎯 التوقعات الاستراتيجية")
res_a, res_b = st.columns(2)

p1, p2 = "N/A", "N/A"

if not matches.empty:
    counts = matches.iloc[:, 8].value_counts()
    p1 = counts.index[0]
    p2 = counts.index[1] if len(counts) > 1 else (v2 if v2 != p1 else v3)
    
    with res_a:
        st.markdown(f"""<div style="text-align:center; border:3px solid #00FFCC; padding:15px; border-radius:15px; background-color:#1a1c24;">
        <p style="margin:0; color:#00FFCC;">🥇 توقع أساسي (تاريخي)</p>
        <h2 style="margin:0;">{p1}</h2>
        <p style="font-size:12px; color:#666;">الاستراتيجية: النمط الأكثر تكراراً بالملف</p></div>""", unsafe_allow_html=True)
    
    with res_b:
        st.markdown(f"""<div style="text-align:center; border:3px solid #FFCC00; padding:15px; border-radius:15px; background-color:#1a1c24;">
        <p style="margin:0; color:#FFCC00;">🥈 توقع ثانوي (منطقي)</p>
        <h2 style="margin:0;">{p2}</h2>
        <p style="font-size:12px; color:#666;">الاستراتيجية: كسر النمط السائد (Pivot)</p></div>""", unsafe_allow_html=True)
else:
    st.info("💡 هذا النمط يظهر لأول مرة، سيتم التوقع بناءً على السيارة القوية افتراضياً.")

st.divider()

# --- 4. منطقة ترحيل نهاية الجولة (البراغي) ---
tab1, tab2 = st.tabs(["📥 ترحيل وحفظ الجولة", "🔍 مختبر البحث المشتق"])

with tab1:
    with st.form("entry_form", clear_on_submit=False):
        st.subheader("📝 سجل ما حدث في نهاية الجولة")
        others = [p for p in ["L", "C", "R"] if p != vp]
        f_c1, f_c2 = st.columns(2)
        h1 = f_c1.selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = f_c2.selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_c3, f_c4 = st.columns(2)
        lp = f_c3.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f_c4.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        submit = st.form_submit_button("🚀 ترحيل البيانات الآن (بالونات التأكيد)", use_container_width=True)

    if submit:
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success(f"✅ تم الترحيل! جولة رقم {total+1} سُجلت.")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()

with tab2:
    st.subheader("🔬 البحث المشتق العميق")
    sc1, sc2, sc3 = st.columns(3)
    sv1, sv2, sv3 = sc1.selectbox("L", cars, key="sl"), sc2.selectbox("C", cars, key="sc"), sc3.selectbox("R", cars, key="sr")
    
    sc4, sc5 = st.columns(2)
    s_pos = sc4.multiselect("موقع الطريق المختار", ["L", "C", "R"], default=["L", "C", "R"])
    s_road = sc5.multiselect("نوع الطريق المختار", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], default=["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    s_df = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3)]
    st.write(f"🔍 عدد الحالات التاريخية: {len(s_df)}")
    st.dataframe(s_df, use_container_width=True)
