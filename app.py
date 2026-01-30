import streamlit as st
import pandas as pd
import requests

# الروابط الرسمية الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V5.4", layout="wide", page_icon="🧠")

# جلب البيانات مع تحديث فوري
@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read
    except:
        return pd.DataFrame()

df = fetch_data()

# --- الإحصائيات الجانبية ---
st.sidebar.title("📊 مركز التحليل")
if not df.empty:
    total = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات", total)
    if df.shape[1] >= 10:
        # مقارنة الفائز (I) مع التوقع (J)
        actual = df.iloc[:, 8].astype(str).str.strip()
        predicted = df.iloc[:, 9].astype(str).str.strip()
        correct = (actual == predicted).sum()
        accuracy = (correct / total) * 100 if total > 0 else 0
        st.sidebar.metric("🎯 نسبة الدقة الحقيقية", f"{round(accuracy, 1)}%")

# --- واجهة التنبؤ ---
st.title("🔮 الخوارزمية الذكية")

with st.container(border=True):
    st.subheader("🏁 مدخلات ما قبل الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("L (1)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("C (2)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("R (3)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي 4", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي 5", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # منطق الخوارزمية (سيتطور بناءً على عمود J)
    current_prediction = v1
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            current_prediction = sub.iloc[:, 8].value_counts().idxmax() if not sub.empty else df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]

    st.subheader(f"🏆 الفائز المتوقع: :green[{current_prediction}]")

# --- واجهة التدوين ---
st.divider()
st.subheader("📝 تدوين النتائج الفعلية")
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_t = c_hid[0].selectbox(f"طريق {others[0]} (6)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_hid[1].selectbox(f"طريق {others[1]} (7)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("الأطول فعلياً (8)", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي (9)", [v1, v2, v3])

# الإرسال باستخدام المعرفات الصحيحة التي أثبتت نجاحها يدوياً
if st.button("✅ حفظ وتدوين التوقع في العمود J (رقم 10)", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(roads["L"]),
        "entry.725223032": str(roads["C"]),
        "entry.1054834699": str(roads["R"]),
        "entry.21622378": str(lp_pos),
        "entry.77901429": str(actual_w),
        "entry.1444222044": str(current_prediction)  # هذا المعرف هو الذي استقبل رسالتك "تريد حلاً سريعاً"
    }
    
    try:
        # إرسال البيانات بطريقة تحاكي ضغطة الزر في المتصفح
        response = requests.post(FORM_URL, data=payload)
        if response.status_code == 200:
            st.success(f"تم الحفظ! التوقع ({current_prediction}) سُجل الآن في العمود J.")
            st.balloons()
        else:
            st.error("جوجل رفض الاستلام، يرجى التأكد من عدم إغلاق النموذج.")
    except:
        st.error("فشل الاتصال بالخادم.")
