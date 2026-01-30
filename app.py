import streamlit as st
import pandas as pd
import requests
import time

# الروابط الخاصة بك (الجديدة)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeMVuDTK9rzhUJ4YsjX10KbBbszwZv2YNzjzlFRzWb2cZgh1A/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1Y25ss5fUxLir2VnVgUqPBesyaU7EHDrmsNkyGrPUAsg/export?format=csv"

st.set_page_config(page_title="Race Master V12.0", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- الإحصائيات الذكية ---
st.sidebar.title("📊 حالة النظام")
if not df.empty and len(df) > 0:
    total = len(df)
    st.sidebar.metric("🔢 عدد السباقات", total)
    # التحقق من وجود أعمدة الفائز والتوقع (أصبحت الآن في مراكز جديدة)
    if df.shape[1] >= 11:
        try:
            # الفائز الفعلي (العمود رقم 10 - J) والتوقع (العمود رقم 11 - K)
            actual = df.iloc[:, 9].astype(str).str.strip().lower()
            pred = df.iloc[:, 10].astype(str).str.strip().lower()
            correct = (actual == pred).sum()
            st.sidebar.metric("🎯 نسبة الدقة", f"{round((correct/total)*100, 1)}%")
        except: pass
else:
    st.sidebar.info("بانتظار تسجيل أول جولة...")

# --- محرك التوقع ---
st.title("🏁 نظام السباق: الصفحة الجديدة")

with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوعه", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = v1
    # البحث التاريخي مع مراعاة العمود الإضافي "Untitled Question"
    if not df.empty and df.shape[1] >= 10:
        pos_map = {"L": 5, "C": 6, "R": 7} # زحف الأعمدة بسبب العمود B
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            match = history[history.iloc[:, 9].isin([v1, v2, v3])]
            if not match.empty:
                prediction = match.iloc[:, 9].value_counts().idxmax()

    st.subheader(f"🏆 التوقع الحالي: :green[{prediction}]")

# --- التسجيل الفعلي ---
st.divider()
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ الجولة النهائية", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # المعرفات الدقيقة جداً من رابط المعاينة الخاص بك
    payload = {
        "entry.1492211933": "System_Entry",  # قيمة للعمود Untitled Question (B)
        "entry.371932644": str(v1),          # Car 1 (C)
        "entry.1030013919": str(v2),         # Car 2 (D)
        "entry.1432243265": str(v3),         # Car 3 (E)
        "entry.2001155981": str(roads["L"]),   # Road L (F)
        "entry.75163351": str(roads["C"]),     # Road C (G)
        "entry.1226065545": str(roads["R"]),   # Road R (H)
        "entry.1848529511": str(lp_pos),       # Long Path (I)
        "entry.1704283180": str(actual_w),     # Winner (J)
        "entry.1690558907": str(prediction)    # Prediction (K)
    }
    
    try:
        r = requests.post(FORM_URL, data=payload)
        if r.ok:
            st.success("✅ تم الحفظ! البيانات ستظهر الآن في الأعمدة J و K.")
            st.balloons()
            st.cache_data.clear()
        else: st.error("فشل الإرسال.")
    except: st.error("خطأ اتصال.")
