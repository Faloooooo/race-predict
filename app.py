import streamlit as st
import pandas as pd
import requests
import time

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeMVuDTK9rzhUJ4YsjX10KbBbszwZv2YNzjzlFRzWb2cZgh1A/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1Y25ss5fUxLir2VnVgUqPBesyaU7EHDrmsNkyGrPUAsg/export?format=csv"

st.set_page_config(page_title="Race Logic Gold V13.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        df_read = pd.read_csv(url)
        return df_read
    except:
        return pd.DataFrame()

df = fetch_data()

# --- معالجة الإحصائيات بأمان ---
st.sidebar.title("📊 مركز البيانات")
if not df.empty and df.shape[1] >= 11:
    try:
        total = len(df)
        actual_col = df.iloc[:, 9].astype(str).str.strip().lower()
        pred_col = df.iloc[:, 10].astype(str).str.strip().lower()
        correct = (actual_col == pred_col).sum()
        st.sidebar.metric("🔢 إجمالي الجولات", total)
        st.sidebar.metric("🎯 دقة التوقع", f"{round((correct/total)*100, 1)}%")
    except Exception:
        st.sidebar.warning("سجل بيانات لفعيل الإحصائيات")
else:
    st.sidebar.info("الشيت جديد ونظيف. سجل أول جولة الآن!")

# --- واجهة التوقع ---
st.title("🧠 نظام التحليل الذكي")

with st.container(border=True):
    col_v = st.columns(3)
    v1 = col_v[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_v[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_v[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = v1
    if not df.empty and df.shape[1] >= 10:
        pos_map = {"L": 5, "C": 6, "R": 7}
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            matches = history[history.iloc[:, 9].isin([v1, v2, v3])]
            if not matches.empty:
                prediction = matches.iloc[:, 9].value_counts().idxmax()

    st.subheader(f"🏆 التوقع للعمود K: :green[{prediction}]")

# --- تدوين النتائج ---
st.divider()
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("الأطول فعلياً", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 تسجيل الجولة الأولى", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    payload = {
        "entry.1492211933": "First_Entry",
        "entry.371932644": str(v1),
        "entry.1030013919": str(v2),
        "entry.1432243265": str(v3),
        "entry.2001155981": str(r_map["L"]),
        "entry.75163351": str(r_map["C"]),
        "entry.1226065545": str(r_map["R"]),
        "entry.1848529511": str(lp_pos),
        "entry.1704283180": str(actual_w),
        "entry.1690558907": str(prediction)
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.ok:
            st.success("✅ تم تسجيل أول جولة بنجاح! سيختفي الخطأ الآن.")
            st.balloons()
            st.cache_data.clear()
        else:
            st.error("مشكلة في الإرسال.")
    except:
        st.error("خطأ اتصال.")
