import streamlit as st
import math

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·足球预测", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 足球预测引擎")
st.caption("输入Elo + 六爻参数，自动解卦融合二十八法")

# ============================================================
# 2. 知识库模块（卦象类象、六亲取象、二十八法断语）
# ============================================================
GUA_LEI_XIANG = {
    "乾": {"五行":"金","人物":"领导、父亲","场所":"京都","方位":"西北","数字":"1,6","动物":"马","静物":"金玉","人体":"头","颜色":"白","五味":"辛"},
    "坤": {"五行":"土","人物":"母亲、老妇","场所":"田野","方位":"西南","数字":"2,8","动物":"牛","静物":"五谷","人体":"腹","颜色":"黄","五味":"甘"},
    "震": {"五行":"木","人物":"长男、军人","场所":"森林","方位":"东","数字":"4,3","动物":"龙","静物":"竹","人体":"足","颜色":"绿","五味":"酸"},
    "巽": {"五行":"木","人物":"长女、教师","场所":"邮局","方位":"东南","数字":"5,4","动物":"鸡","静物":"绳","人体":"股","颜色":"蓝","五味":"酸"},
    "坎": {"五行":"水","人物":"中男、医生","场所":"江河","方位":"北","数字":"1,6","动物":"猪","静物":"油","人体":"耳","颜色":"黑","五味":"咸"},
    "离": {"五行":"火","人物":"中女、文人","场所":"影院","方位":"南","数字":"3,9","动物":"孔雀","静物":"书画","人体":"眼","颜色":"红","五味":"苦"},
    "艮": {"五行":"土","人物":"少男、警卫","场所":"山丘","方位":"东北","数字":"7,8","动物":"狗","静物":"石","人体":"鼻","颜色":"棕","五味":"甘"},
    "兑": {"五行":"金","人物":"少女、歌手","场所":"沼泽","方位":"西","数字":"2,7","动物":"羊","静物":"刀","人体":"口","颜色":"白","五味":"辛"}
}

LIU_QIN_QU_XIANG = {
    "父母": {"人物":"师长、长辈","事物":"文书、考试、护照","场所":"学校","性情":"大义","人体":"头","自然":"雨"},
    "兄弟": {"人物":"同学、竞争者","事物":"破财、阻隔","场所":"赌场","性情":"仗义","人体":"手足","自然":"风"},
    "子孙": {"人物":"晚辈、医生、警察","事物":"财源、游乐、解忧","场所":"医院","性情":"善良","人体":"眼耳","自然":"晴"},
    "官鬼": {"人物":"领导、官方、小人","事物":"工作、官职、疾病","场所":"法院","性情":"刚强","人体":"心脏","自然":"雷电"},
    "妻财": {"人物":"妻子、下属","事物":"钱财、利润、食物","场所":"银行","性情":"柔弱","人体":"血液","自然":"云"}
}

ER_SHI_BA_FA = {
    "六合卦": "平局优先（≥60%），总进球≤3",
    "归魂卦": "胶着反复，平局或小胜，双方有球",
    "游魂卦": "客队不败或意外赛果",
    "六冲卦": "优先分胜负，不轻易判平",
    "体克用": "主胜",
    "用克体": "客胜",
    "体用比和": "平局",
    "官鬼持世": "主队防守压力大，难零封",
    "子孙伏藏": "主队进攻乏力，最多1-2球",
    "妻财动化进": "70分钟后进球（补时绝杀）",
    "互卦归妹": "比赛有扳平、反超剧情",
    "变卦明夷": "主队有损失（丢球或被追平）",
    "六冲多动": "必分胜负，绝无闷平",
    "应爻暗动": "客队先进球或占先机",
    "世爻安静": "主队后程发力",
    "平局首选": "1-1 > 0-0 > 2-2",
    "分胜负区间": "胜方1-2球，负方0-1球",
    "卦气旺衰": "月建决定旺衰，日辰定根气",
    "过旺应凶": "能而不能，本该成却没成",
    "过衰应吉": "不能而能，绝境逢生"
}

