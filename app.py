# app.py
import streamlit as st
import requests
import random
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="AI 습관 트래커 (포켓몬)",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 AI 습관 트래커 (포켓몬 에디션)")

# =========================
# 사이드바 (API 키는 선택)
# =========================
with st.sidebar:
    st.header("🔑 API 설정 (선택)")
    openai_api_key = st.text_input("OpenAI API Key (없어도 실행됨)", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key (없어도 실행됨)", type="password")

# =========================
# 습관 체크인 UI
# =========================
st.subheader("✅ 오늘의 습관 체크인")

c1, c2 = st.columns(2)
with c1:
    wake = st.checkbox("🌅 기상 미션")
    water = st.checkbox("💧 물 마시기")
    study = st.checkbox("📚 공부/독서")
with c2:
    exercise = st.checkbox("🏃 운동하기")
    sleep = st.checkbox("😴 수면")

habits = {
    "기상 미션": wake,
    "물 마시기": water,
    "공부/독서": study,
    "운동하기": exercise,
    "수면": sleep,
}

mood = st.slider("😊 오늘의 기분", 1, 10, 5)

cities = [
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
    "Gwangju", "Suwon", "Ulsan", "Jeju", "Sejong"
]
city = st.selectbox("🌍 도시 선택", cities)

coach_style = st.radio(
    "🎭 코치 스타일",
    ["스파르타 코치", "따뜻한 멘토", "게임 마스터"],
    horizontal=True
)

# =========================
# 달성률
# =========================
checked = sum(habits.values())
achievement = int((checked / 5) * 100)

m1, m2, m3 = st.columns(3)
m1.metric("📈 달성률", f"{achievement}%")
m2.metric("✅ 달성 습관", f"{checked}/5")
m3.metric("😊 기분", mood)

# =========================
# 7일 데모 차트
# =========================
st.subheader("📊 최근 7일 기록")

demo = [
    {"day": "D-6", "count": 3},
    {"day": "D-5", "count": 4},
    {"day": "D-4", "count": 2},
    {"day": "D-3", "count": 5},
    {"day": "D-2", "count": 4},
    {"day": "D-1", "count": 3},
    {"day": datetime.now().strftime("%m/%d"), "count": checked},
]

df = pd.DataFrame(demo)
fig, ax = plt.subplots()
ax.bar(df["day"], df["count"])
ax.set_ylim(0, 5)
ax.set_ylabel("습관 수")
st.pyplot(fig)

# =========================
# API FUNCTIONS
# =========================
def get_weather(city, api_key):
    if not api_key:
        return None
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric&lang=kr"
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        return {
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"]
        }
    except:
        return None

# ✅ API 키 필요 없는 포켓몬 API
def get_pokemon():
    try:
        number = random.randint(1, 151)
        url = f"https://pokeapi.co/api/v2/pokemon/{number}"
        r = requests.get(url, timeout=10)
        data = r.json()

        stats_raw = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

        return {
            "id": data["id"],
            "name": data["name"].capitalize(),
            "types": [t["type"]["name"] for t in data["types"]],
            "image": data["sprites"]["other"]["official-artwork"]["front_default"],
            "stats": {
                "HP": stats_raw["hp"],
                "공격": stats_raw["attack"],
                "방어": stats_raw["defense"],
                "특수공격": stats_raw["special-attack"],
                "특수방어": stats_raw["special-defense"],
                "스피드": stats_raw["speed"],
            }
        }
    except:
        return None

def generate_fallback_report(pokemon, style):
    tone = {
        "스파르타 코치": "핑계는 없다. 오늘도 전진이다.",
        "따뜻한 멘토": "괜찮아, 한 걸음씩 가면 돼.",
        "게임 마스터": "퀘스트는 이미 시작되었다!"
    }[style]

    return f"""
컨디션 등급: B

습관 분석:
오늘은 완벽하진 않지만 충분히 의미 있는 하루였어.

내일 미션:
✔️ 체크한 습관 하나를 반드시 반복하기

오늘의 파트너 포켓몬:
{pokemon['name']} ({', '.join(pokemon['types'])})
→ {tone}
"""

# =========================
# 결과
# =========================
st.divider()
st.subheader("🤖 컨디션 리포트")

if st.button("컨디션 리포트 생성"):
    pokemon = get_pokemon()
    weather = get_weather(city, weather_api_key)

    c1, c2 = st.columns(2)

    with c1:
        if weather:
            st.info(f"🌤 {city}\n{weather['desc']} / {weather['temp']}℃")
        else:
            st.info("🌤 날씨 정보 없음 (API 키 미사용)")

    with c2:
        if pokemon:
            st.image(pokemon["image"], caption=f"#{pokemon['id']} {pokemon['name']}")
            stat_df = pd.DataFrame(
                pokemon["stats"].values(),
                index=pokemon["stats"].keys(),
                columns=["스탯"]
            )
            st.bar_chart(stat_df, color="#ff0000")

    if openai_api_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        report = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "너는 게임 코치다."},
                {"role": "user", "content": str(habits)}
            ]
        ).choices[0].message.content
    else:
        report = generate_fallback_report(pokemon, coach_style)

    st.markdown("### 📋 리포트")
    st.write(report)
    st.code(report)

# =========================
# API 안내
# =========================
with st.expander("ℹ️ 사용 API"):
    st.markdown("""
- **PokeAPI (API 키 불필요)**  
  https://pokeapi.co/api/v2/pokemon/{id}

- **OpenWeatherMap (선택)**  
- **OpenAI (선택)**
""")
