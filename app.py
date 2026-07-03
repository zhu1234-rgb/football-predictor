import streamlit as st
import requests
import math
import json

# ============ 页面配置 ============
st.set_page_config(page_title="足球预测神器", layout="centered")
st.title("⚽ 足球预测引擎 (网页输入版)")
st.caption("专为 Streamlit 优化，解决空白页问题 | 数据源：API-Football")

# ============ 侧边栏：免费API配置 ============
with st.sidebar:
    st.header("🔑 数据源配置")
    api_key = st.text_input("输入你的 API-Football Key", type="password", help="免费版每天100次请求")
    fixture_id = st.number_input("比赛ID (Fixture ID)", min_value=1, value=123456, step=1)
    
    st.divider()
    st.header("📊 手动输入核心数据")
    # 必发指数（替代input()）
    bf_big = st.slider("必发大球指数", 0, 100, 55)
    bf_small = st.slider("必发小球指数", 0, 100, 45)
    
    # 六爻量化
    moving_yao = st.selectbox("动爻力量 (1-9)", [1,2,3,4,5,6,7,8,9], index=4)
    gua_score = st.slider("主卦对主队评分 (-5凶 到 +5吉)", -5, 5, 0)
    
    # xG 预期进球
    xg_home = st.number_input("主队xG", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
    xg_away = st.number_input("客队xG", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
    
    # 战意系数
    zhan_yi = st.selectbox("战意系数", [0.8, 0.9, 1.0, 1.2, 1.4], index=2, help="保级/争冠选1.4，无欲无求选0.8")

# ============ 核心函数 ============
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def fetch_odds(api_key, fid):
    if not api_key:
        return None
    headers = {"x-rapidapi-key": api_key}
    try:
        resp = requests.get(f"https://v3.football.api-sports.io/odds", 
                            headers=headers, 
                            params={"fixture": fid},
                            timeout=10)
        data = resp.json()
        if data.get("response"):
            # 简易解析，取第一个盘口
            return {"status": "ok", "data": data["response"][0]}
        else:
            return {"status": "error", "msg": "无数据或ID错误"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def predict_score(xg_h, xg_a, zhan_yi, gua_score, moving_yao, bf_big):
    # 必发修正
    if bf_big > 65:
        xg_h *= 1.15
        xg_a *= 1.15
    # 六爻修正
    yao_effect = 1 + (int(moving_yao) / 10) * 0.05
    gua_effect = 1 + (gua_score / 50)
    
    lam_h = xg_h * zhan_yi * yao_effect * gua_effect
    lam_a = xg_a * zhan_yi * yao_effect * (1 / max(gua_effect, 0.1))
    
    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_scores, lam_h, lam_a

# ============ 主按钮与结果展示 ============
if st.button("🚀 开始预测", type="primary"):
    # 1. 拉取数据
    if api_key:
        with st.spinner("正在拉取初盘/变盘数据..."):
            result = fetch_odds(api_key, fixture_id)
            if result and result.get("status") == "ok":
                st.success("✅ API数据拉取成功")
                st.json(result["data"])  # 展示原始数据供参考
            else:
                st.warning(f"⚠️ API错误：{result.get('msg', '未知错误')}，将跳过自动预警")
    else:
        st.info("未输入API Key，跳过自动抓取，仅使用手动数据计算")
    
    # 2. 执行预测
    top_scores, lam_h, lam_a = predict_score(xg_home, xg_away, zhan_yi, gua_score, moving_yao, bf_big)
    
    # 3. 显示结果
    st.subheader("📈 预测结果")
    col1, col2 = st.columns(2)
    col1.metric("主队预期进球 λ", f"{lam_h:.2f}")
    col2.metric("客队预期进球 λ", f"{lam_a:.2f}")
    
    st.subheader("🏆 最可能比分 (概率%)")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  ->  {prob:.2f}%")
    
    # 4. 凯利简易计算
    if top_scores:
        kelly_val = (1.8 * (top_scores[0][1]/100) - (1 - top_scores[0][1]/100)) / 1.8
        if kelly_val > 0.8:
            st.error(f"🚨 凯利值 {kelly_val:.2f}，风险极高！")
        else:
            st.success(f"✅ 凯利值 {kelly_val:.2f}，状态平稳。")

st.divider()
st.caption("💡 提示：免费API每天限100次，若空白请检查Key或改用纯手动模式（不填Key即可）")
