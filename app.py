import streamlit as st
import pandas as pd
import requests
import time

# الروابط الجديدة الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeMVuDTK9rzhUJ4YsjX10KbBbszwZv2YNzjzlFRzWb2cZgh1A/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1Y25ss5fUxLir2VnVgUqPBesyaU7EHDrmsNkyGrPUAsg/export?format=csv"

st.set_page_config(page_title="Race Master Gold V11.1", layout="wide", page_icon="🏁")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        df_read = pd.read_csv(url)
        return df_read
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (تم إصلاحها لتجنب الخطأ) ---
st.sidebar.title("📊 الإحصائيات")
if not df.empty and len(df) > 0:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي السباقات", total_races)
    
    # لا نحسب الدقة إلا إذا كان هناك 10 أعمدة على الأقل وبيانات فعلية
    if df.shape[1] >= 10:
        try:
            actual_col = df.iloc[:, 8].astype(str).str.strip().lower()
            pred_col = df.iloc[:, 9].astype(str).str.strip().lower()
            correct = (actual_col == pred_col).sum()
            acc = (correct / total_races) * 100
            st.sidebar.metric("🎯 نسبة الدقة", f"{round(acc, 1)}%")
        except:
            st.sidebar.write("انتظار البيانات الإحصائية...")
else:
    st.sidebar.info("سجل أول سباق لبدء الإحصائيات")

# --- واجهة التوقع ---
st.title("🔮 محرك التنبؤ الذكي")

with st.container(border=True):
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("السيارة 1 (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("السيارة 2 (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("السيارة 3 (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    final_pred = v1
    # منطق التوقع سيعمل فقط إذا كان هناك بيانات سابقة
    if not df.empty and df.shape[1] >= 9:
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
st.subheader("📝 تسجيل النتائج")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_t = c_hid[0].selectbox(f"نوع طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_hid[1].selectbox(f"نوع طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ الجولة في العمود J", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    form_data = {
        "entry.371932644": str(v1),
        "entry.1030013919": str(v2),
        "entry.1432243265": str(v3),
        "entry.2001155981": str(roads["L"]),
        "entry.75163351": str(roads["C"]),
        "entry.1226065545": str(roads["R"]),
        "entry.1848529511": str(lp_pos),
        "entry.1704283180": str(actual_w),
        "entry.1690558907": str(final_pred)
    }
    
    try:
        r = requests.post(FORM_URL, data=form_data)
        if r.ok:
            st.success("تم الحفظ بنجاح! حدث الصفحة لرؤية النتائج.")
            st.balloons()
            st.cache_data.clear()
        else:
            st.error("فشل الإرسال.")
    except:
        st.error("خطأ في الاتصال.")
