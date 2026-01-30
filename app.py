import streamlit as st
import pandas as pd
import requests
import time

# الروابط الثابتة (مؤكدة 100%)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V8.0", layout="wide", page_icon="🏁")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={time.time()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (الإحصائيات الحقيقية) ---
st.sidebar.title("📊 مركز تحليل البيانات")
if not df.empty and df.shape[1] >= 10:
    # فلترة السطور التي تحتوي على فائز (I) وتوقع (J)
    valid_df = df.dropna(subset=[df.columns[8], df.columns[9]])
    total_valid = len(valid_df)
    st.sidebar.metric("🔢 جولات مسجلة بـ J", total_valid)
    if total_valid > 0:
        correct = (valid_df.iloc[:, 8].astype(str).str.strip().lower() == 
                   valid_df.iloc[:, 9].astype(str).str.strip().lower()).sum()
        accuracy = (correct / total_valid) * 100
        st.sidebar.metric("🎯 الدقة التاريخية", f"{round(accuracy, 1)}%")

# --- واجهة التوقع ---
st.title("🧠 الخوارزمية الذكية (المصلحة)")

with st.container(border=True):
    col_c = st.columns(3)
    v1 = col_c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vis_pos = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # الخوارزمية المحسنة قليلاً
    prediction = v1
    if not df.empty:
        pos_map = {"L": 4, "C": 5, "R": 6}
        idx = pos_map[vis_pos]
        history = df[df.iloc[:, idx] == vis_type]
        if not history.empty:
            match_cars = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not match_cars.empty:
                prediction = match_cars.iloc[:, 8].value_counts().idxmax()

    st.subheader(f"🏆 الفائز المتوقع: :green[{prediction}]")

# --- واجهة تدوين النتائج ---
st.divider()
st.subheader("📝 تدوين النتائج (الإرسال القسري للعمود J)")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_t = c_hid[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_t = c_hid[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

lp_pos = st.radio("المسار الأطول فعلياً", ["L", "C", "R"], horizontal=True)
actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 تدوين البيانات وحفظ التوقع (العمود J)", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_t, others[1]: h2_t}
    
    # تحضير البيانات بصيغة نصية صرفة لضمان قبول جوجل لها
    payload = {
        "entry.1815594157": str(v1),
        "entry.1382952591": str(v2),
        "entry.734801074": str(v3),
        "entry.189628538": str(roads["L"]),
        "entry.725223032": str(roads["C"]),
        "entry.1054834699": str(roads["R"]),
        "entry.21622378": str(lp_pos),
        "entry.77901429": str(actual_w),
        "entry.1444222044": str(prediction) # الإرسال للعمود J
    }
    
    try:
        # استخدام ترويسة تحاكي المتصفح تماماً
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(FORM_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            st.success(f"✅ تم بنجاح! التوقع ({prediction}) سُجل الآن في العمود J.")
            st.balloons()
            st.cache_data.clear()
        else:
            st.error(f"فشل الإرسال. كود الخطأ: {response.status_code}")
    except:
        st.error("فشل الاتصال بخادم جوجل.")
