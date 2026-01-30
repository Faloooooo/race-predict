import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V4.6", layout="wide", page_icon="🧠")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (العداد والنسبة) ---
st.sidebar.title("📊 إحصائيات النظام")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات", total_races)
    
    # حساب النسبة بمقارنة العمود I (الفائز) بالعمود J (التوقع)
    if total_races > 0 and df.shape[1] >= 10:
        actual = df.iloc[:, 8].astype(str).str.strip()
        predicted = df.iloc[:, 9].astype(str).str.strip()
        correct = (actual == predicted).sum()
        accuracy = (correct / total_races) * 100
        st.sidebar.metric("🎯 نسبة الدقة الحقيقية", f"{round(accuracy, 1)}%")
        st.sidebar.progress(min(accuracy/100, 1.0))

# --- الجزء العلوي: مدخلات التوقع ---
st.title("🔮 التنبؤ وبناء الخوارزمية")

with st.container(border=True):
    st.subheader("🏁 مدخلات ما قبل الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L) 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C) 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R) 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    col_vis, col_type = st.columns(2)
    vis_pos = col_vis.radio("موقع الطريق المرئي 4", ["L", "C", "R"], horizontal=True)
    vis_type = col_type.selectbox("نوع الطريق المرئي 5", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # حساب التوقع وتخزينه في session_state لضمان ثباته عند الإرسال
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            if not sub_match.empty:
                st.session_state.current_pred = sub_match.iloc[:, 8].value_counts().idxmax()
            else:
                st.session_state.current_pred = df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]
        else:
            st.session_state.current_pred = v1
    else:
        st.session_state.current_pred = v1

    st.subheader(f"🏆 الفائز المتوقع: :green[{st.session_state.current_pred}]")

# --- الجزء السفلي: تدوين النتائج ---
st.divider()
st.subheader("📝 تدوين نتائج الجولة (كشف الطرق المخفية)")
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_type = c_hid[0].selectbox(f"نوع الطريق المخفي ({others[0]}) 6", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_type = c_hid[1].selectbox(f"نوع الطريق المخفي ({others[1]}) 7", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

st.divider()
col_res1, col_res2 = st.columns(2)
lp_pos = col_res1.radio("موقع الطريق الأطول فعلياً 8", ["L", "C", "R"], horizontal=True)
actual_winner = col_res2.selectbox("الفائز الفعلي 9", [v1, v2, v3])

if st.button("✅ حفظ في السجل التاريخي وتدوين التوقع 10", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
    
    # تحضير البيانات بدقة للإرسال
    payload = {
        "entry.1815594157": v1, 
        "entry.1382952591": v2, 
        "entry.734801074": v3,
        "entry.189628538": roads["L"], 
        "entry.725223032": roads["C"], 
        "entry.1054834699": roads["R"],
        "entry.21622378": lp_pos, 
        "entry.77901429": actual_winner,
        "entry.1017387431": st.session_state.current_pred  # إرسال القيمة المخزنة في الذاكرة اللحظية
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.ok:
            st.success(f"تم الحفظ! التوقع ({st.session_state.current_pred}) ظهر الآن في العمود J.")
            st.balloons()
        else:
            st.error("فشل في الإرسال للنموذج.")
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
