import streamlit as st
import pandas as pd
import requests
import time

# إعدادات الواجهة (ممنوع تغييرها)
st.set_page_config(page_title="Race Master V62.1 - Stabilized Edition", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_data()

# --- التنقل بين الغرف ---
tab1, tab2 = st.tabs(["🚀 غرفة العمليات (الترحيل)", "🔬 مختبر تحليل الأنماط (الفلترة)"])

# --- الغرفة الأولى: العمل والترحيل ---
with tab1:
    st.markdown("<h2 style='text-align: center;'>🛡️ كونسول العمليات V62.1</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        recent = df.tail(100)
        acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / len(recent) * 100) if not recent.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 الإجمالي", f"{len(df)} / 10,000")
        m2.metric("📈 دقة التوقعات", f"{acc:.1f}%")
        m3.progress(min(len(df)/10000, 1.0))

    st.divider()
    
    # --- نموذج الإدخال والتوقع (استخدام Form لمنع الرجة) ---
    with st.form("prediction_area"):
        st.subheader("🏁 بيانات الجولة والتوقع")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        
        ci = st.columns([1, 2])
        vp = ci[0].radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')
        
        # زر مخصص للتوقع داخل الفورم
        get_pred = st.form_submit_button("⚡ تحديث التوقع اللحظي", use_container_width=True)

    # محرك التوقع (يتم تفعيله عند الضغط أو الإدخال)
    recent_data = df.tail(600)
    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = recent_data[(recent_data.iloc[:, 1] == v1) & (recent_data.iloc[:, 2] == v2) & (recent_data.iloc[:, 3] == v3) & (recent_data.iloc[:, pos_map[vp]] == vt)]
    p1 = matches.iloc[-1, 8] if not matches.empty else v1
    
    if get_pred:
        st.success(f"🥇 التوقع الحالي بناءً على النمط: {p1}")
    else:
        st.info(f"💡 التوقع المقترح: {p1} (اضغط التحديث للتأكيد)")

    st.divider()
    
    # --- نموذج الترحيل (استخدام Form لضمان الثبات والبالونات) ---
    with st.form("upload_area"):
        st.subheader("📥 إرسال البيانات الكاملة")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_col = st.columns(2)
        h1 = h_col[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
        h2 = h_col[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
        
        f_col = st.columns(2)
        lp = f_col[0].radio("الأطول", ["L", "C", "R"], horizontal=True, key='lp')
        aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3], key='aw')

        submitted = st.form_submit_button("🚀 حفظ النمط وترحيل الداتا", use_container_width=True)

        if submitted:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.ok:
                    st.balloons()
                    st.success("✅ تم ترحيل وحفظ الجولة بنجاح!")
                    time.sleep(2) # مهلة ليرى المستخدم الرسالة
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ فشل الترحيل، تأكد من اتصال الإنترنت.")
            except:
                st.error("❌ حدث خطأ تقني أثناء الإرسال.")

# --- الغرفة الثانية: مختبر الفلترة (كما هي تماماً) ---
with tab2:
    st.header("🔬 مختبر الهندسة العكسية للأنماط")
    st.info("هنا يمكنك مقارنة الأنماط المتطابقة بدقة لمعرفة متى يغدر السيرفر.")

    with st.container(border=True):
        st.subheader("🔍 حدد النمط المراد فحصه")
        fx = st.columns(3)
        fv1 = fx[0].selectbox("سيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv1')
        fv2 = fx[1].selectbox("سيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv2')
        fv3 = fx[2].selectbox("سيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='fv3')

    if not df.empty:
        res = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3)]
        if not res.empty:
            st.write(f"✅ تم العثور على **{len(res)}** جولة بنفس ترتيب السيارات.")
            clean_res = res.iloc[:, [0, 4, 5, 6, 7, 8]]
            clean_res.columns = ['التوقيت', 'طريق L', 'طريق C', 'طريق R', 'المسار الأطول', 'الفائز الفعلي']
            st.dataframe(clean_res.style.highlight_max(axis=0, subset=['الفائز الفعلي']), use_container_width=True)
            st.divider()
            st.subheader("⚖️ تحليل التناقض في الظروف المتطابقة")
            duplicates = clean_res.groupby(['طريق L', 'طريق C', 'طريق R', 'المسار الأطول'])['الفائز الفعلي'].unique()
            for index, winners in duplicates.items():
                if len(winners) > 1:
                    st.error(f"⚠️ **تناقض صارخ:** في نمط الطرق {index}، الفائز يتغير بين: {list(winners)}")
                else:
                    st.success(f"💎 **نمط ذهبي:** في نمط الطرق {index}، الفائز دائماً هو: {winners[0]}")
        else:
            st.warning("هذا النمط من السيارات لم يظهر في قاعدة بياناتك من قبل.")
