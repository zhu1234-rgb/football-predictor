import streamlit as st
import math

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ ELO·六爻预测", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ ELO + 六爻 · 足球预测")
st.caption("无 xG，完全基于 ELO 自动计算预期进球")

# ============================================================
# 2. 卦象属性库（与之前一致）
# ============================================================
GUA_STRUCT = {
    "乾": (1,1), "坤": (8,8), "屯": (6,4), "蒙": (7,6), "需": (6,1), "讼": (1,6),
    "师": (6,8), "比": (8,6), "小畜": (5,1), "履": (1,2), "泰": (8,1), "否": (1,8),
    "同人": (1,3), "大有": (3,1), "谦": (7,8), "豫": (4,8), "随": (2,4), "蛊": (7,5),
    "临": (8,2), "观": (5,8), "噬嗑": (3,4), "贲": (7,3), "剥": (7,8), "复": (4,8),
    "无妄": (1,4), "大畜": (7,1), "颐": (7,4), "大过": (2,5), "坎": (6,6), "离": (3,3),
    "咸": (2,7), "恒": (4,5), "遁": (1,7), "大壮": (4,1), "晋": (3,8), "明夷": (8,3),
    "家人": (5,3), "睽": (3,2), "蹇": (7,6), "解": (4,6), "损": (7,2), "益": (5,4),
    "夬": (2,1), "姤": (1,5), "萃": (2,8), "升": (5,8), "困": (2,6), "井": (5,6),
    "革": (2,3), "鼎": (3,5), "震": (4,4), "艮": (7,7), "渐": (5,7), "归妹": (4,2),
    "丰": (4,3), "旅": (3,7), "巽": (5,5), "兑": (2,2), "涣": (5,6), "节": (6,2),
    "中孚": (5,2), "小过": (4,7), "既济": (6,3), "未济": (3,6)
}
GUA_WUXING_MAP = {1:"金", 2:"金", 3:"火", 4:"木", 5:"木", 6:"水", 7:"土", 8:"土"}

# 六合、归魂、游魂、六冲集合（与之前一致）
LIUHE_SET = {"泰","否","咸","恒","损","益","既济","未济","节","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣","中孚","小过"}
GUIHUN_SET = {"大有","需","大畜","随","蛊","同人","晋","归妹"}
YOUHUN_SET = {"需","讼","明夷","晋","中孚","大过","颐","大壮"}
LIUCHONG_SET = {"乾","坎","兑","离","震","巽","艮","坤"}

# 联赛平均总进球（用于从 ELO 计算预期进球）
LEAGUE_AVG_TOTAL = {
    "英超": 2.8, "西甲": 2.6, "德甲": 2.9, "意甲": 2.5,
    "法甲": 2.5, "日职": 2.4, "K联赛": 2.3, "世界杯": 2.2
}

def wuxing_sheng_ke(wo, ta):
    sheng = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
    ke = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
    if wo == ta:
        return 0
    elif sheng[wo] == ta:
        return 1
    elif ke[wo] == ta:
        return -1
    elif sheng[ta] == wo:
        return -2
    elif ke[ta] == wo:
        return 2
    else:
        return 0