def query_knowledge(keyword):
    if keyword in GUA_LEI_XIANG:
        info = GUA_LEI_XIANG[keyword]
        return f"【{keyword}卦】\n五行：{info['五行']}\n人物：{info['人物']}\n场所：{info['场所']}\n方位：{info['方位']}\n数字：{info['数字']}\n动物：{info['动物']}\n静物：{info['静物']}\n人体：{info['人体']}\n颜色：{info['颜色']}\n五味：{info['五味']}"
    if keyword in LIU_QIN_QU_XIANG:
        info = LIU_QIN_QU_XIANG[keyword]
        return f"【{keyword}爻】\n人物：{info['人物']}\n事物：{info['事物']}\n场所：{info['场所']}\n性情：{info['性情']}\n人体：{info['人体']}\n自然：{info['自然']}"
    if keyword in ER_SHI_BA_FA:
        return f"【{keyword}】\n{ER_SHI_BA_FA[keyword]}"
    return "未找到，试试输入卦名（乾/坤）、六亲（父母/官鬼）或断语（六合卦）"

# ============================================================
# 3. 卦象数据结构
# ============================================================
GUA_LIST = [
    "乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫",
    "随","蛊","临","观","噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离",
    "咸","恒","遁","大壮","晋","明夷","家人","睽","蹇","解","损","益","夬","姤",
    "萃","升","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑",
    "涣","节","中孚","小过","既济","未济"
]

GUA_STRUCT = {
    "乾":(1,1),"坤":(8,8),"屯":(6,4),"蒙":(7,6),"需":(6,1),"讼":(1,6),
    "师":(6,8),"比":(8,6),"小畜":(5,1),"履":(1,2),"泰":(8,1),"否":(1,8),
    "同人":(1,3),"大有":(3,1),"谦":(7,8),"豫":(4,8),"随":(2,4),"蛊":(7,5),
    "临":(8,2),"观":(5,8),"噬嗑":(3,4),"贲":(7,3),"剥":(7,8),"复":(4,8),
    "无妄":(1,4),"大畜":(7,1),"颐":(7,4),"大过":(2,5),"坎":(6,6),"离":(3,3),
    "咸":(2,7),"恒":(4,5),"遁":(1,7),"大壮":(4,1),"晋":(3,8),"明夷":(8,3),
    "家人":(5,3),"睽":(3,2),"蹇":(7,6),"解":(4,6),"损":(7,2),"益":(5,4),
    "夬":(2,1),"姤":(1,5),"萃":(2,8),"升":(5,8),"困":(2,6),"井":(5,6),
    "革":(2,3),"鼎":(3,5),"震":(4,4),"艮":(7,7),"渐":(5,7),"归妹":(4,2),
    "丰":(4,3),"旅":(3,7),"巽":(5,5),"兑":(2,2),"涣":(5,6),"节":(6,2),
    "中孚":(5,2),"小过":(4,7),"既济":(6,3),"未济":(3,6)
}
GUA_WUXING_MAP = {1:"金",2:"金",3:"火",4:"木",5:"木",6:"水",7:"土",8:"土"}

LIUHE_SET = {"泰","否","咸","恒","损","益","既济","未济","节","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣","中孚","小过"}
GUIHUN_SET = {"大有","需","大畜","随","蛊","同人","晋","归妹"}
YOUHUN_SET = {"需","讼","明夷","晋","中孚","大过","颐","大壮"}
LIUCHONG_SET = {"乾","坎","兑","离","震","巽","艮","坤"}

LEAGUE_AVG_TOTAL = {"英超":2.8,"西甲":2.6,"德甲":2.9,"意甲":2.5,"法甲":2.5,"日职":2.4,"K联赛":2.3,"世界杯":2.2}

# ============================================================
# 4. 五行生克函数
# ============================================================
def wuxing_sheng_ke(wo, ta):
    sheng = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
    ke = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
    if wo == ta: return 0
    elif sheng[wo] == ta: return 1
    elif ke[wo] == ta: return -1
    elif sheng[ta] == wo: return -2
    elif ke[ta] == wo: return 2
    else: return 0

