import streamlit as st
import math

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 足球预测引擎", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 足球预测引擎 · 手动版")
st.caption("所有数据手动输入，六爻自动解卦")

# ============================================================
# 2. 六爻自动解卦模块
# ============================================================

# 64卦列表（按常见顺序）
GUA_LIST = [
    "乾", "坤", "屯", "蒙", "需", "讼", "师", "比", "小畜", "履",
    "泰", "否", "同人", "大有", "谦", "豫", "随", "蛊", "临", "观",
    "噬嗑", "贲", "剥", "复", "无妄", "大畜", "颐", "大过", "坎", "离",
    "咸", "恒", "遁", "大壮", "晋", "明夷", "家人", "睽", "蹇", "解",
    "损", "益", "夬", "姤", "萃", "升", "困", "井", "革", "鼎",
    "震", "艮", "渐", "归妹", "丰", "旅", "巽", "兑", "涣", "节",
    "中孚", "小过", "既济", "未济"
]

# 卦的五行属性（梅花易数体用分类）
GUA_WUXING = {
    "乾": "金", "兑": "金",
    "震": "木", "巽": "木",
    "坤": "土", "艮": "土",
    "坎": "水",
    "离": "火",
    # 其他卦根据上卦下卦组合，但我们按单卦五行处理（实际上每卦有上下卦，简化：用上卦五行代表）
    # 这里为了简化，我们只使用上卦五行，但用户选的是整卦名，我们需定义每个卦的五行。
    # 更准确的做法是按卦宫，但为了快速，我们简单归类：
    "屯": "水", "蒙": "水", "需": "水", "讼": "水", "师": "水", "比": "水",
    "小畜": "木", "履": "木", "泰": "土", "否": "土", "同人": "火", "大有": "火",
    "谦": "土", "豫": "土", "随": "木", "蛊": "木", "临": "土", "观": "土",
    "噬嗑": "木", "贲": "火", "剥": "土", "复": "土", "无妄": "木", "大畜": "土",
    "颐": "木", "大过": "木", "坎": "水", "离": "火",
    "咸": "金", "恒": "木", "遁": "金", "大壮": "木", "晋": "火", "明夷": "土",
    "家人": "木", "睽": "火", "蹇": "水", "解": "木", "损": "土", "益": "木",
    "夬": "金", "姤": "金", "萃": "金", "升": "木", "困": "水", "井": "水",
    "革": "火", "鼎": "火", "震": "木", "艮": "土", "渐": "木", "归妹": "木",
    "丰": "火", "旅": "火", "巽": "木", "兑": "金", "涣": "水", "节": "水",
    "中孚": "木", "小过": "木", "既济": "水", "未济": "火"
}

def get_wuxing(gua):
    """获取卦的五行"""
    return GUA_WUXING.get(gua, "土")  # 默认土

def wuxing_sheng_ke(wo, ta):
    """判断五行生克关系：返回 1 生, -1 克, 0 比和"""
    # 五行相生：金生水，水生木，木生火，火生土，土生金
    # 五行相克：金克木，木克土，土克水，水克火，火克金
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if wo == ta:
        return 0  # 比和
    elif sheng[wo] == ta:
        return 1  # 我生ta（泄气）
    elif ke[wo] == ta:
        return -1  # 我克ta（耗力）
    elif sheng[ta] == wo:
        return -2  # 生我（生气）
    elif ke[ta] == wo:
        return 2   # 克我（受制）
    else:
        return 0

