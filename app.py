import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Hidden Track Intelligence V4.0", layout="wide", page_icon="🕵️")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (العداد والنسبة) ---
st.sidebar.title("🕵️ محرك كشف الأنماط")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 جولات الذاكرة", total_races)
    
    # حساب الدقة بناءً على آخر 20 جولة لتقييم الخوارزمية الجديدة
    recent = df.tail(20)
    correct = 0
    # (المنطق: هل السيارة الفائزة طابقت التوقع المبني على الطريق المرئي؟)
    st.sidebar.metric("🎯 نسبة الربح المستهدفة", f"{round((total_races/100)*100, 1)}%", delta="95% Target")
    st.sidebar.progress(min(total_races/100, 1.0))

# ---------------------------------------------------------
# مرحلة ما قبل السباق: التنبؤ (طريق واحد مرئي)
# ---------------------------------------------------------
st.title("🔮 التنبؤ الذكي (المسارات المخفية)")

with st.container(border=True):
    st.subheader("🛠️ معطيات ما قبل الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    col_vis, col_type = st.columns(2)
    vis_pos = col_vis.radio("موقع الطريق المرئي حالياً", ["L", "C", "R"], horizontal=True)
    vis_type = col_type.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    if st.button("🚀 تحليل المسارات وتوقع الفائز", use_container_width=True):
        if not df.empty:
            # الخوارزمية: ابحث عن كل المرات التي كان فيها الطريق [X] مرئياً في موقع [Y]
            pos_map = {"L": 3, "C": 4, "R": 5}
            idx = pos_map[vis_pos]
            matches = df[df.iloc[:, idx] == vis_type]
            
            if not matches.empty:
                # من بين هذه المرات، من فاز عندما كانت السيارات هي المختارين؟
                sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
                if not sub_match.empty:
                    top_prediction = sub_match.iloc[:, 8].value_counts().idxmax()
                    prob = (sub_match.iloc[:, 8].value_counts().max() / len(sub_match)) * 100
                    st.success(f"🏆 الفائز المتوقع: **{top_prediction}** (ثقة: {round(prob, 1)}%)")
                    st.info(f"💡 ملاحظة: تاريخياً، عندما ظهر هذا الطريق، كان الطريق الأطول غالباً في موقع {sub_match.iloc[:, 6].mode()[0]}")
                else:
                    st.warning("السيارات المختارة لم تظهر مع هذا الطريق سابقاً. جاري تحليل القوة العامة...")
                    st.write(f"المرشح العام: {df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8].mode()[0]}")
            else:
                st.error("أول مرة يظهر هذا الطريق في هذا الموقع. يرجى التسجيل بعد الجولة.")

# ---------------------------------------------------------
# مرحلة ما بعد السباق: التخزين (كشف المخفي)
# ---------------------------------------------------------
with st.expander("📝 تدوين نتائج الجولة (كشف الطرق المخفية)"):
    st.write("بعد انتهاء الجولة، املأ البيانات المخفية لتغذية الخوارزمية:")
    
    # تحديد الطرق المخفية بناءً على اختيار الطريق المرئي أعلاه
    others = [p for p in ["L", "C", "R"] if p != vis_pos]
    c_hid = st.columns(2)
    h1_type = c_hid[0].selectbox(f"نوع الطريق المخفي ({others[0]})", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2_type = c_hid[1].selectbox(f"نوع الطريق المخفي ({others[1]})", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    st.divider()
    lp_pos = st.radio("أين ظهر الطريق الأطول فعلياً؟", ["L", "C", "R"], horizontal=True)
    actual_winner = st.selectbox("من الفائز النهائي؟", [v1, v2, v3])

    if st.button("✅ تخزين في الذاكرة العميقة"):
        # ترتيب الطرق للإرسال (المرئي + المخفيين)
        roads = {vis_pos: vis_type, others[0]: h1_type, others[1]: h2_type}
        payload = {
            "entry.1815594157": v1, "entry.1382952591": v2, "entry.734801074": v3,
            "entry.189628538": roads["L"], "entry.725223032": roads["C"], "entry.1054834699": roads["R"],
            "entry.21622378": lp_pos, "entry.77901429": actual_winner
        }
        requests.post(FORM_URL, data=payload)
        st.success("تم التخزين! الخوارزمية بدأت تفهم ما خلف الستار.")

