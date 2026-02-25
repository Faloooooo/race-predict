import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V64.1 - Ultimate Radar", layout="wide")

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

# --- 1. العدادات والنسبة (مثبتة في الأعلى) ---
if not df.empty:
    total_rounds = len(df)
    correct_preds = len(df[df.iloc[:, 8] == df.iloc[:, 9]])
    win_rate = (correct_preds / total_rounds) * 100 if total_rounds > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 إجمالي الجولات", total_rounds)
    c2.metric("🎯 نسبة دقة المحرك", f"{win_rate:.1f}%")
    c3.info(f"آخر تحديث للسجل: {time.strftime('%H:%M:%S')}")

st.divider()

tab1, tab2 = st.tabs(["🚀 الرادار والترحيل", "🔬 مختبر البحث"])

with tab1:
    # --- 2. منطقة التوقعات اللحظية (تظهر فوراً) ---
    st.subheader("🎯 رادار التوقع اللحظي")
    cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
    
    r_col1, r_col2, r_col3 = st.columns(3)
    v1_p = r_col1.selectbox("L", cars, index=0, key="v1_p")
    v2_p = r_col2.selectbox("C", cars, index=1, key="v2_p")
    v3_p = r_col3.selectbox("R", cars, index=2, key="v3_p")
    
    ri_col1, ri_col2 = st.columns([1, 2])
    vp_p = ri_col1.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key="vp_p")
    vt_p = ri_col2.selectbox("طريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="vt_p")

    # حساب التوقع بناءً على الـ 1853 جولة
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1_p) & (df.iloc[:, 2] == v2_p) & (df.iloc[:, 3] == v3_p) & (df.iloc[:, pos_map[vp_p]] == vt_p)]
    
    if not matches.empty:
        counts = matches.iloc[:, 8].value_counts()
        p1 = counts.index[0]
        p2 = counts.index[1] if len(counts) > 1 else (v2_p if v2_p != p1 else v1_p)
        
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin: 15px 0; background-color: #0E1117; padding: 15px; border-radius: 10px; border: 1px solid #00FFCC;">
            <div style="flex:1; text-align:center;"><h4>🥇 التوقع الأساسي</h4><h2 style="color:#00FFCC;">{p1}</h2></div>
            <div style="flex:1; text-align:center; border-left: 1px solid #444;"><h4>🥈 التوقع البديل</h4><h2 style="color:#FFCC00;">{p2}</h2></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ نمط جديد لم يسجل مسبقاً في البيانات.")

    st.divider()

    # --- 3. منطقة الترحيل (ثابتة) ---
    with st.form("recording_form"):
        st.subheader("📥 تدوين نتائج الجولة بعد الانتهاء")
        others = [p for p in ["L", "C", "R"] if p != vp_p]
        f_c1, f_c2 = st.columns(2)
        h1 = f_c1.selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = f_c2.selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_c3, f_c4 = st.columns(2)
        lp = f_c3.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f_c4.selectbox("الفائز الفعلي", [v1_p, v2_p, v3_p])
        
        submit = st.form_submit_button("🚀 ترحيل وحفظ الجولة الآن", use_container_width=True)

    if submit:
        # تجهيز البيانات للترحيل
        roads = {vp_p: vt_p, others[0]: h1, others[1]: h2}
        final_p = p1 if not matches.empty else v1_p
        payload = {
            "entry.159051415": v1_p, "entry.1682422047": v2_p, "entry.918899545": v3_p,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": final_p
        }
        try:
            res = requests.post(FORM_URL, data=payload)
            if res.ok:
                st.balloons()
                st.success("✅ تم ترحيل البيانات بنجاح!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("❌ فشل الاتصال، حاول مرة أخرى.")

with tab2:
    st.subheader("🔬 أداة البحث في الـ 1853 جولة")
    sc1, sc2, sc3 = st.columns(3)
    s1 = sc1.selectbox("سيارة L", cars, key="s1")
    s2 = sc2.selectbox("سيارة C", cars, key="s2")
    s3 = sc3.selectbox("سيارة R", cars, key="s3")
    
    search_res = df[(df.iloc[:, 1] == s1) & (df.iloc[:, 2] == s2) & (df.iloc[:, 3] == s3)]
    st.write(f"🔍 تم العثور على {len(search_res)} جولة مشابهة.")
    st.dataframe(search_res, use_container_width=True)