def auto_jie_gua(zhu_gua, bian_gua, dong_yao):
    """
    自动解卦，返回六爻综合系数，以及各分项（用于显示）
    """
    # 1. 五行
    wu_zhu = get_wuxing(zhu_gua)
    wu_bian = get_wuxing(bian_gua)
    # 2. 生克关系（以主卦为体，变卦为用）
    rel = wuxing_sheng_ke(wu_zhu, wu_bian)
    # rel: 0比和, 1体生用(泄), -1体克用(耗), -2用生体(吉), 2用克体(凶)
    if rel == -2:   # 用生体，吉
        shengke_factor = 0.10
    elif rel == 2:  # 用克体，凶
        shengke_factor = -0.08
    elif rel == 1:  # 体生用，泄
        shengke_factor = -0.05
    elif rel == -1: # 体克用，耗
        shengke_factor = 0.03
    else:           # 比和
        shengke_factor = 0.0

    # 3. 动爻位置系数
    dong_map = {"无动爻": 0, "初爻": 0.8, "二爻": 0.9, "三爻": 1.0, "四爻": 1.1, "五爻": 1.15, "上爻": 1.2}
    dong_coef = dong_map.get(dong_yao, 1.0)

    # 4. 六冲六合（简化：主变卦是否相同，相同为伏吟，相反为反吟？不，我们只根据五行生克已包含）
    # 还可以判断主变卦是否为同一宫，但这里省略

    # 5. 综合系数 = 1 + 生克修正 + 动爻修正（动爻基础为1，乘以系数）
    # 动爻系数以1为基准，偏移为 (dong_coef-1)
    base_factor = 1.0 + shengke_factor + (dong_coef - 1) * 0.5  # 动爻影响折半

    # 额外：若为比和且动爻无，则稳定
    if rel == 0 and dong_yao == "无动爻":
        base_factor *= 0.95  # 略减活力度

    return {
        "综合系数": round(base_factor, 3),
        "主卦五行": wu_zhu,
        "变卦五行": wu_bian,
        "生克关系": rel,
        "生克因子": round(shengke_factor, 3),
        "动爻位置": dong_yao,
        "动爻系数": dong_coef
    }

# ============================================================
# 3. 核心算法函数
# ============================================================
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_scores(xg_h, xg_a, elo_h, elo_a, zhan_yi,
                   liu_yao_coef, bf_big, bf_small):
    # ELO修正
    elo_diff = elo_h - elo_a
    elo_factor_h = 1 + (elo_diff / 400) * 0.1
    elo_factor_a = 1 - (elo_diff / 400) * 0.1

    # 必发修正
    if bf_big > 65 and bf_small < 35:
        xg_h *= 1.2
        xg_a *= 1.2
    elif bf_big > 60:
        xg_h *= 1.08
        xg_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        xg_h *= 0.9
        xg_a *= 0.9

    # 六爻综合因子
    liu_factor = liu_yao_coef

    lam_h = xg_h * elo_factor_h * zhan_yi * liu_factor
    lam_a = xg_a * elo_factor_a * zhan_yi * (1 / max(liu_factor, 0.1))

    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_scores, lam_h, lam_a

def kelly_calc(odds, prob):
    if odds <= 1:
        return 0
    return (odds * prob - (1 - prob)) / odds

def check_alert(initial, current):
    alerts = []
    labels = ["主胜", "平局", "客胜"]
    if initial and current:
        for i in range(3):
            drop = initial[i] - current[i]
            if drop > 0.2:
                alerts.append(f"⚠️ {labels[i]} 赔率骤降 {drop:.2f} (初盘 {initial[i]:.2f} → 现盘 {current[i]:.2f})")
    return alerts

# ============================================================
# 4. 界面布局（所有输入都在主页面）
# ============================================================

# ---- 4.1 比赛基本信息 ----
with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("🏠 主队名称", value="利物浦")
        league = st.selectbox("🏆 联赛", ["英超", "西甲", "德甲", "意甲", "法甲", "日职", "K联赛", "世界杯"])
    with col2:
        away_team = st.text_input("✈️ 客队名称", value="曼城")

