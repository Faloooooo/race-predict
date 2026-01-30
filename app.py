import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide", page_icon="🏎️")

def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("🎮 لوحة التحكم")
if not df.empty:
    total_races = len(df)
    st.sidebar.success(f"✅ متصل: {total_races} جولة")
    # حالة التعلم
    status = "مبتدئ" if total_races < 30 else "متوسط" if total_races < 70 else "خبير"
    st.sidebar.info(f"مستوى الذكاء: {status}")
else:
    total_races = 0

page = st.sidebar.radio("انتقل إلى:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محرك التوقع الذكي")
    
    with st.container(border=True):
        st.subheader("🔍 تحليل السباق القادم")
        c_v = st.columns(3)
        c1 = c_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = c_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = c_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        c_t = st.columns(2)
        current_road = c_t[0].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        road_pos = c_t[1].radio("موقع الطريق", ["L", "C", "R"], horizontal=True)
        
        if st.button("🚀 توقع النتيجة", use_container_width=True):
            if not df.empty:
                pos_map = {"L": 3, "C": 4, "R": 5}
                road_col_idx = pos_map[road_pos]
                
                # تحليل البيانات بناءً على الطريق والسيارات
                match = df[(df.iloc[:, road_col_idx] == current_road) & (df.iloc[:, 8].isin([c1, c2, c3]))]
                
                if not match.empty:
                    best_car = match.iloc[:, 8].value_counts().idxmax()
                    prob = (match.iloc[:, 8].value_counts().max() / len(match)) * 100
                    st.success(f"البرنامج يتوقع فوز: **{best_car}**")
                    st.info(f"نسبة الثقة في هذا الطريق: {round(prob, 1)}%")
                else:
                    # توقع عام إذا لم يوجد تطابق للطريق
                    gen_match = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                    if not gen_match.empty:
                        st.warning(f"لا توجد بيانات كافية لهذا الطريق، لكن تاريخياً الأفضل هو: **{gen_match.value_counts().idxmax()}**")
            else:
                st.error("قاعدة البيانات فارغة.")

    with st.expander("💾 تسجيل الجولة"):
        c_r = st.columns(3)
        rl = c_r[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("الأطول", ["L", "C", "R"], horizontal=True, key="lp_reg")
        win = st.selectbox("الفائز الفعلي", [c1, c2, c3], key="win_reg")

        if st.button("✅ حفظ البيانات"):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            requests.post(FORM_URL, data=payload)
            st.success("تم الحفظ!")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات ونسبة الربح الإجمالية
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 لوحة الأداء والربح الإجمالي")
    
    if not df.empty:
        # 1. حساب دقة البرنامج (Simulation)
        # سنقوم بمحاكاة توقع لكل جولة بناءً على ما قبله لحساب الدقة
        correct_preds = 0
        total_attempts = 0
        
        # لنبدأ الحساب بعد أول 10 جولات لتكون منطقية
        for i in range(10, len(df)):
            past_data = df.iloc[:i]
            current_row = df.iloc[i]
            
            # السيارات المتنافسة في تلك الجولة
            cars = [current_row.iloc[0], current_row.iloc[1], current_row.iloc[2]]
            actual_winner = current_row.iloc[8]
            
            # محاكاة توقع البرنامج
            match = past_data[past_data.iloc[:, 8].isin(cars)].iloc[:, 8]
            if not match.empty:
                predicted = match.value_counts().idxmax()
                if predicted == actual_winner:
                    correct_preds += 1
                total_attempts += 1
        
        accuracy = (correct_preds / total_attempts * 100) if total_attempts > 0 else 0
        
        # عرض المقياس الرئيسي
        st.subheader("🎯 دقة توقعات البرنامج")
        st.metric(label="نسبة الربح المتوقعة (إجمالاً)", value=f"{round(accuracy, 1)}%", help="هذه النسبة تمثل مدى نجاح البرنامج في توقع الفائز الصحيح بناءً على البيانات السابقة")
        st.progress(accuracy/100)

        st.divider()
        
        # 2. إحصائيات السيارات
        win_counts = df.iloc[:, 8].value_counts()
        st.subheader("🏁 توزيع الانتصارات الفعلي")
        st.bar_chart(win_counts)
        
        cols = st.columns(3)
        for i, (car, count) in enumerate(win_counts.items()):
            percent = (count / len(df)) * 100
            with cols[i % 3]:
                st.metric(f"🚗 {car}", f"{round(percent, 1)}%", f"{count} فوز")
                
    else:
        st.warning("تحتاج إلى تسجيل المزيد من البيانات لتوليد الإحصائيات.")
