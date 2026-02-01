import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية (لا تتغير لضمان استقرار الشيت)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence V30.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        # فلترة البيانات لضمان وجود الفائز والتوقع لحساب النسبة بدقة
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- محرك التحليل الاحتمالي ---
def pattern_breaker_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, 33
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # حساب النقاط بناءً على تكرار الفوز في نفس الظروف
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        # 1. البحث عن قوة السيارة في هذا النوع من الطرق (وزن عالي)
        match_road = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        scores[car] += len(match_road) * 5.0
        
        # 2. البحث عن أداء السيارة العام (وزن تكميلي)
        total_wins = len(data[data.iloc[:, 8] == car])
        scores[car] += total_wins * 0.5

    # ترتيب النتائج لاستخراج الخيارين
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    p1 = sorted_res[0][0]
    p2 = sorted_res[1][0]
    
    # حساب نسبة ثقة تقريبية (بناءً على تفوق النقاط)
    total_score = sum(scores.values())
    confidence = (scores[p1] / total_score * 100) if total_score > 0 else 33
    
    return p1, p2, confidence

# --- لوحة التحكم والنسب الحية ---
st.title("🛡️ محرك كسر الأنماط المزدوج (V30.1)")

if not df.empty:
    total_rounds = len(df)
    # حساب نسبة الربح بناءً على عمود التوقع (9) وعمود الفائز (8)
    valid_data = df.dropna(subset=[df.columns[8], df.columns[9]])
    correct_hits = len(valid_data[valid_data.iloc[:, 8] == valid_data.iloc[:, 9]])
    win_rate = (correct_hits / len(valid_data)) * 100 if len(valid_data) > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الجولات", f"{total_rounds}")
    c2.metric("دقة التوقع (Win Rate)", f"{win_rate:.1f}%")
    c3.metric("ثبات النمط", "ممتاز ✨" if total_rounds > 400 else "جيد")
else:
    st.info("بانتظار البيانات الإحصائية لبدء التحليل...")

st.divider()

# --- واجهة الإدخال والتوقع ---
with st.container(border=True):
    col_in = st.columns(3)
    v1 = col_in[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_in[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_in[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # استدعاء المحرك
    p1, p2, conf = pattern_breaker_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    res1, res2 = st.columns(2)
    res1.success(f"🥇 التوقع الأساسي: **{p1}**")
    res2.warning(f"🥈 التوقع البديل: **{p2}**")
    
    st.progress(min(conf/100, 1.0), text=f"قوة ثبات النمط لهذا التوقع: {conf:.0f}%")

# --- تسجيل الجولة مع رد فعل بصري ---
with st.expander("📝 تسجيل وحفظ الجولة الحالية"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول؟", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")

    if st.button("🚀 إرسال البيانات وتحديث الذكاء الاصطناعي", use_container_width=True):
        r_map = {vp: vt, others[0]: h1_t, others[1]: h2_t}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.toast("✅ تم الإرسال بنجاح!", icon='🎉')
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("خطأ في الاتصال، حاول مرة أخرى.")
