import streamlit as st
import pandas as pd
import requests

# الروابط الثابتة والمؤكدة من صورك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V6.0", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- حساب الإحصائيات بدقة ---
st.sidebar.title("📊 لوحة الأداء")
if not df.empty:
    # حساب الجولات التي تحتوي على بيانات كاملة (بما فيها التوقع في العمود J)
    valid_data = df.dropna(subset=[df.columns[1], df.columns[9]]) 
    total = len(valid_data)
    st.sidebar.metric("🔢 جولات موثقة", total)
    
    if total > 0:
        # مقارنة الفائز الفعلي (I) بالتوقع (J)
        correct = (valid_data.iloc[:, 8].astype(str).str.strip() == 
                   valid_data.iloc[:, 9].astype(str).str.strip()).sum()
        accuracy = (correct / total) * 100
        st.sidebar.metric("🎯 دقة التنبؤ", f"{round(accuracy, 1)}%")

# --- واجهة التنبؤ ---
st.title("🧠 محرك التحليل الذكي")

with st.container(border=True):
    cols = st.columns(3)
    v1 = cols[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = cols[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = cols[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع (تعتمد على تاريخ العمود I)
    prediction = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6} # مواقع الطرق في شيت Responses
        match_idx = pos_map[vis_pos]
        history = df[df.iloc[:, match_idx] == vis_type]
        if not history.empty:
            relevant = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not relevant.empty:
                prediction = relevant.iloc[:, 8].value_counts().idxmax()
    
    st.subheader(f"🏆 التوقع الحالي: :green[{prediction}]")

# --- واجهة تدوين النتائج ---
st.divider()
st.subheader("📝 تسجيل النتيجة النهائية")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_t = c_hid[0].selectbox(f"طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_hid[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("موقع المسار الأطول فعلياً", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ الجولة ودمج التوقع في العمود J", use_container_width=True):
    road_results = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # إرسال الحزمة كاملة لضمان بقائها في سطر واحد
    payload = {
        "entry.1815594157": v1,
        "entry.1382952591": v2,
        "entry.734801074": v3,
        "entry.189628538": road_results["L"],
        "entry.725223032": road_results["C"],
        "entry.1054834699": road_results["R"],
        "entry.21622378": lp_pos,
        "entry.77901429": actual_w,
        "entry.1444222044": prediction # حقل التوقع الذي يصب في العمود J
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.status_code == 200:
            st.success(f"تم التسجيل! راجع السطر الأخير في العمود J.")
            st.balloons()
        else:
            st.error("فشل في مزامنة البيانات.")
    except:
        st.error("خطأ في الاتصال.")
