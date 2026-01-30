import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V4.1", layout="wide", page_icon="🧠")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (ذكاء البيانات) ---
st.sidebar.title("🧠 مركز البيانات")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات في الذاكرة", total_races)
    
    # حساب نسبة النجاح الفعلية (مقارنة عمود الفائز الفعلي بالسيارة المتوقعة إذا توفرت)
    # ملاحظة: سنبدأ برؤية نتائج حقيقية بعد تسجيل عدة جولات بالكود الجديد
    st.sidebar.info("سيتم تحليل دقة التوقع بناءً على العمود الجديد في الجولات القادمة.")

# ---------------------------------------------------------
# مرحلة التنبؤ (قبل الحدث)
# ---------------------------------------------------------
st.title("🔮 التنبؤ وبناء الخوارزمية")

with st.container(border=True):
    st.subheader("🏁 مدخلات ما قبل الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    col_vis, col_type = st.columns(2)
    vis_pos = col_vis.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_type.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # عملية التوقع الذكي
    predicted_winner = "N/A"
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        # البحث عن أنماط مشابهة للطريق المرئي
        matches = df[df.iloc[:, idx] == vis_type]
        if not matches.empty:
            sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            if not sub_match.empty:
                predicted_winner = sub_match.iloc[:, 8].value_counts().idxmax()
            else:
                predicted_winner = df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]
        else:
            predicted_winner = v1 # خيار افتراضي في حال انعدام البيانات

    st.subheader(f"🏆 الفائز المتوقع: :green[{predicted_winner}]")

# ---------------------------------------------------------
# مرحلة التدوين (بعد الحدث)
# ---------------------------------------------------------
with st.expander("📝 تدوين النتائج وكشف الطرق المخفية"):
    st.write("املأ البيانات لتدريب الخوارزمية على محاكاة اللعبة:")
    
    others = [p for p in ["L", "C", "R"] if p != vis_pos]
    c_hid = st.columns(2)
    h1_type = c_hid[0].selectbox(f"نوع الطريق المخفي ({others[0]})", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2_type = c_hid[1].selectbox(f"نوع الطريق المخفي ({others[1]})", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    lp_pos = st.radio("موقع الطريق الأطول فعلياً", ["L", "C", "R"], horizontal=True)
    actual_winner = st.selectbox("الفائز الفعلي", [v1, v2, v3])

    if st.button("✅ حفظ في Google Sheets", use_container_width=True):
        roads = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
        
        # إرسال البيانات بما في ذلك التوقع التلقائي
        payload = {
            "entry.1815594157": v1, "entry.1382952591": v2, "entry.734801074": v3,
            "entry.189628538": roads["L"], "entry.725223032": roads["C"], "entry.1054834699": roads["R"],
            "entry.21622378": lp_pos, 
            "entry.77901429": actual_winner,
            "entry.1017387431": predicted_winner  # ربط التوقع بالخانة الجديدة
        }
        
        try:
            requests.post(FORM_URL, data=payload)
            st.success(f"تم التسجيل! التوقع كان ({predicted_winner}) والنتيجة كانت ({actual_winner})")
            st.balloons()
        except:
            st.error("فشل الاتصال بـ Google Sheets")
