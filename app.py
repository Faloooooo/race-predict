import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V83.0 - The Core Logic", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_db()

# العدادات العلوية الثابتة
if not df.empty:
    m1, m2 = st.columns(2)
    m1.metric("📊 سجل البيانات", len(df))
    recent_100 = df.tail(100)
    acc = (len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]]) / len(recent_100)) * 100 if len(recent_100) > 0 else 0
    m2.metric("📈 دقة الخوارزمية %", f"{acc:.1f}%")
st.divider()

tab1, tab2 = st.tabs(["🚀 غرفة العمليات والتوقع", "🔬 مختبر التحليل المتقدم"])

with tab1:
    # إدخال البيانات - تم تعطيل التحديث التلقائي المهتز
    with st.form("input_form"):
        st.subheader("🏁 مدخلات الجولة السريعة")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        # زر التوقع لضمان عدم اهتزاز الصفحة أثناء الإدخال
        predict_btn = st.form_submit_button("⚡ تحليل النمط واستخراج التوقع", use_container_width=True)

    if predict_btn:
        p_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, p_map[vp]] == vt)]
        
        # --- منطق خوارزمية V62.0 ---
        if not matches.empty:
            # 1. معلومة أحدث جولة
            last_actual = matches.iloc[-1, 8]
            st.info(f"ℹ️ معلومة: أحدث جولة بهذا النمط فازت بها: {last_actual}")
            
            # 2. الخوارزمية الإحصائية للتوقع
            counts = matches.iloc[:, 8].value_counts()
            best_bet = counts.idxmax() # السيارة الأكثر فوزاً إحصائياً في هذا النمط
            
            st.markdown(f"""<div style="text-align: center; border: 3px solid #00FFCC; border-radius: 15px; padding: 20px; background-color: #0E1117;">
            <h2 style="color:white; margin:0;">🎯 التوقع بناءً على الخوارزمية:</h2>
            <h1 style="color:#00FFCC; font-size:60px; margin:10px;">{best_bet}</h1>
            </div>""", unsafe_allow_html=True)
            
            st.write("📊 **تفصيل فوز السيارات (إحصاء الوزن التاريخي):**")
            c_stats = st.columns(len(counts))
            for i, (car, count) in enumerate(counts.items()):
                c_stats[i].warning(f"**{car}**: فازت {count} مرة")
        else:
            st.warning("🆕 نمط جديد كلياً - لا توجد بيانات تاريخية.")

    st.divider()

    # قسم ترحيل البيانات (كامل المعلومات: الطرق المخفية + الأطول)
    with st.form("save_data_form"):
        st.subheader("📥 تدوين نتائج ما بعد السباق")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp = st.radio("المسار الأطول الفعلي (LP)", ["L", "C", "R"], horizontal=True)
        aw = st.selectbox("الفائز الفعلي في الجولة", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل وحفظ الجولة الآن", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": "V62_Logic"
            }
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تم حفظ الجولة بنجاح!")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()

with tab2:
    st.header("🔬 مختبر التحليل (فلترة الظاهر)")
    # (هنا وضعت الفلترة الضيقة التي تمنع تشتت الداتا)
    with st.container(border=True):
        st.write("🔎 ابحث عن جولات مطابقة (سيارات + ظاهر + موقع):")
        sf = st.columns([1,1,1,1,1])
        sv1 = sf[0].selectbox("Car 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f1')
        sv2 = sf[1].selectbox("Car 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f2')
        sv3 = sf[2].selectbox("Car 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f3')
        svp = sf[3].selectbox("موقع الظاهر", ["L", "C", "R"], key='fp')
        svt = sf[4].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='ft')

    idx = {"L": 4, "C": 5, "R": 6}
    res = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3) & (df.iloc[:, idx[svp]] == svt)]
    
    if not res.empty:
        st.dataframe(res.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8]], use_container_width=True)
    else:
        st.warning("لا توجد جولات مطابقة لهذا النمط المحدد.")
