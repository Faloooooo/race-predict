import streamlit as st
import pandas as pd
import requests

# الروابط الأساسية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro V3.6", layout="wide", page_icon="🏎️")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (تحليل الربح المتقدم) ---
st.sidebar.title("🎮 رادار الخوارزمية")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات", total_races)
    
    # حساب الدقة بناءً على "آخر نمط مكتشف"
    correct_p = 0
    total_p = 0
    # نركز على آخر 30 جولة لاكتشاف إذا كانت اللعبة غيرت نمطها مؤخراً
    recent_df = df.tail(30)
    for i in range(5, len(recent_df)):
        past = recent_df.iloc[:i]
        curr = recent_df.iloc[i]
        actual = str(curr.iloc[8])
        lp_pos = str(curr.iloc[6]).strip().upper()
        
        # محاكاة التوقع بناءً على المسار الأطول
        match = past[past.iloc[:, 6] == lp_pos]
        if not match.empty:
            predicted = str(match.iloc[:, 8].value_counts().idxmax())
            if predicted == actual:
                correct_p += 1
            total_p += 1
    
    accuracy = (correct_p / total_p * 100) if total_p > 0 else 33.3
    st.sidebar.metric("🎯 نسبة الربح (النمط الحالي)", f"{round(accuracy, 1)}%")
    st.sidebar.progress(min(accuracy/100, 1.0))
    
    # تحليل الذكاء الاصطناعي للوضع الحالي
    if accuracy > 40:
        st.sidebar.success("✅ تم كسر العشوائية! النمط بدأ يتضح.")
    else:
        st.sidebar.info("🔄 اللعبة في وضع التدوير العشوائي حالياً.")

page = st.sidebar.radio("التنقل:", ["🔮 محرك التنبؤ", "📊 مصفوفة القوة المستهدفة"])

# ---------------------------------------------------------
# محرك التنبؤ V3.6
# ---------------------------------------------------------
if page == "🔮 محرك التنبؤ":
    st.title("🧠 محرك التوقع المتقدم")
    
    with st.container(border=True):
        st.subheader("🏁 بيانات السباق القادم")
        c_v = st.columns(3)
        c1 = c_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
        c2 = c_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
        c3 = c_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
        
        st.divider()
        c_t = st.columns(2)
        lp_type = c_t[0].selectbox("نوع الطريق (المسار الأطول)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp_pos = c_t[1].radio("موقع المسار الأطول", ["L", "C", "R"], horizontal=True)
        
        # منطق التوقع الخارق
        final_prediction = "تحليل..."
        if not df.empty:
            # فلترة مزدوجة: الموقع + نوع الطريق في ذلك الموقع
            pos_map = {"L": 3, "C": 4, "R": 5}
            idx = pos_map[lp_pos]
            condition = (df.iloc[:, 6] == lp_pos) & (df.iloc[:, idx] == lp_type)
            match = df[condition & df.iloc[:, 8].isin([c1, c2, c3])]
            
            if not match.empty:
                final_prediction = match.iloc[:, 8].value_counts().idxmax()
                confidence = (match.iloc[:, 8].value_counts().max() / len(match)) * 100
                st.info(f"💡 درجة الثقة في هذا المسار: {round(confidence, 1)}%")
            else:
                # إذا لم توجد بيانات للمسار، نبحث عن أداء السيارات العام في هذا النوع من الطرق
                alt_match = df[(df.iloc[:, 3] == lp_type) | (df.iloc[:, 4] == lp_type) | (df.iloc[:, 5] == lp_type)]
                alt_match = alt_match[alt_match.iloc[:, 8].isin([c1, c2, c3])]
                if not alt_match.empty:
                    final_prediction = alt_match.iloc[:, 8].value_counts().idxmax()
                else:
                    final_prediction = c1 # خيار افتراضي

        st.success(f"🏆 الفائز المتوقع: **{final_prediction}**")

    with st.expander("💾 تسجيل الجولة"):
        win_act = st.selectbox("من فاز فعلياً؟", [c1, c2, c3])
        if st.button("✅ حفظ وتحديث القاعدة"):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": lp_type, # تسجيل نوع الطريق الأطول
                "entry.21622378": lp_pos,
                "entry.77901429": win_act
            }
            requests.post(FORM_URL, data=payload)
            st.success("تم التسجيل! الخوارزمية تحلل البيانات الآن...")

# ---------------------------------------------------------
# مصفوفة القوة
# ---------------------------------------------------------
elif page == "📊 مصفوفة القوة المستهدفة":
    st.title("📊 مصفوفة " + lp_type if 'lp_type' in locals() else "تحليل الطرق")
    if not df.empty:
        st.subheader("🔥 السيارات الأكثر سيطرة حسب نوع الطريق")
        road_types = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]
        results = []
        for rt in road_types:
            # البحث عن الجولات التي كان فيها هذا الطريق هو الأطول وفازت فيه سيارة
            wins = df[(df.iloc[:, 3] == rt) | (df.iloc[:, 4] == rt) | (df.iloc[:, 5] == rt)].iloc[:, 8]
            if not wins.empty:
                results.append({"الطريق": rt, "السيارة الملك": wins.value_counts().idxmax(), "مرات الفوز": wins.value_counts().max()})
        st.table(pd.DataFrame(results))
