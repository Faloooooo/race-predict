import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V5.1", layout="wide", page_icon="🏁")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[1]]) 
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (الإحصائيات) ---
st.sidebar.title("📊 مركز تحليل البيانات")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)
    # محاولة حساب الدقة بمقارنة العمود I بالعمود K (Prediction)
    if df.shape[1] >= 11:
        actual = df.iloc[:, 8].astype(str).str.strip()
        predicted = df.iloc[:, 10].astype(str).str.strip()
        correct = (actual == predicted).sum()
        accuracy = (correct / total_races) * 100 if total_races > 0 else 0
        st.sidebar.metric("🎯 دقة التوقع", f"{round(accuracy, 1)}%")

# --- التنبؤ ---
st.title("🔮 التنبؤ الذكي")

with st.container(border=True):
    st.subheader("🏁 معطيات الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L) 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C) 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R) 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي 4", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي 5", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # حساب التوقع
    pred_val = v1
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            pred_val = sub_match.iloc[:, 8].value_counts().idxmax() if not sub_match.empty else df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]
    
    st.session_state.current_prediction = pred_val
    st.subheader(f"🏆 الفائز المتوقع: :green[{st.session_state.current_prediction}]")

# --- التدوين ---
st.divider()
st.subheader("📝 تدوين نتائج الجولة")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_type = c_hid[0].selectbox(f"نوع الطريق المخفي ({others[0]}) 6", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_type = c_hid[1].selectbox(f"نوع الطريق المخفي ({others[1]}) 7", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("موقع الطريق الأطول فعلياً 8", ["L", "C", "R"], horizontal=True)
actual_winner = st.selectbox("الفائز الفعلي 9", [v1, v2, v3])

if st.button("✅ حفظ في السجل وتدوين التوقع (10) Prediction", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
    
    # تحضير الحقيبة البرمجية (Payload) - تم استبدال المفاتيح لتطابق طلبك الأخير
    payload = {
        "entry.1815594157": v1, 
        "entry.1382952591": v2, 
        "entry.734801074": v3,
        "entry.189628538": roads["L"], 
        "entry.725223032": roads["C"], 
        "entry.1054834699": roads["R"],
        "entry.21622378": lp_pos, 
        "entry.77901429": actual_winner,
        "entry.1444222044": st.session_state.current_prediction # المفتاح الجديد للخانة Prediction
    }
    
    try:
        # إرسال البيانات وإجبار جوجل على استلامها
        response = requests.post(FORM_URL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200 or response.status_code == 302:
            st.success(f"تم الإرسال! التوقع ({st.session_state.current_prediction}) سجل في العمود K بنجاح.")
            st.balloons()
        else:
            st.error(f"فشل الإرسال. كود الخطأ: {response.status_code}")
    except Exception as e:
        st.error(f"خطأ تقني: {e}")
