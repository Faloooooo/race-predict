import streamlit as st
import pandas as pd
import requests

# الروابط الرسمية (تم التأكد منها من رابط المعاينة الخاص بك)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Master Pro V5.5", layout="wide", page_icon="🏎️")

# دالة جلب البيانات مع تجاوز التخزين المؤقت
@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية: تحليل الأداء ---
st.sidebar.title("📈 لوحة التحكم")
if not df.empty:
    total_races = len(df.dropna(subset=[df.columns[1]]))
    st.sidebar.metric("🔢 إجمالي السباقات", total_races)
    
    # حساب الدقة من العمود J (Index 9) مقارنة بالفائز الفعلي I (Index 8)
    if df.shape[1] >= 10:
        valid_rows = df.dropna(subset=[df.columns[8], df.columns[9]])
        if not valid_rows.empty:
            correct = (valid_rows.iloc[:, 8].astype(str).str.strip() == 
                       valid_rows.iloc[:, 9].astype(str).str.strip()).sum()
            acc = (correct / len(valid_rows)) * 100
            st.sidebar.metric("🎯 دقة الخوارزمية", f"{round(acc, 1)}%")

# --- واجهة التوقع الذكي ---
st.title("🧠 محرك التنبؤ بالسباقات")

with st.container(border=True):
    col_cars = st.columns(3)
    v1 = col_cars[0].selectbox("سيارة اليسار (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col_cars[1].selectbox("سيارة الوسط (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col_cars[2].selectbox("سيارة اليمين (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    col_road = st.columns(2)
    vis_pos = col_road[0].radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_road[1].selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية البحث عن النمط (Pattern Recognition)
    prediction = v1
    if not df.empty:
        # البحث في التاريخ عن نفس نوع الطريق المرئي في نفس الموقع
        pos_idx = {"L": 4, "C": 5, "R": 6} # ترتيب الأعمدة في الشيت الخاص بك
        match_idx = pos_idx[vis_pos]
        history = df[df.iloc[:, match_idx] == vis_type]
        if not history.empty:
            # فلترة النتائج للسيارات الثلاث الحالية فقط
            potential_winners = history[history.iloc[:, 8].isin([v1, v2, v3])]
            if not potential_winners.empty:
                prediction = potential_winners.iloc[:, 8].value_counts().idxmax()
    
    st.subheader(f"🏁 التوقع البرمجي: :green[{prediction}]")

# --- واجهة إدخال النتائج ---
st.divider()
st.subheader("📝 تسجيل بيانات الجولة المكتملة")

others = [p for p in ["L", "C", "R"] if p != vis_pos]
col_hidden = st.columns(2)
h1_type = col_hidden[0].selectbox(f"نوع طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
h2_type = col_hidden[1].selectbox(f"نوع طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")

col_final = st.columns(2)
lp_pos = col_final[0].radio("موقع المسار الأطول", ["L", "C", "R"], horizontal=True)
actual_winner = col_final[1].selectbox("الفائز الفعلي في السباق", [v1, v2, v3])

if st.button("🚀 تدوين البيانات وحفظ التوقع في العمود J", use_container_width=True):
    # ترتيب أنواع الطرق بناءً على مواقعها الثابتة L, C, R
    road_map = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
    
    # حزمة البيانات الموحدة (إرسال كل شيء في طلب واحد لضمان سطر واحد)
    payload = {
        "entry.1815594157": v1,
        "entry.1382952591": v2,
        "entry.734801074": v3,
        "entry.189628538": road_map["L"],
        "entry.725223032": road_map["C"],
        "entry.1054834699": road_map["R"],
        "entry.21622378": lp_pos,
        "entry.77901429": actual_winner,
        "entry.1444222044": prediction # حقل Prediction الذي يصب في العمود J
    }
    
    try:
        response = requests.post(FORM_URL, data=payload)
        if response.status_code == 200:
            st.success(f"✅ تم بنجاح! التوقع ({prediction}) سُجل في نفس سطر الفائز ({actual_winner}) بالعمود J.")
            st.balloons()
        else:
            st.error("فشل الإرسال. تأكد من اتصال الإنترنت.")
    except:
        st.error("حدث خطأ في الخادم.")
