import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

# إعداد الصفحة والاتصال بجوجل شيت
st.set_page_config(page_title="Race Predictor Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# تحميل البيانات الموجودة في الجدول حالياً
try:
    existing_data = conn.read(ttl=0) # ttl=0 لضمان جلب أحدث البيانات دائماً
except:
    existing_data = pd.DataFrame(columns=["Car1", "Car2", "Car3", "Road_L", "Road_C", "Road_R", "Long_Pos", "Winner"])

st.title("🏎️ خوارزمية السباق الذكية (L-C-R Analysis)")

# --- القسم 1: التوقع الاستباقي ---
with st.container():
    st.subheader("🔮 توقع الجولة القادمة")
    col_v, col_r = st.columns([2, 1])
    
    with col_v:
        c1 = st.selectbox("السيارة الأولى", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
        c2 = st.selectbox("السيارة الثانية", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
        c3 = st.selectbox("السيارة الثالثة", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    with col_r:
        known_road = st.selectbox("الطريق الظاهر الآن", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        pos = st.radio("موقع الطريق الظاهر", ["L (شمال)", "C (وسط)", "R (يمين)"])

    if st.button("🚀 تحليل الاحتمالات"):
        # هنا الكود يحلل الأنماط التاريخية
        # إذا وجد أن اللعبة تضع "Truck" كفائز عندما يكون الطريق الأول "Dirt" في جهة "L"
        # سيعطيها نسبة أعلى.
        st.info("جاري تحليل النمط التاريخي بناءً على {} جولة سابقة...".format(len(existing_data)))
        # (كود المحاكاة المتقدم سيضاف هنا)

st.markdown("---")

# --- القسم 2: تسجيل الداتا (بعد انتهاء الجولة) ---
with st.expander("📥 تسجيل نتائج الجولة بدقة (تغذية الذكاء الاصطناعي)"):
    st.write("أدخل ما حدث في الجولة الفعلية لفك شفرة الخوارزمية:")
    
    c_list = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
    r_list = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        res_l = st.selectbox("طريق الشمال (L)", r_list, key="res_l")
    with col_b:
        res_c = st.selectbox("طريق الوسط (C)", r_list, key="res_c")
    with col_c:
        res_r = st.selectbox("طريق اليمين (R)", r_list, key="res_r")
    
    long_pos = st.radio("أين كان الطريق الأطول؟", ["L", "C", "R"], horizontal=True)
    actual_winner = st.selectbox("من فاز فعلياً؟", c_list)

    if st.button("✅ حفظ وتحديث الخوارزمية"):
        new_row = pd.DataFrame([{
            "Car1": c1, "Car2": c2, "Car3": c3,
            "Road_L": res_l, "Road_C": res_c, "Road_R": res_r,
            "Long_Pos": long_pos, "Winner": actual_winner
        }])
        
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success("تم الحفظ في Google Sheets بنجاح! شكراً لمساهمتك في تطوير الذكاء.")
        st.balloons()
