import streamlit as st
import pandas as pd
import requests
import time

# --- الروابط الجديدة الخاصة بك (مستخرجة من رسالتك الأخيرة) ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeMVuDTK9rzhUJ4YsjX10KbBbszwZv2YNzjzlFRzWb2cZgh1A/formResponse"
# تحويل رابط الشيت إلى صيغة CSV للقراءة
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1Y25ss5fUxLir2VnVgUqPBesyaU7EHDrmsNkyGrPUAsg/export?format=csv"

st.set_page_config(page_title="Race Master Gold V11", layout="wide", page_icon="🏁")

# دالة جلب البيانات من الشيت الجديد
@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.title("📊 الإحصائيات (الشيت الجديد)")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي السباقات", total_races)
    
    # حساب الدقة من العمود I (رقم 8) والعمود J (رقم 9)
    if df.shape[1] >= 10:
        actual_col = df.iloc[:, 8].astype(str).str.strip().lower()
        pred_col = df.iloc[:, 9].astype(str).str.strip().lower()
        correct = (actual_col == pred_col).sum()
        acc = (correct / total_races) * 100 if total_races > 0 else 0
        st.sidebar.metric("🎯 نسبة الدقة", f"{round(acc, 1)}%")

# --- واجهة التوقع ---
st.title("🔮 محرك التنبؤ الذكي - الصفحة الجديدة")

with st.container(border=True):
    st.subheader("🏁 مدخلات الجولة")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("السيارة 1 (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("السيارة 2 (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("السيارة 3 (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع (ستبني ذكاءها من الصفر مع كل إدخال جديد)
    final_pred = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        idx = pos_map[vis_pos]
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            if not sub.empty:
                final_pred = sub.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🏆 الفائز المتوقع: :green[{final_pred}]")

# --- واجهة التدوين ---
st.divider()
st.subheader("📝 تسجيل نتائج الجولة في الشيت")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_t = c_hid[0].selectbox(f"نوع طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_hid[1].selectbox(f"نوع طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("المسار الأطول فعلياً", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي في السباق", [v1, v2, v3])

# زر الحفظ - تم ضبط المعرفات بناءً على النموذج الجديد 100%
if st.button("🚀 حفظ الجولة وتدوين التوقع في العمود J", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # المعرفات (Entry IDs) الجديدة والمؤكدة لنموذجك الجديد
    form_data = {
        "entry.371932644": str(v1),        # Car 1
        "entry.1030013919": str(v2),       # Car 2
        "entry.1432243265": str(v3),       # Car 3
        "entry.2001155981": str(roads["L"]), # Road L
        "entry.75163351": str(roads["C"]),   # Road C
        "entry.1226065545": str(roads["R"]), # Road R
        "entry.1848529511": str(lp_pos),     # Longer Path
        "entry.1704283180": str(actual_w),   # Actual Winner
        "entry.1690558907": str(final_pred)  # Prediction (العمود J)
    }
    
    try:
        r = requests.post(FORM_URL, data=form_data)
        if r.ok:
            st.success(f"تم بنجاح! التوقع ({final_pred}) ظهر الآن في العمود J بالشيت الجديد.")
            st.balloons()
            st.cache_data.clear() # تحديث البيانات فوراً
        else:
            st.error("فشل في الإرسال، تأكد من إعدادات النموذج.")
    except:
        st.error("خطأ في الاتصال.")
