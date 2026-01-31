import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية (تم التأكد منها من رابط المعاينة الأخير)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        # كسر التخزين المؤقت لجلب البيانات الجديدة فوراً
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

st.title("🧠 نظام تحليل السباقات الذكي")

# --- واجهة الإدخال ---
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("السيارة الأولى (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("السيارة الثانية (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("السيارة الثالثة (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    vis_pos = st.radio("ما هو الموقع المرئي حالياً؟", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع (تبحث في العمود I و J)
    prediction = v1
    if not df.empty and df.shape[1] >= 10:
        pos_map = {"L": 4, "C": 5, "R": 6} # مطابقة لأعمدة الشيت E, F, G
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            # البحث عن الفائز الفعلي في التاريخ (العمود رقم 9 أي I)
            matches = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not matches.empty:
                prediction = matches.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🔮 التوقع المقترح للعمود J: :green[{prediction}]")

# --- تسجيل النتائج ---
st.divider()
st.subheader("📝 تسجيل بيانات السباق")
others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_h = st.columns(2)
h1_t = c_h[0].selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_h[1].selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

c_res = st.columns(2)
lp_pos = c_res[0].radio("المسار الأطول (Longer Path)", ["L", "C", "R"], horizontal=True)
actual_w = c_res[1].selectbox("من الفائز الفعلي؟", [v1, v2, v3])

if st.button("🚀 إرسال البيانات للتطبيق (مطابقة للإرسال اليدوي)", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # المعرفات المستخرجة من نموذجك (Race Database Pro) لضمان عدم وجود فراغات
    payload = {
        "entry.1705663365": str(v1),        # Car 1
        "entry.1982703816": str(v2),        # Car 2
        "entry.1030999553": str(v3),        # Car 3
        "entry.1223932977": str(r_map["L"]), # Road L
        "entry.1691888463": str(r_map["C"]), # Road C
        "entry.1788753238": str(r_map["R"]), # Road R
        "entry.1681290352": str(lp_pos),     # Longer Path
        "entry.763567117": str(actual_w),   # Actual Winner
        "entry.353386927": str(prediction)  # Prediction (العمود J)
    }
    
    try:
        # محاكاة إرسال المتصفح
        response = requests.post(FORM_URL, data=payload)
        if response.ok:
            st.success(f"✅ تم الربط بنجاح! السطر الجديد سيمتلئ تماماً مثل السطر رقم 7.")
            st.cache_data.clear()
        else:
            st.error(f"خطأ في الاستجابة من جوجل: {response.status_code}")
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال: {e}")
