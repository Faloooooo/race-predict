import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence V29.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- محرك التوقع المزدوج ---
def dual_engine_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    car_at_pos = v1 if v_pos == "L" else v2 if v_pos == "C" else v3
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # وزن الطريق (قوة السيارة في هذا المناخ)
        road_wins = len(data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)])
        scores[car] += road_wins * 3.0
        # وزن القوة العامة (تراتبية السيارة في اللعبة)
        total_wins = len(data[data.iloc[:, 8] == car])
        scores[car] += total_wins * 0.5

    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_res[0][0], sorted_res[1][0]

# --- لوحة التحكم العلوية ---
st.title("🏆 محرك التوقعات المزدوج (V29.1)")

if not df.empty:
    total = len(df)
    valid_preds = df.dropna(subset=[df.columns[8], df.columns[9]])
    correct = len(valid_preds[valid_preds.iloc[:, 8] == valid_preds.iloc[:, 9]])
    rate = (correct / len(valid_preds)) * 100 if len(valid_preds) > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الجولات", f"{total}")
    c2.metric("دقة التوقع (Win Rate)", f"{rate:.1f}%")
    c3.metric("حالة القاعدة", "محدثة ✅")
else:
    st.info("بانتظار البيانات الإحصائية...")

st.divider()

# --- المدخلات ---
with st.container(border=True):
    col_in = st.columns(3)
    v1 = col_in[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_in[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_in[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2 = dual_engine_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    res1, res2 = st.columns(2)
    res1.success(f"🥇 الخيار الأول: **{p1}**")
    res2.warning(f"🥈 الخيار الثاني: **{p2}**")

# --- نموذج التسجيل السريع ---
with st.expander("📝 تسجيل وحفظ الجولة الحالية"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("أيهما كان المسار الأطول؟", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي في السباق", [v1, v2, v3], key="aw")

    # زر الحفظ مع استجابة بصرية
    if st.button("🚀 إرسال البيانات إلى السحابة", use_container_width=True):
        r_map = {vp: vt, others[0]: h1_t, others[1]: h2_t}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        
        try:
            resp = requests.post(FORM_URL, data=payload)
            if resp.ok:
                st.balloons() # احتفال بسيط عند النجاح
                st.toast('تم الحفظ بنجاح! جاري تحديث العدادات...', icon='✅')
                time.sleep(1) # مهلة بسيطة ليرى المستخدم التأكيد
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("فشل في الإرسال، تأكد من اتصال الإنترنت.")
        except:
            st.error("خطأ في الاتصال بالسيرفر.")
