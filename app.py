import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro V3.1", layout="wide", page_icon="🧠")

def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        # التأكد من وجود بيانات في عمود الفائز (Index 8) وعمود الموقع (Index 6)
        df_clean = df_read.dropna(subset=[df_read.columns[6], df_read.columns[8]])
        return df_clean
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية المصلحة ---
st.sidebar.title("🧠 عقل الخوارزمية")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)
    
    # حساب الدقة مع معالجة الأخطاء (Safe Mode)
    correct_p = 0
    total_a = 0
    pos_map = {"L": 3, "C": 4, "R": 5}
    
    for i in range(10, len(df)):
        curr = df.iloc[i]
        lp_pos = str(curr.iloc[6]).strip().upper() # تنظيف النص
        
        if lp_pos in pos_map:
            past = df.iloc[:i]
            cars = [str(curr.iloc[0]), str(curr.iloc[1]), str(curr.iloc[2])]
            actual = str(curr.iloc[8])
            rd_type = str(curr.iloc[pos_map[lp_pos]])
            
            # محاكاة التوقع
            match = past[(past.iloc[:, 6] == lp_pos) & (past.iloc[:, pos_map[lp_pos]] == rd_type)]
            match = match[match.iloc[:, 8].isin(cars)]
            
            if not match.empty:
                if str(match.iloc[:, 8].value_counts().idxmax()) == actual:
                    correct_p += 1
                total_a += 1
    
    accuracy = (correct_p / total_a * 100) if total_a > 0 else 33.3
    st.sidebar.metric("🎯 نسبة الربح الحالية", f"{round(accuracy, 1)}%")
    st.sidebar.progress(min(accuracy/100, 1.0))
else:
    total_races = 0

page = st.sidebar.radio("انتقل إلى:", ["🔮 محرك التنبؤ الخارق", "📊 مصفوفة البيانات والذكاء"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع المتقدم
# ---------------------------------------------------------
if page == "🔮 محرك التنبؤ الخارق":
    st.title("🚀 التوقع بناءً على الارتباط الشرطي")
    
    with st.container(border=True):
        st.subheader("🏁 معطيات السباق الحالي")
        c_v = st.columns(3)
        c1 = c_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = c_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = c_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        st.divider()
        c_t = st.columns(2)
        lp_type = c_t[0].selectbox("نوع الطريق الأطول", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp_pos = c_t[1].radio("موقع المسار الأطول", ["L", "C", "R"], horizontal=True)
        
        if st.button("🧠 استخراج النتيجة الذهبية", use_container_width=True):
            if not df.empty:
                pos_map = {"L": 3, "C": 4, "R": 5}
                match = df[(df.iloc[:, 6] == lp_pos) & (df.iloc[:, pos_map[lp_pos]] == lp_type)]
                match = match[match.iloc[:, 8].isin([c1, c2, c3])]
                
                if not match.empty:
                    stats = match.iloc[:, 8].value_counts()
                    st.success(f"🏆 الفائز المتوقع: **{stats.idxmax()}**")
                    st.write(f"📈 درجة الثقة: **{round((stats.max()/stats.sum())*100, 1)}%**")
                else:
                    gen_match = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                    if not gen_match.empty:
                        st.info(f"تاريخياً، الأفضل هو: **{gen_match.value_counts().idxmax()}**")
            else:
                st.error("القاعدة فارغة.")

    with st.expander("💾 تسجيل جولة جديدة"):
        c_r = st.columns(3)
        rl = c_r[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp_act = st.radio("الأطول فعلياً", ["L", "C", "R"], horizontal=True, key="lp_act")
        win_act = st.selectbox("الفائز الفعلي", [c1, c2, c3], key="win_act")

        if st.button("✅ تسجيل وتعلم"):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp_act, "entry.77901429": win_act
            }
            requests.post(FORM_URL, data=payload)
            st.success("تم التحديث!")

# ---------------------------------------------------------
# الصفحة الثانية: مصفوفة البيانات
# ---------------------------------------------------------
elif page == "📊 مصفوفة البيانات والذكاء":
    st.title("📊 مصفوفة تحليل الخوارزمية")
    if not df.empty:
        st.subheader("🔥 مصفوفة القوة: ملك الطريق")
        road_types = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]
        matrix_data = []
        for rt in road_types:
            wins = []
            for pos in ["L", "C", "R"]:
                p_idx = {"L": 3, "C": 4, "R": 5}[pos]
                m = df[(df.iloc[:, 6] == pos) & (df.iloc[:, p_idx] == rt)]
                wins.extend(m.iloc[:, 8].tolist())
            if wins:
                best = max(set(wins), key=wins.count)
                matrix_data.append({"نوع الطريق": rt, "السيارة المسيطرة": best, "الفوز": wins.count(best)})
            else:
                matrix_data.append({"نوع الطريق": rt, "السيارة المسيطرة": "نقص بيانات", "الفوز": 0})
        st.table(pd.DataFrame(matrix_data))
        st.bar_chart(df.iloc[:, 8].value_counts())
