import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الثبات ومنع القفز
st.set_page_config(page_title="Race Master V67.1 - Secure Sync", layout="wide")

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

# حساب الإحصائيات (نسبة النجاح وإجمالي الجولات)
accuracy, total_rounds = 0, 0
if not df.empty:
    total_rounds = len(df)
    recent_100 = df.tail(100)
    # حساب الدقة: مقارنة العمود 8 (Actual) بالعمود 9 (Prediction)
    correct = len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]])
    accuracy = (correct / len(recent_100)) * 100 if len(recent_100) > 0 else 0

tab1, tab2 = st.tabs(["🚀 غرفة العمليات (ترحيل آمن)", "🔬 مختبر الفلترة (تحليل عميق)"])

# --- التاب الأول: غرفة العمليات ---
with tab1:
    st.markdown(f"### 📈 الدقة الحالية: `{accuracy:.1f}%` | 📊 إجمالي الجولات في الشيت: `{total_rounds}`")
    
    with st.container(border=True):
        st.subheader("🏁 تحديد النمط الحالي")
        c_cols = st.columns(3)
        v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ir_cols = st.columns([1, 2])
        vp = ir_cols[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir_cols[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    # تحليل السيرفر وآخر ظهور للنمط
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    current_prediction = v1 # قيمة افتراضية للتوقع
    
    if not matches.empty:
        last_m = matches.iloc[-1]
        st.info(f"🔄 **آخر ظهور:** فاز **{last_m.iloc[8]}** | الأطول: **{last_m.iloc[7]}**")
        
        for path in ["L", "C", "R"]:
            specific = matches[matches.iloc[:, 7] == path]
            if not specific.empty and len(specific.iloc[:, 8].unique()) == 1:
                winner = specific.iloc[0, 8]
                st.success(f"🌟 **نمط ذهبي:** إذا كان الأطول **{path}** ارهن على **{winner}**")
                current_prediction = winner
    else:
        st.warning("🆕 نمط جديد كلياً في قاعدة البيانات.")

    # نموذج الترحيل الثابت (st.form لمنع القفز)
    with st.form("secure_entry_form"):
        st.subheader("📥 إكمال البيانات والترحيل إلى Google Sheets")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        f_cols = st.columns(2)
        lp = f_cols[0].radio("المسار الأطول (LP)", ["L", "C", "R"], horizontal=True)
        aw = f_cols[1].selectbox("من الفائز الفعلي؟", [v1, v2, v3])
        
        submit = st.form_submit_button("🚀 ترحيل وحفظ الجولة الآن", use_container_width=True)
        
        if submit:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": current_prediction
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.ok:
                    st.balloons()
                    st.success("✅ تم الترحيل بنجاح إلى غوغل شيت!")
                    time.sleep(1.5)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ فشل الترحيل: السيرفر لم يستجب.")
            except:
                st.error("❌ خطأ في الاتصال: تأكد من الإنترنت.")

# --- التاب الثاني: مختبر الفلترة (المثبت) ---
with tab2:
    st.header("🔬 مختبر الفلترة والتحليل العميق")
    if not df.empty:
        with st.container(border=True):
            st.subheader("🔎 البحث عن نمط تاريخي")
            fx = st.columns(3)
            fv1 = fx[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
            fv2 = fx[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
            fv3 = fx[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')
            
            f_road_cols = st.columns(2)
            f_vp = f_road_cols[0].radio("موقع الظاهر", ["L", "C", "R"], key='f_vp_lab', horizontal=True)
            f_vt = f_road_cols[1].selectbox("نوع الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='f_vt_lab')

        # تطبيق الفلترة للمختبر
        lab_results = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, pos_map[f_vp]] == f_vt)]
        
        st.write(f"📊 عدد الجولات المكتشفة: **{len(lab_results)}**")
        if not lab_results.empty:
            # عرض الأعمدة: التوقيت، الطرق الثلاثة، الأطول، الفائز
            view_df = lab_results.iloc[:, [0, 4, 5, 6, 7, 8]]
            view_df.columns = ['التوقيت', 'طريق L', 'طريق C', 'طريق R', 'الأطول', 'الفائز الفعلي']
            st.dataframe(view_df, use_container_width=True)
