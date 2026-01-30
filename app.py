import streamlit as st
import pandas as pd
import requests

# الروابط الثابتة (لا تغيرها)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Ultimate V6.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- إحصائيات دقيقة من العمود J ---
st.sidebar.title("📊 دقة النظام")
if not df.empty and df.shape[1] >= 10:
    # فلترة السطور التي تحتوي على توقع (العمود J) وفائز (العمود I)
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    total = len(valid)
    if total > 0:
        correct = (valid.iloc[:, 8].astype(str).str.strip() == 
                   valid.iloc[:, 9].astype(str).str.strip()).sum()
        accuracy = (correct / total) * 100
        st.sidebar.metric("🎯 نسبة النجاح", f"{round(accuracy, 1)}%")
        st.sidebar.metric("🔢 سباقات موثقة", total)

# --- محرك التنبؤ ---
st.title("🧠 الخوارزمية النهائية")

with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col_r = st.columns(2)
    vis_pos = col_r[0].radio("موقع المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_r[1].selectbox("نوع المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع
    final_pred = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        m_idx = pos_map[vis_pos]
        history = df[df.iloc[:, m_idx] == vis_type]
        if not history.empty:
            matches = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not matches.empty:
                final_pred = matches.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🏆 التوقع: :green[{final_pred}]")

# --- تدوين النتائج ---
st.divider()
st.subheader("📝 تدوين بيانات السباق")
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

c_f = st.columns(2)
lp = c_f[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
aw = c_f[1].selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ ودمج في العمود J", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1, others[1]: h2}
    
    # هذه الحزمة (Payload) هي "المسمار" الذي سيربط الصف ببعضه
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(r_map["L"]),
        "entry.725223032": str(r_map["C"]),
        "entry.1054834699": str(r_map["R"]),
        "entry.21622378": str(lp),
        "entry.77901429": str(aw),
        "entry.1444222044": str(final_pred) # التوقع في نفس الحزمة لضمان نفس الصف
    }
    
    try:
        res = requests.post(FORM_URL, data=payload)
        if res.ok:
            st.success("✅ تم بنجاح! التوقع والفائز في نفس السطر الآن.")
            st.balloons()
        else:
            st.error("جوجل استلم البيانات بشكل خاطئ.")
    except:
        st.error("خطأ في الاتصال.")
