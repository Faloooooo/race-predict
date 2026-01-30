import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية والمؤكدة
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Master V9.0", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- محرك التحليل ---
st.title("🧠 الخوارزمية العبقرية - النسخة النهائية")

with st.container(border=True):
    cols = st.columns(3)
    v1 = cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # الخوارزمية (تبحث عن الفائز الأكثر تكراراً لنفس الطريق)
    prediction = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            match = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not match.empty:
                prediction = match.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🏆 التوقع: :green[{prediction}]")

# --- التدوين القسري ---
st.divider()
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 تسجيل الجولة (إرسال قسري للعمود J)", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # 1. إرسال البيانات الأساسية
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(roads["L"]),
        "entry.725223032": str(roads["C"]),
        "entry.1054834699": str(roads["R"]),
        "entry.21622378": str(lp_pos),
        "entry.77901429": str(actual_w),
        "entry.1444222044": str(prediction) # المحاولة الأولى للدمج
    }
    
    try:
        # محاكاة إرسال "نظيف" كأنه من متصفح
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(FORM_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            st.success(f"تم الإرسال! التوقع ({prediction}) أُرسل للعمود J.")
            st.balloons()
            # مسح الذاكرة لجلب السطر الجديد فوراً
            st.cache_data.clear()
        else:
            st.error("جوجل رفض الطلب.")
    except:
        st.error("فشل الاتصال.")
