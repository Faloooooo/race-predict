import streamlit as st
import pandas as pd
import requests
import time

# الروابط الثابتة والمحققة من صورك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Master V7.0", layout="wide", page_icon="🏁")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        # إضافة طابع زمني لمنع جوجل من إعطائنا بيانات قديمة مخزنة
        url = f"{SHEET_READ_URL}&t={time.time()}"
        df_read = pd.read_csv(url)
        return df_read
    except Exception:
        return pd.DataFrame()

df = fetch_data()

# --- واجهة الإحصائيات (Sidebar) ---
st.sidebar.title("📊 مركز تحليل الجولات")
if not df.empty and df.shape[1] >= 10:
    # تنظيف البيانات لضمان حساب دقيق
    clean_df = df.dropna(subset=[df.columns[8], df.columns[9]])
    total = len(clean_df)
    st.sidebar.metric("🔢 جولات مكتملة (في نفس السطر)", total)
    
    if total > 0:
        correct = (clean_df.iloc[:, 8].astype(str).str.strip() == 
                   clean_df.iloc[:, 9].astype(str).str.strip()).sum()
        accuracy = (correct / total) * 100
        st.sidebar.metric("🎯 دقة التنبؤ الفعلية", f"{round(accuracy, 1)}%")

# --- واجهة التنبؤ (Prediction Section) ---
st.title("🧠 نظام التنبؤ الذكي")

with st.container(border=True):
    st.subheader("🏁 مدخلات السباق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    c_r = st.columns(2)
    vis_pos = c_r[0].radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = c_r[1].selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية البحث عن النمط التاريخي
    prediction = v1 # قيمة افتراضية
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6} # ترتيب الأعمدة في شيتك
        idx = pos_map[vis_pos]
        # البحث عن حالات مشابهة في التاريخ
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            if not sub.empty:
                prediction = sub.iloc[:, 8].value_counts().idxmax()
    
    st.subheader(f"🏆 التوقع البرمجي: :green[{prediction}]")

# --- واجهة التدوين (Logging Section) ---
st.divider()
st.subheader("📝 تسجيل بيانات الجولة")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"نوع طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"نوع طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

c_f = st.columns(2)
lp_pos = c_f[0].radio("موقع المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_w = c_f[1].selectbox("الفائز الفعلي", [v1, v2, v3])

# زر الإرسال النهائي الموحد
if st.button("🚀 تدوين النتيجة ودمج التوقع في العمود J", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # حزمة البيانات (Payload) - تم دمج التوقع كجزء لا يتجزأ من السطر
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(r_map["L"]),
        "entry.725223032": str(r_map["C"]),
        "entry.1054834699": str(r_map["R"]),
        "entry.21622378": str(lp_pos),
        "entry.77901429": str(actual_w),
        "entry.1444222044": str(prediction) # ضمان وصول التوقع لنفس السطر
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.status_code == 200:
            st.success(f"تم الحفظ! التوقع ({prediction}) سُجل في العمود J بنفس السطر.")
            st.balloons()
            st.cache_data.clear() # إجبار التطبيق على قراءة البيانات الجديدة فوراً
        else:
            st.error(f"خطأ في الاتصال بجوجل: {response.status_code}")
    except Exception as e:
        st.error(f"حدث خطأ تقني: {e}")
