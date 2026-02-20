import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V61.0 - Reverse Engineering", layout="wide")

SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        return pd.read_csv(f"{SHEET_READ_URL}&cb={time.time()}").dropna(subset=['Car 1 '])
    except: return pd.DataFrame()

df = load_data()

# --- واجهة التطبيق الرئيسية ---
tab1, tab2 = st.tabs(["🎮 غرفة العمليات والترحيل", "🔍 مختبر تحليل الخوارزمية (الفلترة)"])

# --- التاب الأول: العمل المعتاد ---
with tab1:
    st.subheader("إدخال الجولات الحالية")
    # (هنا يوضع كود الترحيل والعدادات كما في النسخ السابقة لضمان استمرارية العمل)
    st.info("استخدم هذا القسم لإدخال الجولات الجديدة كما تفعل دائماً.")

# --- التاب الثاني: مختبر الفلترة العميقة (اقتراحك) ---
with tab2:
    st.header("🔬 رادار كشف أنماط السيرفر")
    st.write("ضع تفاصيل النمط الذي تشك فيه، وسأظهر لك تاريخه الكامل.")

    with st.container(border=True):
        f_col = st.columns(3)
        fv1 = f_col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = f_col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = f_col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
        
        f_road = st.columns([1, 2])
        fvp = f_road[0].radio("موقع الظاهر", ["L", "C", "R"], key='fvp', horizontal=True)
        fvt = f_road[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='fvt')

    if not df.empty:
        # عملية الفلترة بناءً على اقتراحك
        pos_map = {"L": 4, "C": 5, "R": 6}
        results = df[
            (df.iloc[:, 1] == fv1) & 
            (df.iloc[:, 2] == fv2) & 
            (df.iloc[:, 3] == fv3) &
            (df.iloc[:, pos_map[fvp]] == fvt)
        ]

        st.subheader(f"📊 نتائج الفحص: تم العثور على ({len(results)}) تكرار")

        if not results.empty:
            # عرض البيانات بالتفصيل (الطرق المخفية، المسار الأطول، الفائز)
            # سنعرض الأعمدة من 4 إلى 9 (الطرق، المسار الأطول، الفائز، التوقع)
            display_df = results.iloc[:, [0, 4, 5, 6, 7, 8, 9]]
            display_df.columns = ['التوقيت', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز الفعلي', 'توقع الكود']
            
            st.dataframe(display_df, use_container_width=True)

            # تحليل ذكي للتناقضات
            unique_winners = results.iloc[:, 8].unique()
            if len(unique_winners) > 1:
                st.warning(f"⚠️ تنبيه: هذا النمط مضلل! فاز فيه سابقاً كل من: {', '.join(unique_winners)}")
            else:
                st.success(f"✅ نمط مستقر: الفائز دائماً هو {unique_winners[0]}")
        else:
            st.error("لم يسبق رصد هذا النمط في قاعدة بياناتك حتى الآن.")

st.divider()