# ============================================================
# 3. 自动解卦函数（不变）
# ============================================================
def auto_jie_gua(zhu_gua, bian_gua, dong_yao):
    ping_ju = 0.0
    ke_adv = 1.0
    zhu_adv = 1.0
    jin_qiu_limit = 0
    both_score = False
    fen_sheng_fu = 0.0
    detail = []

    if zhu_gua in LIUHE_SET:
        ping_ju += 0.6
        jin_qiu_limit = 3
        detail.append("六合→平局优先，总进球≤3")
    if zhu_gua in GUIHUN_SET:
        ping_ju += 0.3
        both_score = True
        detail.append("归魂→胶着，双方有球")
    if zhu_gua in YOUHUN_SET:
        ke_adv *= 1.15
        detail.append("游魂→客队不败")
    if zhu_gua in LIUCHONG_SET:
        fen_sheng_fu += 0.7
        detail.append("六冲→分胜负")

    if bian_gua in LIUHE_SET:
        ping_ju += 0.4
        detail.append("变卦六合→趋向平")

    # 体用生克
    if dong_yao == "无动爻":
        ti_wuxing = "土"
        yong_wuxing = "土"
        rel = 0
        detail.append("无动爻，体用比和")
    else:
        dong_index = {"初爻":0,"二爻":1,"三爻":2,"四爻":3,"五爻":4,"上爻":5}[dong_yao]
        shang_gua, xia_gua = GUA_STRUCT[zhu_gua]
        shang_wu = GUA_WUXING_MAP[shang_gua]
        xia_wu = GUA_WUXING_MAP[xia_gua]
        if dong_index < 3:
            ti_wuxing = shang_wu
            yong_wuxing = xia_wu
            detail.append(f"动爻{dong_yao}（下卦）→ 下卦为用")
        else:
            ti_wuxing = xia_wu
            yong_wuxing = shang_wu
            detail.append(f"动爻{dong_yao}（上卦）→ 上卦为用")
        rel = wuxing_sheng_ke(ti_wuxing, yong_wuxing)
        if rel == -2:
            zhu_adv *= 1.12
            ping_ju -= 0.1
            detail.append("用生体→主利")
        elif rel == 2:
            ke_adv *= 1.15
            ping_ju -= 0.1
            detail.append("用克体→客利")
        elif rel == 1:
            ke_adv *= 1.10
            ping_ju += 0.15
            detail.append("体生用→主耗，客不败")
        elif rel == -1:
            zhu_adv *= 1.10
            ping_ju -= 0.05
            detail.append("体克用→主胜机")
        else:
            ping_ju += 0.3
            detail.append("比和→平局倾向")

    # 动爻位置
    dong_effect = {"无动爻":1.0,"初爻":0.85,"二爻":0.9,"三爻":1.0,"四爻":1.05,"五爻":1.1,"上爻":1.15}
    dong_factor = dong_effect[dong_yao]
    if dong_yao in ["四爻","五爻","上爻"]:
        zhu_adv *= 1.05
        detail.append("动在上卦→进攻")
    else:
        ke_adv *= 1.05
        detail.append("动在下卦→防守")

    zong_he = 1.0 + (zhu_adv-1.0) + (ke_adv-1.0) + (ping_ju*0.3) - (fen_sheng_fu*0.2)
    zong_he = max(0.5, min(1.5, zong_he))

    return {
        "ping_ju_tend": min(1.0, ping_ju),
        "ke_advantage": ke_adv,
        "zhu_advantage": zhu_adv,
        "jin_qiu_limit": jin_qiu_limit,
        "both_score": both_score,
        "fen_sheng_fu": fen_sheng_fu,
        "zong_he": round(zong_he, 3),
        "detail": "；".join(detail) if detail else "常规"
    }

# ============================================================
# 4. 核心预测函数（仅基于 ELO）
# ============================================================
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_score_with_elo(elo_h, elo_a, league_avg_total,
                           zhan_yi, liu_factors, bf_big, bf_small):
    # 从 ELO 计算预期进球
    total_goals = league_avg_total  # 联赛平均总进球
    # 按 ELO 比例分配
    elo_sum = elo_h + elo_a
    lam_h = total_goals * (elo_h / elo_sum) * 2  # 主队预期
    lam_a = total_goals * (elo_a / elo_sum) * 2  # 客队预期

    # 必发修正
    if bf_big > 65 and bf_small < 35:
        lam_h *= 1.2
        lam_a *= 1.2
    elif bf_big > 60:
        lam_h *= 1.08
        lam_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        lam_h *= 0.9
        lam_a *= 0.9

    # 六爻因子
    zhu_adv = liu_factors["zhu_advantage"]
    ke_adv = liu_factors["ke_advantage"]
    ping_ju = liu_factors["ping_ju_tend"]
    jin_limit = liu_factors["jin_qiu_limit"]
    both_score = liu_factors["both_score"]
    fen_sheng = liu_factors["fen_sheng_fu"]
    zong = liu_factors["zong_he"]

    lam_h *= zhu_adv * zhan_yi * zong
    lam_a *= ke_adv * zhan_yi * zong

    # 平局拉近
    if ping_ju > 0.3:
        avg = (lam_h + lam_a) / 2
        lam_h = lam_h * (1 - ping_ju*0.3) + avg * ping_ju*0.3
        lam_a = lam_a * (1 - ping_ju*0.3) + avg * ping_ju*0.3

    # 进球上限
    if jin_limit > 0:
        total = lam_h + lam_a
        if total > jin_limit:
            scale = jin_limit / total
            lam_h *= scale
            lam_a *= scale

    if both_score:
        lam_h = max(lam_h, 1.0)
        lam_a = max(lam_a, 1.0)

    if fen_sheng > 0.5:
        diff = lam_h - lam_a
        lam_h += diff * 0.1
        lam_a -= diff * 0.1

    lam_h = max(0.3, lam_h)
    lam_a = max(0.3, lam_a)

    # 比分概率
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
    labels = ["主胜","平局","客胜"]
    if initial and current:
        for i in range(3):
            drop = initial[i] - current[i]
            if drop > 0.2:
                alerts.append(f"⚠️ {labels[i]} 骤降 {drop:.2f}")
    return alerts