# ============================================================
# 5. 自动解卦函数（融合二十八法）
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
        detail.append("归魂→双方有球")
    if zhu_gua in YOUHUN_SET:
        ke_adv *= 1.15
        detail.append("游魂→客不败")
    if zhu_gua in LIUCHONG_SET:
        fen_sheng_fu += 0.7
        detail.append("六冲→分胜负")

    if bian_gua in LIUHE_SET:
        ping_ju += 0.4
        detail.append("变卦六合→趋平")

    # 体用生克（梅花易数）
    if dong_yao == "无动爻":
        detail.append("无动爻→体用比和")
    else:
        dong_idx = {"初爻":0,"二爻":1,"三爻":2,"四爻":3,"五爻":4,"上爻":5}[dong_yao]
        shang, xia = GUA_STRUCT[zhu_gua]
        shang_wu = GUA_WUXING_MAP[shang]
        xia_wu = GUA_WUXING_MAP[xia]
        if dong_idx < 3:
            ti_wu, yong_wu = shang_wu, xia_wu
            detail.append(f"动{dong_yao}(下卦)→下卦为用(客)")
        else:
            ti_wu, yong_wu = xia_wu, shang_wu
            detail.append(f"动{dong_yao}(上卦)→上卦为用(客)")
        rel = wuxing_sheng_ke(ti_wu, yong_wu)
        if rel == -2:
            zhu_adv *= 1.12
            detail.append("用生体→主利")
        elif rel == 2:
            ke_adv *= 1.15
            detail.append("用克体→客利")
        elif rel == 1:
            ke_adv *= 1.10
            ping_ju += 0.15
            detail.append("体生用→主耗，客不败")
        elif rel == -1:
            zhu_adv *= 1.10
            detail.append("体克用→主胜机")
        else:
            ping_ju += 0.3
            detail.append("比和→平局")

    # 动爻位置
    dong_effect = {"无动爻":1.0,"初爻":0.85,"二爻":0.9,"三爻":1.0,"四爻":1.05,"五爻":1.1,"上爻":1.15}
    dong_factor = dong_effect[dong_yao]
    if dong_yao in ["四爻","五爻","上爻"]:
        zhu_adv *= 1.05
        detail.append("动在上卦→进攻端")
    else:
        ke_adv *= 1.05
        detail.append("动在下卦→防守端")

    # 综合系数
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
# 6. 核心预测函数（泊松分布 + 修正）
# ============================================================
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_score(elo_h, elo_a, league_avg, zhan_yi, liu_factors, bf_big, bf_small):
    total_goals = league_avg
    elo_sum = elo_h + elo_a
    lam_h = total_goals * (elo_h / elo_sum) * 2
    lam_a = total_goals * (elo_a / elo_sum) * 2

    # 必发修正
    if bf_big > 65 and bf_small < 35:
        lam_h *= 1.2; lam_a *= 1.2
    elif bf_big > 60:
        lam_h *= 1.08; lam_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        lam_h *= 0.9; lam_a *= 0.9

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

    if ping_ju > 0.3:
        avg = (lam_h + lam_a) / 2
        lam_h = lam_h * (1 - ping_ju*0.3) + avg * ping_ju*0.3
        lam_a = lam_a * (1 - ping_ju*0.3) + avg * ping_ju*0.3

    if jin_limit > 0:
        total = lam_h + lam_a
        if total > jin_limit:
            scale = jin_limit / total
            lam_h *= scale; lam_a *= scale

    if both_score:
        lam_h = max(lam_h, 1.0); lam_a = max(lam_a, 1.0)

    if fen_sheng > 0.5:
        diff = lam_h - lam_a
        lam_h += diff * 0.1; lam_a -= diff * 0.1

    lam_h = max(0.3, lam_h); lam_a = max(0.3, lam_a)

    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5], lam_h, lam_a

