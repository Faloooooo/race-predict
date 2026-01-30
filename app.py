import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية والمحققة
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Master V10.0", layout="wide", page_icon="🏁")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- واجهة التنبؤ والتحليل ---
st.title("🧠 النظام المحدث - الربط المباشر بـ Prediction")

with st.container(border=True):
    col_v = st.columns(3)
    v1 = col_v[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_v[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_v[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col_r = st.columns(2)
    vis_pos = col_r[0].radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_r[1].selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # الخوارزمية التاريخية
    prediction = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            matches = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not matches.empty:
                prediction = matches.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🏆 التوقع البرمجي لـ (Column J): :green[{prediction}]")

# --- تدوين النتائج ---
st.divider()
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

c_f = st.columns(2)
lp_pos = c_f[0].radio("الموقع الأطول فعلياً", ["L", "C", "R"], horizontal=True)
actual_w = c_f[1].selectbox("الفائز الفعلي (العمود I)", [v1, v2, v3])

if st.button("🚀 إرسال وحفظ في العمود J", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # المعرفات المستخرجة من رابط المعاينة الخاص بك الآن
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(r_map["L"]),
        "entry.725223032": str(r_map["C"]),
        "entry.1054834699": str(r_map["R"]),
        "entry.21622378": str(lp_pos),
        "entry.77901429": str(actual_w),
        "entry.1444222044": str(prediction) # المعرّف المؤكد لخانة Prediction في العمود J
    }
    
    try:
        # إرسال البيانات
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(FORM_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            st.success(f"تم بنجاح! راجع العمود J الآن، ستجد ({prediction}) بجانب ({actual_w}).")
            st.balloons()
            st.cache_data.clear()
        else:
            st.error(f"خطأ في الاستجابة: {response.status_code}")
    except:
        st.error("فشل في الاتصال بخادم جوجل.")
