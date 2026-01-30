import streamlit as st
import pandas as pd
import requests
import time

# روابطك الجديدة والمؤكدة
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Logic Final", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

st.title("🏆 نظام Race Database Pro")

# --- واجهة التوقع ---
with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col_r = st.columns(2)
    vis_pos = col_r[0].radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_r[1].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = v1
    # البحث التاريخي (الأعمدة من 1 إلى 9)
    if not df.empty and df.shape[1] >= 9:
        pos_map = {"L": 4, "C": 5, "R": 6}
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            matches = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not matches.empty:
                prediction = matches.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🔮 التوقع للعمود J: :green[{prediction}]")

# --- تسجيل النتائج ---
st.divider()
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

c_res = st.columns(2)
lp_pos = c_res[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_w = c_res[1].selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 إرسال البيانات فوراً", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # المعرفات الدقيقة المستخرجة من رابط المعاينة الجديد
    payload = {
        "entry.1705663365": str(v1),        # Car 1 -> B
        "entry.1982703816": str(v2),        # Car 2 -> C
        "entry.1030999553": str(v3),        # Car 3 -> D
        "entry.1223932977": str(r_map["L"]), # Road L -> E
        "entry.1691888463": str(r_map["C"]), # Road C -> F
        "entry.1788753238": str(r_map["R"]), # Road R -> G
        "entry.1681290352": str(lp_pos),     # Long Path -> H
        "entry.763567117": str(actual_w),   # Winner -> I
        "entry.353386927": str(prediction)  # Prediction -> J
    }
    
    try:
        r = requests.post(FORM_URL, data=payload)
        if r.ok:
            st.success(f"✅ تم الإرسال! التوقع ({prediction}) سيعبئ العمود J الآن.")
            st.cache_data.clear()
        else:
            st.error("فشل في الإرسال.")
    except:
        st.error("خطأ اتصال.")
