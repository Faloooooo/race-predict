import streamlit as st

# 1. قاعدة البيانات (السرعات)
data = {
    "Car":      {"desert": 132, "highway": 290.4, "bumpy": 98.4, "expressway": 264, "dirt": 153.6, "potholes": 67.2},
    "Sport":    {"desert": 96, "highway": 480, "bumpy": 168, "expressway": 432, "dirt": 360, "potholes": 57.6},
    "Super":    {"desert": 62.4, "highway": 528, "bumpy": 151.2, "expressway": 480, "dirt": 264, "potholes": 52.8},
    "Bigbike":  {"desert": 132, "highway": 230.4, "bumpy": 259.2, "expressway": 264, "dirt": 165.6, "potholes": 187.2},
    "Moto":     {"desert": 72, "highway": 225.6, "bumpy": 108, "expressway": 220.8, "dirt": 144, "potholes": 96},
    "Orv":      {"desert": 58.08, "highway": 240, "bumpy": 218.4, "expressway": 286, "dirt": 220.8, "potholes": 134.4},
    "Suv":      {"desert": 139.2, "highway": 360, "bumpy": 213.6, "expressway": 348, "dirt": 336, "potholes": 110.4},
    "Truck":    {"desert": 98.28, "highway": 276, "bumpy": 216, "expressway": 240, "dirt": 87.6, "potholes": 108},
    "Atv":      {"desert": 168, "highway": 115.2, "bumpy": 187.2, "expressway": 115.2, "dirt": 187.2, "potholes": 144}
}

# إعدادات الصفحة
st.set_page_config(page_title="توقع سباق السيارات", page_icon="🏎️")
st.title("🏎️ محلل السباقات الذكي")
st.markdown("---")

# 2. واجهة المستخدم - اختيار السيارات
st.subheader("🏁 اختر السيارات المشاركة")
col1, col2, col3 = st.columns(3)
with col1: v1 = st.selectbox("السيارة 1", list(data.keys()), index=0)
with col2: v2 = st.selectbox("السيارة 2", list(data.keys()), index=1)
with col3: v3 = st.selectbox("السيارة 3", list(data.keys()), index=2)

# 3. واجهة المستخدم - اختيار الطرق
st.subheader("🛣️ تفاصيل الطريق")
road_types = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]
r1 = st.selectbox("نوع الطريق الأول", road_types)
r2 = st.selectbox("نوع الطريق الثاني", road_types)
r3 = st.selectbox("نوع الطريق الثالث", road_types)

long_road = st.radio("أي طريق هو الأطول؟", ("الأول", "الثاني", "الثالث"), horizontal=True)
long_map = {"الأول": 0, "الثاني": 1, "الثالث": 2}

# 4. الحسابات والنتيجة
if st.button("🚀 توقع الفائز الآن"):
    participants = [v1, v2, v3]
    roads = [r1, r2, r3]
    long_idx = long_map[long_road]
    
    distances = [100, 100, 100]
    distances[long_idx] = 200 # الطريق الطويل ضعف العادي
    
    results = []
    for name in participants:
        total_time = sum(distances[i] / data[name][roads[i]] for i in range(3))
        results.append((name, total_time))
    
    results.sort(key=lambda x: x[1])
    
    st.success(f"🏆 الفائز المتوقع: **{results[0][0]}**")
    st.info(f"🥈 المركز الثاني: {results[1][0]}")
    st.warning(f"🥉 المركز الثالث: {results[2][0]}")
