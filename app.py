import streamlit as st
import requests
import math
import json
from datetime import datetime

# ============================================================
# 1. 页面配置（手机优先）
# ============================================================
st.set_page_config(page_title="⚽ 足球预测全能版", layout="centered", initial_sidebar_state="expanded")
st.title("⚽ 足球预测引擎 · 全能版")
st.caption("集成：必发指数 | 六爻纳甲 | 泊松分布 | ELO | xG | 凯利公式 | 变盘预警")

# ============================================================
# 2. 侧边栏：所有输入参数
# ============================================================
with st.sidebar:
    st.header("📌 比赛基本信息")
    home_team = st.text_input("🏠 主队名称", value="利物浦")
    away_team = st.text_input("✈️ 客队名称", value="曼城")
    
    st.divider()
    st.header("📊 核心数据（手动输入）")
    bf_big = st.number_input("📈 必发大球指数 (0-100)", min_value=0, max_value=100, value=55, step=1)
    bf_small = st.number_input("📉 必发小球指数 (0-100)", min_value=0, max_value=100, value=45, step=1)
    
    xg_home = st.number_input("⚽ 主队xG (预期进球)", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
    xg_away = st.number_input("⚽ 客队xG (预期进球)", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
    
    elo_home = st.number_input("📊 主队ELO评分", min_value=1000, max_value=2500, value=1900, step=10)
    elo_away = st.number_input("📊 客队ELO评分", min_value=1000, max_value=2500, value=1850, step=10)
    
    st.divider()
    st.header("🔮 玄学参数（六爻）")
    gua_name = st.selectbox("主卦名称", ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑", "其他"])
    moving_yao = st.selectbox("动爻位置 (初爻至上爻)", ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"], index=2)
    gua_score = st.slider("主卦对主队影响 (-5凶 ~ +5吉)", -5, 5, 0, step=1)
    
    st.divider()
    st.header("⚔️ 战意系数")
    zhan_yi = st.selectbox("比赛阶段战意", 
                           options=[("保级/争冠关键战", 1.4), ("淘汰赛", 1.2), ("普通联赛", 1.0), ("无欲无求", 0.85), ("友谊赛", 0.7)],
                           format_func=lambda x: x[0])
    zhan_yi_value = zhan_yi[1]
    
    st.divider()
    st.header("🌐 数据源（可选）")
    api_key = st.text_input("API-Football Key (免费)", type="password", help="不填则纯手动模式")
    fixture_id = st.number_input("比赛ID (用于自动抓取)", min_value=1, value=123456, step=1)
    
    st.divider()
    st.header("📉 手动初盘/变盘 (兜底)")
    use_manual_odds = st.checkbox("手动输入赔率 (否则尝试自动抓取)")
    if use_manual_odds:
        col1, col2, col3 = st.columns(3)
        with col1:
            init_h = st.number_input("初盘主胜", value=1.80, step=0.05)
            curr_h = st.number_input("变盘主胜", value=1.75, step=0.05)
        with col2:
            init_d = st.number_input("初盘平局", value=3.50, step=0.05)
            curr_d = st.number_input("变盘平局", value=3.60, step=0.05)
        with col3:
            init_a = st.number_input("初盘客胜", value=4.00, step=0.05)
            curr_a = st.number_input("变盘客胜", value=4.20, step=0.05)
        initial_odds = [init_h, init_d, init_a]
        current_odds = [curr_h, curr_d, curr_a]
    else:
        initial_odds = current_odds = None

# ============================================================
# 3. 核心算法函数
# ============================================================
def poisson_prob(lam, k):
    """泊松分布概率"""
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def fetch_odds_from_api(api_key, fixture_id):
    """尝试从API获取初盘与变盘"""
    if not api_key:
        return None, None
    headers = {"x-rapidapi-key": api_key}
    try:
        resp = requests.get(f"https://v3.football.api-sports.io/odds", 
                            headers=headers, 
                            params={"fixture": fixture_id}, timeout=8)
        data = resp.json()
        if data.get("response"):
            # 取第一家博彩公司的胜平负数据（简化处理）
            bookie = data["response"][0]["bookmakers"][0]
            bets = bookie["bets"][0]["values"]  # 通常第一个是"Match Winner"
            # 构建初盘和变盘列表（索引0主胜，1平局，2客胜）
            # 注意：实际API返回结构可能不同，这里做健壮处理
            initial = []
            current = []
            for item in bets:
                if "value" in item:
                    # 这里假设"value"为 "Home", "Draw", "Away"
                    if item["value"] == "Home":
                        initial.append(float(item.get("odd", 1.80)))
                    elif item["value"] == "Draw":
                        initial.append(float(item.get("odd", 3.50)))
                    elif item["value"] == "Away":
                        initial.append(float(item.get("odd", 4.00)))
            # 如果没有找到，用默认值
            if len(initial) != 3:
                return None, None
            # 变盘同样方式（实际上不同时间点，但免费版难获取历史，这里用当前赔率作为变盘）
            # 简单起见，将当前赔率作为变盘（实际中可用另一个接口）
            current = initial  # 演示，实际项目应获取即时赔率
            return initial, current
        else:
            return None, None
    except:
        return None, None

def check_alert(initial, current):
    """变盘预警：任一赔率降幅 > 0.2 触发报警"""
    alerts = []
    labels = ["主胜", "平局", "客胜"]
    if initial and current:
        for i in range(3):
            drop = initial[i] - current[i]
            if drop > 0.2:
                alerts.append(f"⚠️ {labels[i]} 赔率骤降 {drop:.2f} (初盘 {initial[i]:.2f} → 现盘 {current[i]:.2f})")
    return alerts

def predict_scores(xg_h, xg_a, elo_h, elo_a, zhan_yi, gua_score, moving_yao, bf_big, bf_small):
    """核心预测：返回前5比分及概率，以及λ值"""
    # 1. ELO修正：将ELO转换为进球因子（双方ELO差影响）
    elo_diff = elo_h - elo_a
    elo_factor_h = 1 + (elo_diff / 400) * 0.1   # 每差100分影响约2.5%
    elo_factor_a = 1 - (elo_diff / 400) * 0.1
    
    # 2. 必发大小球修正
    if bf_big > 65 and bf_small < 35:
        xg_h *= 1.2
        xg_a *= 1.2
    elif bf_big > 60:
        xg_h *= 1.08
        xg_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        xg_h *= 0.9
        xg_a *= 0.9
    
    # 3. 六爻量化（动爻位置影响波动性）
    # 将爻位转为系数（初爻~上爻 对应0.8~1.2）
    yao_map = {"初爻":0.8, "二爻":0.9, "三爻":1.0, "四爻":1.1, "五爻":1.15, "上爻":1.2}
    yao_effect = yao_map.get(moving_yao, 1.0)
    # 卦评分影响
    gua_effect = 1 + (gua_score / 50)  # -5 => 0.9, +5 => 1.1
    
    # 4. 计算预期进球λ
    lam_h = xg_h * elo_factor_h * zhan_yi * yao_effect * gua_effect
    lam_a = xg_a * elo_factor_a * zhan_yi * yao_effect * (1 / max(gua_effect, 0.1))
    
    # 5. 泊松分布计算0~4球的所有组合
    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_scores, lam_h, lam_a

def kelly_calc(odds, prob):
    """凯利值计算 (odds为当前赔率, prob为预测概率0-1)"""
    if odds <= 1:
        return 0
    return (odds * prob - (1 - prob)) / odds

# ============================================================
# 4. 主界面：预测按钮及结果显示
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    # ---- 4.1 获取赔率数据（自动或手动） ----
    initial, current = None, None
    if api_key and not use_manual_odds:
        with st.spinner("正在拉取实时赔率数据..."):
            initial, current = fetch_odds_from_api(api_key, fixture_id)
            if initial:
                st.success("✅ 自动获取赔率成功")
            else:
                st.warning("⚠️ 自动获取失败，请检查API Key或比赛ID，或启用'手动输入赔率'")
                # 使用默认值继续
                initial = [1.80, 3.50, 4.00]
                current = [1.75, 3.60, 4.20]
    elif use_manual_odds and initial_odds:
        initial = initial_odds
        current = current_odds
        st.info("📝 使用手动输入的赔率")
    else:
        # 默认赔率（无数据）
        initial = [1.80, 3.50, 4.00]
        current = [1.80, 3.50, 4.00]
        st.info("📝 使用默认赔率（无变盘预警）")
    
    # ---- 4.2 变盘预警 ----
    if initial and current:
        alerts = check_alert(initial, current)
        if alerts:
            st.error("🚨 变盘预警触发！")
            for a in alerts:
                st.warning(a)
        else:
            st.success("✅ 无剧烈变盘，数据平稳")
    
    # ---- 4.3 执行比分预测 ----
    top_scores, lam_h, lam_a = predict_scores(
        xg_home, xg_away, elo_home, elo_away, zhan_yi_value, 
        gua_score, moving_yao, bf_big, bf_small
    )
    
    # ---- 4.4 显示预测结果 ----
    st.subheader(f"📊 {home_team} vs {away_team} 预测详情")
    col1, col2 = st.columns(2)
    col1.metric(f"{home_team} 预期进球 λ", f"{lam_h:.2f}")
    col2.metric(f"{away_team} 预期进球 λ", f"{lam_a:.2f}")
    
    st.subheader("🏆 最可能比分 (概率%)")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  →  {prob:.2f}%")
    
    # ---- 4.5 凯利公式计算（基于最高概率比分） ----
    if top_scores:
        max_prob = top_scores[0][1] / 100
        # 选取当前主胜赔率（假设为current[0]）
        current_win_odds = current[0] if current and len(current)>0 else 1.80
        kelly_val = kelly_calc(current_win_odds, max_prob)
        st.subheader("💰 凯利风控指标")
        if kelly_val > 0.7:
            st.error(f"🚨 凯利值 {kelly_val:.2f}，庄家赔付风险高，建议谨慎！")
        elif kelly_val > 0.4:
            st.warning(f"⚠️ 凯利值 {kelly_val:.2f}，存在一定风险")
        else:
            st.success(f"✅ 凯利值 {kelly_val:.2f}，模型信心稳定")
        
        # 显示当前的赔率信息
        st.caption(f"当前主胜赔率: {current_win_odds:.2f} | 预测主胜概率: {max_prob*100:.1f}%")
    
    # ---- 4.6 额外信息：ELO和战意 ----
    with st.expander("📌 参数详情"):
        st.write(f"**ELO差**: {elo_home - elo_away} 分")
        st.write(f"**战意系数**: {zhan_yi_value}")
        st.write(f"**六爻**: {gua_name} / {moving_yao} / 卦评分 {gua_score}")
        st.write(f"**必发指数**: 大球 {bf_big} / 小球 {bf_small}")

st.divider()
st.caption("💡 提示：所有参数均在左侧边栏调整，点击预测即可刷新结果。")