# ============================================================
# 7. 知识库查询UI函数
# ============================================================
def knowledge_query_ui():
    st.subheader("📚 六爻知识库")
    keyword = st.text_input("输入关键词查询", placeholder="如：乾 或 父母 或 六合卦")
    if st.button("查询", use_container_width=True):
        if keyword:
            st.info(query_knowledge(keyword.strip()))
        else:
            st.warning("请输入关键词")

# ============================================================
# 8. 界面布局与主程序
# ============================================================
# 初始化session_state
if 'liu_result' not in st.session_state:
    st.session_state.liu_result = auto_jie_gua("乾", "坤", "无动爻")

with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("🏠 主队", value="利物浦")
        league = st.selectbox("🏆 联赛", list(LEAGUE_AVG_TOTAL.keys()))
    with col2:
        away_team = st.text_input("✈️ 客队", value="曼城")

with st.expander("📊 核心数据", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        bf_big = st.number_input("📈 必发大球指数", 0, 100, 55)
        elo_home = st.number_input("📊 主队Elo", 1000, 2500, 1900, 10)
    with col2:
        bf_small = st.number_input("📉 必发小球指数", 0, 100, 45)
        elo_away = st.number_input("📊 客队Elo", 1000, 2500, 1850, 10)

with st.expander("🔮 六爻参数", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        zhu_gua = st.selectbox("主卦", GUA_LIST, index=0)
        dong_yao = st.selectbox("动爻位置", ["无动爻","初爻","二爻","三爻","四爻","五爻","上爻"], index=0)
    with col2:
        bian_gua = st.selectbox("变卦", GUA_LIST, index=1)
        zhan_yi_opt = st.selectbox("战意系数", [("保级/争冠",1.4),("淘汰赛",1.2),("普通联赛",1.0),("无欲无求",0.85),("友谊赛",0.7)],
                                   format_func=lambda x: x[0])
        zhan_yi = zhan_yi_opt[1]

    if st.button("🔄 解卦", use_container_width=True):
        st.session_state.liu_result = auto_jie_gua(zhu_gua, bian_gua, dong_yao)
        st.success("解卦完成")

    liu = st.session_state.liu_result
    st.write(f"**综合系数**: `{liu['zong_he']}`")
    st.write(f"**平局倾向**: {liu['ping_ju_tend']:.2f} | **主队优势**: {liu['zhu_advantage']:.2f} | **客队优势**: {liu['ke_advantage']:.2f}")
    st.caption(f"详情: {liu['detail']}")

with st.expander("📚 知识库查询", expanded=False):
    knowledge_query_ui()

# ============================================================
# 9. 预测按钮
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    liu_factors = st.session_state.liu_result
    league_avg = LEAGUE_AVG_TOTAL[league]

    top_scores, lam_h, lam_a = predict_score(
        elo_home, elo_away, league_avg, zhan_yi,
        liu_factors, bf_big, bf_small
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
            if i > j: win_sum += p
            elif i == j: draw_sum += p
            else: lose_sum += p
    st.write(f"**胜平负概率**: 主胜 {win_sum:.1f}% | 平局 {draw_sum:.1f}% | 客胜 {lose_sum:.1f}%")

    # 大小球概率（>2.5）
    over25 = sum(poisson_prob(lam_h,i) * poisson_prob(lam_a,j) * 100
                 for i in range(5) for j in range(5) if i+j > 2.5)
    under25 = 100 - over25
    st.write(f"**大小球概率**: 大球(>2.5) {over25:.1f}% | 小球(≤2.5) {under25:.1f}%")

    # 显示解卦详情
    with st.expander("🔮 解卦详情"):
        st.write(f"平局倾向: {liu_factors['ping_ju_tend']:.2f}")
        st.write(f"主队优势系数: {liu_factors['zhu_advantage']:.2f}")
        st.write(f"客队优势系数: {liu_factors['ke_advantage']:.2f}")
        st.write(f"综合系数: {liu_factors['zong_he']}")
        st.caption(liu_factors['detail'])

st.caption("💡 输入主卦、变卦、动爻后点击「解卦」，再点击「开始预测」")