# ============================================================
# 5. UI 布局（无 xG 输入）
# ============================================================
with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("🏠 主队", value="利物浦")
        league = st.selectbox("🏆 联赛", list(LEAGUE_AVG_TOTAL.keys()))
    with col2:
        away_team = st.text_input("✈️ 客队", value="曼城")

with st.expander("📊 核心数据（手动输入）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        bf_big = st.number_input("📈 必发大球指数", 0, 100, 55)
        elo_home = st.number_input("📊 主队 ELO", 1000, 2500, 1900, 10)
    with col2:
        bf_small = st.number_input("📉 必发小球指数", 0, 100, 45)
        elo_away = st.number_input("📊 客队 ELO", 1000, 2500, 1850, 10)

with st.expander("🔮 六爻参数（输入主卦、变卦、动爻）", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        zhu_gua = st.selectbox("主卦", list(GUA_STRUCT.keys()), index=0)
        dong_yao = st.selectbox("动爻位置", ["无动爻","初爻","二爻","三爻","四爻","五爻","上爻"], index=0)
    with col2:
        bian_gua = st.selectbox("变卦", list(GUA_STRUCT.keys()), index=1)
        zhan_yi_opt = st.selectbox("战意系数", [("保级/争冠",1.4),("淘汰赛",1.2),("普通联赛",1.0),("无欲无求",0.85),("友谊赛",0.7)],
                                   format_func=lambda x: x[0])
        zhan_yi = zhan_yi_opt[1]

    if st.button("🔄 解卦", use_container_width=True):
        with st.spinner("解卦中..."):
            result = auto_jie_gua(zhu_gua, bian_gua, dong_yao)
            st.session_state['liu_result'] = result
            st.success("解卦完成")

    if 'liu_result' not in st.session_state:
        st.session_state['liu_result'] = auto_jie_gua(zhu_gua, bian_gua, dong_yao)

    liu = st.session_state['liu_result']
    st.write(f"**综合系数**: `{liu['zong_he']}`")
    st.write(f"**平局倾向**: {liu['ping_ju_tend']:.2f} | **主队优势**: {liu['zhu_advantage']:.2f} | **客队优势**: {liu['ke_advantage']:.2f}")
    st.caption(f"详情: {liu['detail']}")

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
# 6. 预测按钮
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    liu_factors = st.session_state['liu_result']
    avg_total = LEAGUE_AVG_TOTAL[league]  # 根据联赛获取平均总进球

    alerts = check_alert(initial_odds, current_odds)
    if alerts:
        st.error("🚨 变盘预警！")
        for a in alerts:
            st.warning(a)
    else:
        st.success("✅ 赔率稳定")

    top_scores, lam_h, lam_a = predict_score_with_elo(
        elo_home, elo_away, avg_total,
        zhan_yi, liu_factors, bf_big, bf_small
    )

    st.subheader(f"📊 {home_team} vs {away_team}")
    col1, col2 = st.columns(2)
    col1.metric(f"{home_team} 预期进球", f"{lam_h:.2f}")
    col2.metric(f"{away_team} 预期进球", f"{lam_a:.2f}")

    st.subheader("🏆 最可能比分")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  →  {prob:.2f}%")

    # 胜平负概率
    win_sum = draw_sum = lose_sum = 0
    for i in range(5):
        for j in range(5):
            p = poisson_prob(lam_h, i) * poisson_prob(lam_a, j) * 100
            if i > j:
                win_sum += p
            elif i == j:
                draw_sum += p
            else:
                lose_sum += p
    st.write(f"**胜平负概率**: 主胜 {win_sum:.1f}% | 平局 {draw_sum:.1f}% | 客胜 {lose_sum:.1f}%")

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

st.caption("💡 预期进球由 ELO 和联赛平均总进球自动计算，无需手动输入 xG")
