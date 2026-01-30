import streamlit as st
import pandas as pd
import requests
import time

# --- الروابط الرسمية (المستخرجة من آخر تحديث لك) ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeMVuDTK9rzhUJ4YsjX10KbBbszwZv2YNzjzlFRzWb2cZgh1A/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1Y25ss5fUxLir2VnVgUqPBesyaU7EHDrmsNkyGrPUAsg/export?format=csv"

st.set_page_config(page_title="Race Logic Pro V14", layout="wide", page_icon="🚀")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        # إضافة متغير عشوائي لضمان جلب أحدث البيانات من جوجل
        url = f"{SHEET_READ_URL}&cache_bust={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- واجهة المستخدم الذكية ---
st.title("🧠 نظام تحليل السباقات الذكي")

with st.container(border=True):
    col_v = st.columns(3)
    v1 = col_v[0].selectbox("السيارة اليسرى (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_v[1].selectbox("السيارة الوسطى (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_v[2].selectbox("السيارة اليمنى (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    
    col_road = st.columns(2)
    vis_pos = col_road[0].radio("أي مسار هو المرئي حالياً؟", ["L", "C", "R"], horizontal=True)
    vis_type = col_road[1].selectbox("ما هو نوع الطريق المرئي؟", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع (تعتمد على التاريخ في العمود J والعمود K)
    prediction = v1
    if not df.empty and df.shape[1] >= 10:
        # الخرائط البرمجية لمواقع الطرق في الشيت (بناءً على العمود B الزائد)
        pos_map = {"L": 5, "C": 6, "R": 7} 
        idx = pos_map[vis_pos]
        # تصفية البيانات التي تطابق نوع الطريق
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            # البحث عن السيارة الفائزة تاريخياً من بين السيارات الحالية
            match = history[history.iloc[:, 9].isin([v1, v2, v3])]
            if not match.empty:
                prediction = match.iloc[:, 9].value_counts().idxmax()

    st.subheader(f"🔮 التوقع المقترح للعمود K: :green[{prediction}]")

# --- تسجيل نتائج السباق ---
st.divider()
st.subheader("📝 تسجيل بيانات السباق الفعلية")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
col_hid = st.columns(2)
h1_t = col_hid[0].selectbox(f"نوع طريق {others[0]} (كان مخفياً)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = col_hid[1].selectbox(f"نوع طريق {others[1]} (كان مخفياً)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

col_res = st.columns(2)
lp_pos = col_res[0].radio("المسار الذي كان الأطول (Longer Path)", ["L", "C", "R"], horizontal=True)
actual_w = col_res[1].selectbox("من هو الفائز الفعلي؟", [v1, v2, v3])

if st.button("🚀 تدوين السباق وحفظ التوقع في العمود K", use_container_width=True):
    r_map = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # تحضير الحقيبة البرمجية (Payload) - أرقام الـ Entry مطابقة تماماً لرابطك الجديد
    payload = {
        "entry.1492211933": "Verified_Row", # تعبئة العمود B "Untitled" لضبط المحاذاة
        "entry.371932644": str(v1),         # العمود C
        "entry.1030013919": str(v2),        # العمود D
        "entry.1432243265": str(v3),        # العمود E
        "entry.2001155981": str(r_map["L"]), # العمود F
        "entry.75163351": str(r_map["C"]),   # العمود G
        "entry.1226065545": str(r_map["R"]), # العمود H
        "entry.1848529511": str(lp_pos),     # العمود I
        "entry.1704283180": str(actual_w),   # العمود J
        "entry.1690558907": str(prediction)  # العمود K (Prediction)
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.ok:
            st.success(f"✅ تم التسجيل! التوقع ({prediction}) أصبح الآن في العمود K.")
            st.balloons()
            st.cache_data.clear() # مسح الذاكرة لجلب السطر الجديد فوراً
        else:
            st.error("فشل في الوصول لخادم جوجل، يرجى المحاولة ثانية.")
    except:
        st.error("تأكد من اتصالك بالإنترنت.")