# ---- 4.2 核心数据（手动输入） ----
with st.expander("📊 核心数据（手动输入）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        bf_big = st.number_input("📈 必发大球指数", min_value=0, max_value=100, value=55, step=1)
        xg_home = st.number_input("⚽ 主队xG", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
        elo_home = st.number_input("📊 主队ELO", min_value=1000, max_value=2500, value=1900, step=10)
    with col2:
        bf_small = st.number_input("📉 必发小球指数", min_value=0, max_value=100, value=45, step=1)
        xg_away = st.number_input("⚽ 客队xG", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
        elo_away = st.number_input("📊 客队ELO", min_value=1000, max_value=2500, value=1850, step=10)

# ---- 4.3 六爻参数（自动解卦） ----
with st.expander("🔮 六爻参数（输入主卦、变卦、动爻，自动解卦）", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        zhu_gua = st.selectbox("主卦名称", GUA_LIST, index=0)
        dong_yao = st.selectbox("动爻位置", ["无动爻", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻"], index=0)
    with col2:
        bian_gua = st.selectbox("变卦名称", GUA_LIST, index=1)
        # 战意系数放在这里
        zhan_yi_option = st.selectbox("⚔️ 战意系数",
                                      options=[("保级/争冠关键战", 1.4), ("淘汰赛", 1.2), ("普通联赛", 1.0), ("无欲无求", 0.85), ("友谊赛", 0.7)],
                                      format_func=lambda x: x[0])
        zhan_yi = zhan_yi_option[1]

    # 自动解卦按钮
    if st.button("🔄 解卦计算系数", use_container_width=True):
        with st.spinner("正在解卦..."):
            result = auto_jie_gua(zhu_gua, bian_gua, dong_yao)
            st.session_state['liu_yao_result'] = result
            st.success("解卦完成！查看下方详情")
    else:
        if 'liu_yao_result' not in st.session_state:
            # 默认解一次
            st.session_state['liu_yao_result'] = auto_jie_gua(zhu_gua, bian_gua, dong_yao)

    # 显示解卦结果
    liu_info = st.session_state.get('liu_yao_result', {})
    if liu_info:
        st.write(f"**综合系数**: `{liu_info['综合系数']}`")
        st.write(f"主卦五行: {liu_info['主卦五行']} | 变卦五行: {liu_info['变卦五行']} | 生克因子: {liu_info['生克因子']} | 动爻: {liu_info['动爻位置']} (系数 {liu_info['动爻系数']})")

# ---- 4.4 赔率数据（手动输入） ----
with st.expander("📉 赔率数据（手动输入初盘/变盘）", expanded=False):
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

# ============================================================
# 5. 预测按钮与结果
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    # 获取六爻系数
    liu_coef = st.session_state.get('liu_yao_result', {}).get('综合系数', 1.0)

    # 变盘预警
    alerts = check_alert(initial_odds, current_odds)
    if alerts:
        st.error("🚨 变盘预警！")
        for a in alerts:
            st.warning(a)
    else:
        st.success("✅ 赔率稳定，无剧烈变盘")

    # 预测
    top_scores, lam_h, lam_a = predict_scores(
        xg_home, xg_away, elo_home, elo_away, zhan_yi,
        liu_coef, bf_big, bf_small
    )

    # 显示结果
    st.subheader(f"📊 {home_team} vs {away_team}")
    col1, col2 = st.columns(2)
    col1.metric(f"{home_team} λ", f"{lam_h:.2f}")
    col2.metric(f"{away_team} λ", f"{lam_a:.2f}")

    st.subheader("🏆 最可能比分")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  →  {prob:.2f}%")

    # 凯利
    if top_scores:
        max_prob = top_scores[0][1] / 100
        current_win_odds = current_odds[0] if current_odds else 1.80
        kelly_val = kelly_calc(current_win_odds, max_prob)
        st.subheader("💰 凯利风控")
        if kelly_val > 0.7:
            st.error(f"🚨 凯利值 {kelly_val:.2f}，风险高")
        elif kelly_val > 0.4:
            st.warning(f"⚠️ 凯利值 {kelly_val:.2f}")
        else:
            st.success(f"✅ 凯利值 {kelly_val:.2f}，稳定")

st.caption("💡 所有数据手动输入，六爻自动解卦。")
