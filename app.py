import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence V28.2", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        # تعديل مهم: التأكد من وجود بيانات حقيقية في الأعمدة الأساسية
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- خوارزمية البصمة المستقلة المحسنة ---
def fingerprint_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1
    
    current_cars = {v1, v2, v3}
    pos_map = {"L": 4, "C": 5, "R": 6}
    car_at_pos = v1 if v_pos == "L" else v2 if v_pos == "C" else v3
    
    # فلترة المواجهات المتشابهة
    mask_same_cars = data.apply(lambda row: {row.iloc[1], row.iloc[2], row.iloc[3]} == current_cars, axis=1)
    mask_specific = (data.iloc[:, pos_map[v_pos]] == v_type) & \
                    (data.iloc[:, 1 if v_pos=="L" else 2 if v_pos=="C" else 3] == car_at_pos)
    
    scores = {v1: 0, v2: 0, v3: 0}
    
    # إضافة النقاط مع حماية من الأخطاء
    for _, row in data[mask_same_cars].iterrows():
        winner = str(row.iloc[8])
        if winner in scores: scores[winner] += 2
        
    for _, row in data[mask_specific].iterrows():
        winner = str(row.iloc[8])
        if winner in scores: scores[winner] += 5
    
    prediction = max(scores, key=scores.get)
    return prediction if scores[prediction] > 0 else v1

# --- العرض الإحصائي ---
st.title("🎯 محرك البصمة الرقمية (V28.2)")

if not df.empty:
    total_rounds = len(df)
    # حساب نسبة النجاح (فقط للجولات التي تحتوي على توقع وفوز فعلي)
    valid_preds = df.dropna(subset=[df.columns[8], df.columns[9]])
    correct_hits = len(valid_preds[valid_preds.iloc[:, 8] == valid_preds.iloc[:, 9]])
    win_rate = (correct_hits / len(valid_preds)) * 100 if len(valid_preds) > 0 else 0

    col1, col2 = st.columns(2)
    col1.metric("الجولات المكتملة", f"{total_rounds}")
    col2.metric("دقة التوقع الحالية", f"{win_rate:.1f}%")
else:
    st.info("بانتظار مزيد من الجولات لتفعيل التحليل الإحصائي.")

st.divider()

# --- واجهة الإدخال والتوقع الفوري ---
with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = fingerprint_logic(v1, v2, v3, vp, vt, df)
    st.subheader(f"🔮 التوقع المقترح: :green[{prediction}]")

# --- نموذج الحفظ السريع ---
with st.expander("📥 تسجيل نتيجة السباق"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول (حسب الرؤية)", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ الجولة وتحديث الذكاء الاصطناعي", use_container_width=True):
    r_map = {vp: vt, others[0]: h1_t, others[1]: h2_t}
    payload = {
        "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
        "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
        "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(prediction)
    }
    try:
        if requests.post(FORM_URL, data=payload).ok:
            st.success("تم التحديث!")
            st.cache_data.clear()
            st.rerun()
    except Exception as e:
        st.error(f"فشل الاتصال: {e}")
