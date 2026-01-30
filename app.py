import streamlit as st
import pandas as pd
import requests

# روابط البيانات الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro V3.3", layout="wide", page_icon="🏎️")

@st.cache_data(ttl=2) # تحديث فائق السرعة
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (عداد الذكاء والربح) ---
st.sidebar.title("🏎️ لوحة البيانات الذكية")

if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)
    
    # خوارزمية حساب نسبة النجاح (Prediction Accuracy)
    correct_p = 0
    total_a = 0
    for i in range(15, len(df)): # البدء بعد 15 جولة للنضج الإحصائي
        past = df.iloc[:i]
        curr = df.iloc[i]
        competitors = [str(curr.iloc[0]), str(curr.iloc[1]), str(curr.iloc[2])]
        actual = str(curr.iloc[8])
        lp_pos = str(curr.iloc[6]).strip().upper()
        
        # محاكاة التوقع المعتمد على الطريق الأطول
        match = past[(past.iloc[:, 6] == lp_pos) & (past.iloc[:, 8].isin(competitors))]
        if not match.empty:
            if str(match.iloc[:, 8].value_counts().idxmax()) == actual:
                correct_p += 1
            total_a += 1
            
    accuracy = (correct_p / total_a * 100) if total_a > 0 else 33.3
    st.sidebar.metric("🎯 نسبة الربح المتوقعة", f"{round(accuracy, 1)}%")
    
    # شريط التقدم للوصول للهدف (95%)
    target_progress = min(accuracy / 95, 1.0)
    st.sidebar.write(f"التقدم نحو الهدف (95%):")
    st.sidebar.progress(target_progress)
    
    if accuracy >= 80:
        st.sidebar.success("🔥 النظام يقترب من كسر الخوارزمية!")
else:
    total_races = 0

st.sidebar.divider()
page = st.sidebar.radio("التنقل:", ["🔮 المحرك التنبؤي", "📊 مصفوفة القوة"])

# ---------------------------------------------------------
# محرك التنبؤ V3.3 (الارتباط الشرطي المتقدم)
# ---------------------------------------------------------
if page == "🔮 المحرك التنبؤي":
    st.title("🧠 محرك التنبؤ الخارق - V3.3")
    
    with st.container(border=True):
        st.subheader("🏁 مدخلات السباق الحالي")
        c_v = st.columns(3)
        c1 = c_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
        c2 = c_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
        c3 = c_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
        
        st.divider()
        c_t = st.columns(2)
        lp_type = c_t[0].selectbox("نوع الطريق الأطول", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp_pos = c_t[1].radio("موقع المسار الأطول", ["L", "C", "R"], horizontal=True)
        
        if st.button("🚀 استنتاج الفائز الأرجح", use_container_width=True):
            if not df.empty:
                pos_map = {"L": 3, "C": 4, "R": 5}
                # البحث في الحالات المتطابقة تماماً (الطريق الأطول + الموقع + النوع)
                condition = (df.iloc[:, 6] == lp_pos) & (df.iloc[:, pos_map[lp_pos]] == lp_type)
                match = df[condition & df.iloc[:, 8].isin([c1, c2, c3])]
                
                if not match.empty:
                    stats = match.iloc[:, 8].value_counts()
                    best = stats.idxmax()
                    conf = (stats.max() / stats.sum()) * 100
                    st.success(f"🏆 النتيجة المرجحة: **{best}**")
                    st.info(f"📊 درجة الثقة اللحظية: {round(conf, 1)}% بناءً على مواقف سابقة.")
                else:
                    # تحليل القوة العامة للسيارات المختارة
                    gen_match = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                    if not gen_match.empty:
                        st.warning(f"لا توجد مواجهة سابقة في هذا المسار، ولكن الأفضل تاريخياً بين هذه الثلاثة هو: **{gen_match.value_counts().idxmax()}**")
            else:
                st.error("قاعدة البيانات لا تزال فارغة.")

    with st.expander("💾 تسجيل البيانات (جولات جديدة)"):
        c_reg = st.columns(3)
        rl = c_reg[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_reg[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_reg[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp_act = st.radio("الأطول فعلياً", ["L", "C", "R"], horizontal=True, key="lp_act")
        win_act = st.selectbox("الفائز الفعلي", [c1, c2, c3], key="win_act")
        if st.button("✅ حفظ وتعلم"):
            payload = {"entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                       "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                       "entry.21622378": lp_act, "entry.77901429": win_act}
            requests.post(FORM_URL, data=payload)
            st.success(f"تمت إضافة الجولة رقم {total_races + 1}!")

# ---------------------------------------------------------
# مصفوفة القوة والبيانات
# ---------------------------------------------------------
elif page == "📊 مصفوفة القوة":
    st.title("📊 مصفوفة تحليل قوة السيارات")
    if not df.empty:
        st.subheader("🔥 ملك الطريق (أعلى نسبة فوز لكل تضريس)")
        road_types = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]
        matrix = []
        for rt in road_types:
            # البحث عن الجولات التي كان فيها هذا الطريق هو الحاسم (الأطول)
            wins = df[((df.iloc[:, 3] == rt) & (df.iloc[:, 6] == "L")) | 
                       ((df.iloc[:, 4] == rt) & (df.iloc[:, 6] == "C")) | 
                       ((df.iloc[:, 5] == rt) & (df.iloc[:, 6] == "R"))].iloc[:, 8]
            if not wins.empty:
                best = wins.value_counts().idxmax()
                matrix.append({"نوع الطريق": rt, "السيارة المتصدرة": best, "الانتصارات": wins.value_counts().max()})
        st.table(pd.DataFrame(matrix))
        
        st.divider()
        st.subheader("📉 التوزيع العام للانتصارات")
        st.bar_chart(df.iloc[:, 8].value_counts())
    else:
        st.info("سجل المزيد من البيانات لتظهر المصفوفة.")
