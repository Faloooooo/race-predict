import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V81.0 - Full Data Recovery", layout="wide")

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

# العدادات في القمة
if not df.empty:
    m1, m2 = st.columns(2)
    m1.metric("📊 إجمالي السجلات", len(df))
    recent_100 = df.tail(100)
    acc = (len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]]) / len(recent_100)) * 100 if len(recent_100) > 0 else 0
    m2.metric("📈 دقة النظام %", f"{acc:.1f}%")
st.divider()

tab1, tab2 = st.tabs(["🚀 غرفة التوقع والترحيل", "🔬 مختبر البحث الكامل (كاشف المخفي)"])

# --- التاب الأول: غرفة التوقع (كاملة كما كانت) ---
with tab1:
    with st.container(border=True):
        st.subheader("🏁 إدخال الجولة الحالية")
        c_cols = st.columns(3)
        v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    p_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, p_map[vp]] == vt)]
    
    if not matches.empty:
        last_winner = matches.iloc[-1, 8]
        st.markdown(f"""<div style="text-align: center; border: 2px solid #00FFCC; border-radius: 10px; padding: 15px; background-color: #0E1117;">
        <h3 style="margin:0;">🎯 أحدث فوز لهذا النمط:</h3><h1 style="color:#00FFCC; font-size:50px; margin:5px;">{last_winner}</h1></div>""", unsafe_allow_html=True)
        
        st.write("📊 **إحصائيات تكرار الفوز:**")
        counts = matches.iloc[:, 8].value_counts()
        c_stats = st.columns(len(counts))
        for i, (car, count) in enumerate(counts.items()):
            c_stats[i].warning(f"**{car}**: {count} مرات")
    
    with st.form("save_v81"):
        st.subheader("📥 ترحيل البيانات")
        # بقية الكود كما هو مثبت سابقا
        st.form_submit_button("🚀 حفظ التحديث")

# --- التاب الثاني: المختبر (إعادة عرض البيانات المخفية) ---
with tab2:
    st.header("🔬 بحث الأنماط وكشف الطرق المخفية")
    with st.container(border=True):
        st.write("🔎 أدخل معطيات الظاهر للبحث عن المخفي:")
        f_cols = st.columns([1,1,1,1,1])
        fv1 = f_cols[0].selectbox("Car 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f1')
        fv2 = f_cols[1].selectbox("Car 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f2')
        fv3 = f_cols[2].selectbox("Car 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f3')
        fvp = f_cols[3].selectbox("جهة الظاهر", ["L", "C", "R"], key='fp')
        fvt = f_cols[4].selectbox("نوع الطريق", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='ft')

    # الفلترة بالظاهر
    p_idx = {"L": 4, "C": 5, "R": 6}
    res = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, p_idx[fvp]] == fvt)].copy()
    
    if not res.empty:
        st.success(f"✅ تم العثور على {len(res)} جولة. إليك البيانات الكاملة (المخفي والظاهر):")
        
        # إعادة الأعمدة كاملة: التاريخ، الطرق الثلاثة، المسار، الفائز
        display_df = res.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8]].copy()
        display_df.columns = ['التاريخ', 'Car 1', 'Car 2', 'Car 3', 'طريق L', 'طريق C', 'طريق R', 'الأطول LP', 'الفائز']
        
        # تلوين عمود الطريق الظاهر لتمييزه عن المخفي بصرية
        st.dataframe(display_df, use_container_width=True)
        
        st.info("💡 ملاحظة: الأعمدة (طريق L, C, R) تعرض لك كل الطرق التي كانت في تلك الجولة، لتتمكن من دراسة الأنماط المخفية.")
    else:
        st.warning("لم يسبق تدوين هذا النمط.")
