import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الصفحة لمنع القفز والتمرير غير الضروري
st.set_page_config(page_title="Race Master V64 - Stability First", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_data()

# --- 1. العدادات والنسبة (Header) ---
if not df.empty:
    total_rounds = len(df)
    # حساب نسبة الربح بناءً على مطابقة التوقع للفائز الفعلي في الشيت
    correct_preds = len(df[df['Actual Winner '] == df['Prediction ']])
    win_rate = (correct_preds / total_rounds) * 100 if total_rounds > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 إجمالي الجولات", total_rounds)
    c2.metric("🎯 نسبة الربح العامة", f"{win_rate:.1f}%")
    c3.info(f"آخر تحديث: {time.strftime('%H:%M:%S')}")

st.divider()

# --- 2. منطقة الإدخال والتوقع (ثابتة) ---
tab1, tab2 = st.tabs(["🚀 إدخال وترحيل", "🔍 بحث وتدقيق"])

with tab1:
    # استخدام Form لمنع الصفحة من العودة للأعلى عند كل اختيار
    with st.form("main_input_form"):
        st.subheader("📝 تدوين بيانات الجولة")
        
        col1, col2, col3 = st.columns(3)
        cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
        v1 = col1.selectbox("السيارة L", cars, index=0)
        v2 = col2.selectbox("السيارة C", cars, index=1)
        v3 = col3.selectbox("السيارة R", cars, index=2)
        
        col_in1, col_in2 = st.columns([1, 2])
        vp = col_in1.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = col_in2.selectbox("طريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        st.write("---")
        st.subheader("🏁 النتائج والمخفي")
        
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_cols = st.columns(2)
        lp = f_cols[0].radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
        aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3])
        
        # التوقع الداخلي (يتم حسابه عند الضغط)
        submit_button = st.form_submit_button("🚀 حفظ الجولة وترحيلها الآن", use_container_width=True)

    if submit_button:
        # حساب التوقع للحفظ فقط
        pos_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3)]
        prediction = matches.iloc[-1, 8] if not matches.empty else v1
        
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": prediction
        }
        
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.ok:
                st.balloons() # بالونات التأكيد
                st.success(f"✅ تم الحفظ! جولة رقم {total_rounds + 1} أضيفت للسجل.")
                time.sleep(1)
                st.cache_data.clear() # تحديث العداد
                st.rerun()
            else:
                st.error("❌ فشل الترحيل، تأكد من اتصالك.")
        except:
            st.error("❌ عطل في الوصول للسيرفر.")

with tab2:
    st.subheader("🔬 أداة البحث السريع")
    search_cols = st.columns(3)
    s1 = search_cols[0].selectbox("L", cars, key="s1")
    s2 = search_cols[1].selectbox("C", cars, key="s2")
    s3 = search_cols[2].selectbox("R", cars, key="s3")
    
    result = df[(df.iloc[:, 1] == s1) & (df.iloc[:, 2] == s2) & (df.iloc[:, 3] == s3)]
    st.write(f"عدد الأنماط المطابقة: {len(result)}")
    st.dataframe(result, use_container_width=True)

