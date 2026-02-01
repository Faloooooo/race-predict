import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V30.2 - Stable", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        # إضافة بارامتر عشوائي لضمان عدم قراءة نسخة قديمة من الذاكرة
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except Exception as e:
        return pd.DataFrame()

df = fetch_data()

# --- محرك التحليل المتقدم ---
def advanced_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, 33
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن التطابق المباشر في نفس المسار
        match = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        scores[car] += len(match) * 6.0 # رفعنا الوزن هنا لزيادة الدقة
        
        # وزن الأداء العام
        scores[car] += len(data[data.iloc[:, 8] == car]) * 0.4

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]
    
    total = sum(scores.values())
    conf = (scores[p1] / total * 100) if total > 0 else 33
    return p1, p2, conf

# --- اللوحة العلوية ---
st.title("🛡️ محرك السباق المستقر (V30.2)")

if not df.empty:
    total = len(df) # سيقرأ 406 أو أكثر
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات المسجلة", f"{total}")
    c2.metric("دقة النظام", f"{rate:.1f}%")
    c3.metric("جودة البيانات", "عالية (400+)" if total > 400 else "متوسطة")

st.divider()

# --- التوقعات والمدخلات ---
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, conf = advanced_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    res1, res2 = st.columns(2)
    res1.success(f"🥇 الخيار الأول: {p1} (قوة: {conf:.0f}%)")
    res2.warning(f"🥈 الخيار الثاني: {p2}")

# --- التسجيل الآمن ---
with st.expander("📥 تسجيل الجولة"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")

    if st.button("🚀 تحديث البيانات", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        try:
            r = requests.post(FORM_URL, data=payload, timeout=10) # أضفنا مهلة 10 ثوانٍ
            if r.status_code == 200:
                st.balloons()
                st.toast("تم الإرسال بنجاح!", icon='🎉')
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"فشل الإرسال (رمز الخطأ: {r.status_code}). حاول مرة أخرى.")
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}. يرجى التأكد من الإنترنت.")
