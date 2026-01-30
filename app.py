import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V5.0", layout="wide", page_icon="🏁")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        # جلب البيانات والتأكد من وجود الفائز الفعلي (العمود I)
        return df_read.dropna(subset=[df_read.columns[8]]) 
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (عداد الجولات والنسبة) ---
st.sidebar.title("📊 مركز تحليل البيانات")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)
    
    # محاولة حساب الدقة بمقارنة الفائز الفعلي (العمود 8) مع التوقع (العمود 10 الجديد)
    if df.shape[1] >= 11: # التأكد من وجود عمود Prediction الجديد
        actual = df.iloc[:, 8].astype(str).str.strip()
        predicted = df.iloc[:, 10].astype(str).str.strip()
        correct = (actual == predicted).sum()
        accuracy = (correct / total_races) * 100 if total_races > 0 else 0
        st.sidebar.metric("🎯 دقة التوقع الحالية", f"{round(accuracy, 1)}%")
        st.sidebar.progress(min(accuracy/100, 1.0))

# --- القسم الأول: مدخلات ما قبل السباق (التنبؤ) ---
st.title("🔮 التنبؤ الذكي وبناء الخوارزمية")

with st.container(border=True):
    st.subheader("🏁 معطيات الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L) 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C) 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R) 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    col_vis, col_type = st.columns(2)
    vis_pos = col_vis.radio("موقع الطريق المرئي 4", ["L", "C", "R"], horizontal=True)
    vis_type = col_type.selectbox("نوع الطريق المرئي 5", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # الخوارزمية: التوقع بناءً على التاريخ
    pred_val = v1
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            pred_val = sub_match.iloc[:, 8].value_counts().idxmax() if not sub_match.empty else df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]

    st.subheader(f"🏆 الفائز المتوقع: :green[{pred_val}]")

# --- القسم الثاني: تدوين النتائج (ما بعد السباق) ---
st.divider()
st.subheader("📝 تدوين نتائج الجولة وكشف الطرق")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
c_hid = st.columns(2)
h1_type = c_hid[0].selectbox(f"نوع الطريق المخفي ({others[0]}) 6", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_type = c_hid[1].selectbox(f"نوع الطريق المخفي ({others[1]}) 7", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

st.divider()
col_res1, col_res2 = st.columns(2)
lp_pos = col_res1.radio("موقع الطريق الأطول فعلياً 8", ["L", "C", "R"], horizontal=True)
actual_winner = col_res2.selectbox("الفائز الفعلي 9", [v1, v2, v3])

if st.button("✅ حفظ في السجل وتدوين التوقع (10) Prediction", use_container_width=True):
    roads = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
    
    # إرسال البيانات للنموذج باستخدام الرموز الصحيحة
    payload = {
        "entry.1815594157": v1, 
        "entry.1382952591": v2, 
        "entry.734801074": v3,
        "entry.189628538": roads["L"], 
        "entry.725223032": roads["C"], 
        "entry.1054834699": roads["R"],
        "entry.21622378": lp_pos, 
        "entry.77901429": actual_winner,
        "entry.1444222044": str(pred_val) # الرمز الجديد لخانة Prediction
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.ok:
            st.success(f"تم التسجيل بنجاح! التوقع ({pred_val}) ظهر الآن في عمود Prediction.")
            st.balloons()
        else:
            st.error("تعذر وصول البيانات للنموذج.")
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال: {e}")
