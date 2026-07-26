import streamlit as st

# ===================== 全局体系说明【古法纳甲｜野鹤实战派｜赛事量化模型V2.0】 =====================
"""
更新规则清单（按本次修正方案落地）
1. 三合局优先级：生源泄气优先，不叠加生扶；局生爻正常叠加
2. 世爻兄弟爻：总分硬性扣除 -1.5（纳入数值运算，不只文字提示）
3. 扩充动变选项：化进、化退、化空、回头克，互斥不可叠加
4. 六神量化增加前置条件：旺相生效，休囚归零；仅青龙(世)、朱雀(应)参与计分
5. 分差四档概率区间划分，适配足球赛事判断
6. 增加单爻得分上下限约束：[-5, +6]
"""

# ===================== 基础卦库 =====================
GUA_DB = {
    "乾为天": {"gong": "乾宫"}, "天风姤": {"gong": "乾宫"}, "天山遁": {"gong": "乾宫"}, "天地否": {"gong": "乾宫"},
    "风地观": {"gong": "乾宫"}, "山地剥": {"gong": "乾宫"}, "火地晋": {"gong": "乾宫"}, "火天大有": {"gong": "乾宫"},
    "兑为泽": {"gong": "兑宫"}, "泽水困": {"gong": "兑宫"}, "泽地萃": {"gong": "兑宫"}, "泽山咸": {"gong": "兑宫"},
    "水山蹇": {"gong": "兑宫"}, "地山谦": {"gong": "兑宫"}, "雷山小过": {"gong": "兑宫"}, "雷泽归妹": {"gong": "兑宫"},
    "离为火": {"gong": "离宫"}, "火山旅": {"gong": "离宫"}, "火风鼎": {"gong": "离宫"}, "火水未济": {"gong": "离宫"},
    "山水蒙": {"gong": "离宫"}, "风水涣": {"gong": "离宫"}, "天水讼": {"gong": "离宫"}, "天火同人": {"gong": "离宫"},
    "震为雷": {"gong": "震宫"}, "雷地豫": {"gong": "震宫"}, "雷水解": {"gong": "震宫"}, "雷风恒": {"gong": "震宫"},
    "地风升": {"gong": "震宫"}, "水风井": {"gong": "震宫"}, "泽风大过": {"gong": "震宫"}, "泽雷随": {"gong": "震宫"},
    "巽为风": {"gong": "巽宫"}, "风天小畜": {"gong": "巽宫"}, "风火家人": {"gong": "巽宫"}, "风雷益": {"gong": "巽宫"},
    "天雷无妄": {"gong": "巽宫"}, "火雷噬嗑": {"gong": "巽宫"}, "山雷颐": {"gong": "巽宫"}, "山风蛊": {"gong": "巽宫"},
    "坎为水": {"gong": "坎宫"}, "水泽节": {"gong": "坎宫"}, "水雷屯": {"gong": "坎宫"}, "水火既济": {"gong": "坎宫"},
    "泽火革": {"gong": "坎宫"}, "雷火丰": {"gong": "坎宫"}, "地火明夷": {"gong": "坎宫"}, "地水师": {"gong": "坎宫"},
    "艮为山": {"gong": "艮宫"}, "山火贲": {"gong": "艮宫"}, "山天大畜": {"gong": "艮宫"}, "山泽损": {"gong": "艮宫"},
    "火泽睽": {"gong": "艮宫"}, "天泽履": {"gong": "艮宫"}, "风泽中孚": {"gong": "艮宫"}, "风山渐": {"gong": "艮宫"},
    "坤为地": {"gong": "坤宫"}, "地雷复": {"gong": "坤宫"}, "地泽临": {"gong": "坤宫"}, "地天泰": {"gong": "坤宫"},
    "雷天大壮": {"gong": "坤宫"}, "泽天夬": {"gong": "坤宫"}, "水天需": {"gong": "坤宫"}, "水地比": {"gong": "坤宫"},
}
GUA_NAME_LIST = list(GUA_DB.keys())
LIUCHONG_GUA = ["乾为天", "兑为泽", "离为火", "震为雷", "巽为风", "坎为水", "艮为山", "坤为地", "天雷无妄"]
LIUHE_GUA = ["天地否", "地天泰", "雷风恒", "风泽中孚", "山泽损", "泽山咸", "风火家人", "水泽节"]

# ===================== 计分选项定义 =====================
MONTH_STATE = [
    "临月建(+2)",
    "得月生扶(+1)",
    "余气有根(+0.5)",
    "平相无生克(0)",
    "休囚无力(-1)",
    "月破(-2)"
]
DAY_STATE = [
    "临日/日合起旺(+2)",
    "得日生扶(+1)",
    "平相无生克(0)",
    "入墓/受日克(-1)",
    "日破/真空(-2)"
]
SANHE_STATE = [
    "三合局中神(+3)",
    "辅神｜局生爻(+1.5)",
    "辅神｜爻生局【泄气】(-0.5)",
    "静爻参与三合无得失(0)",
    "被三合局克制(-1.5)"
]
DONG_BIAN_STATE = [
    "动而化进神(+1.0)",
    "动而回头生(+0.5)",
    "静爻无动变(0)",
    "动而化泄(-0.5)",
    "动而化空(-0.5)",
    "动而化退神(-1.0)",
    "动而回头克(-1.0)"
]
SHI_YING_RELATION = [
    "应生世｜世+0.5 应-0.5",
    "世生应｜世-0.5 应+0.5",
    "世克应｜世+0.5 应-0.5",
    "应克世｜世-0.5 应+0.5",
    "世应比和｜双方0"
]
SHEN_LIST = ["青龙", "朱雀", "勾陈", "玄武"]
LIUQIN_LIST = ["父母", "子孙", "妻财", "官鬼", "兄弟"]
WANGSHUAI_FLAG = ["爻旺相", "爻休囚"]

# ===================== 数值映射函数 =====================
def parse_val(text: str):
    num_str = text.split("(")[-1].replace(")", "")
    return float(num_str)

def calc_shiying_bonus(rel_text):
    shi_add, ying_add = 0.0, 0.0
    if rel_text == "应生世｜世+0.5 应-0.5":
        shi_add, ying_add = 0.5, -0.5
    elif rel_text == "世生应｜世-0.5 应+0.5":
        shi_add, ying_add = -0.5, 0.5
    elif rel_text == "世克应｜世+0.5 应-0.5":
        shi_add, ying_add = 0.5, -0.5
    elif rel_text == "应克世｜世-0.5 应+0.5":
        shi_add, ying_add = -0.5, 0.5
    return shi_add, ying_add

def clamp_score(x: float):
    # 单爻分值上下限 [-5, 6]
    return max(-5.0, min(6.0, x))

# ===================== 核心计算函数 =====================
def calculate_model(
    # 世爻参数
    shi_month, shi_day, shi_sanhe, shi_dongbian, shi_shen, shi_wangshuai, shi_liuqin,
    # 应爻参数
    ying_month, ying_day, ying_sanhe, ying_dongbian, ying_shen, ying_wangshuai,
    shiying_relation
):
    # 基础分累加
    shi = parse_val(shi_month) + parse_val(shi_day) + parse_val(shi_sanhe) + parse_val(shi_dongbian)
    ying = parse_val(ying_month) + parse_val(ying_day) + parse_val(ying_sanhe) + parse_val(ying_dongbian)

    # 世应生克加成
    shi_plus, ying_plus = calc_shiying_bonus(shiying_relation)
    shi += shi_plus
    ying += ying_plus

    # 六神量化规则
    if shi_wangshuai == "爻旺相" and shi_shen == "青龙":
        shi += 0.3
    if ying_wangshuai == "爻旺相" and ying_shen == "朱雀":
        ying -= 0.3

    # 核心修正：世爻兄弟持世 -1.5
    xiong_mod = 0.0
    if shi_liuqin == "兄弟":
        xiong_mod = -1.5
        shi += xiong_mod

    # 上下限约束
    shi = clamp_score(shi)
    ying = clamp_score(ying)
    delta = round(shi - ying, 2)

    # 四档判词
    if delta >= 4.0:
        res_text = "强弱悬殊，高分方胜率＞75%，平局概率极低"
    elif 2.0 <= delta <= 3.9:
        res_text = "优势方不败（胜率≈60%，平局≈30%），优先小胜，防范平局"
    elif 0.5 <= delta <= 1.9:
        res_text = "双方势均力敌，平局概率最高（≈45%）"
    else:  # <0.5
        res_text = "双方力量接近，难以出现大比分，首选平局/让平"

    extra_tips = []
    if xiong_mod == -1.5:
        extra_tips.append("【28法提示】世爻兄弟持世，力量存在持续消耗，易出现得势不得分。")
    if shi_sanhe.startswith("辅神｜爻生局"):
        extra_tips.append("【三合规则】辅神为生源，优先计泄气损耗，不叠加局生扶增益。")
    return shi, ying, delta, res_text, extra_tips

# ===================== UI界面 =====================
st.set_page_config(page_title="六爻足球｜古法量化模型V2.0", layout="wide")
st.title("⚽ 足球赛事六爻推演｜古法纳甲量化模型 V2.0")
st.caption("体系：野鹤实战派+黄金策28法｜量化权重严格遵循修正方案")

tab1, tab2 = st.tabs(["📝 卦象基础信息", "📊 世爻 / 应爻参数录入"])
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        event_name = st.text_input("占问事项", value="足球比赛主队能否取胜")
        sel_ben = st.selectbox("本卦选择", GUA_NAME_LIST, index=GUA_NAME_LIST.index("天雷无妄"))
        input_ben = st.text_input("手动输入本卦（覆盖上方选择）", value="天雷无妄")
        sel_bian = st.selectbox("变卦选择", GUA_NAME_LIST, index=GUA_NAME_LIST.index("天地否"))
        input_bian = st.text_input("手动输入变卦（覆盖上方选择）", value="天地否")
        dong_info = st.text_input("动爻完整信息", value="初爻 父母庚子水 动")
    with c2:
        nian = st.number_input("年份", value=2026, min_value=1990, max_value=2100)
        yue = st.number_input("月份", value=7, min_value=1, max_value=12)
        ri = st.number_input("日期", value=26, min_value=1, max_value=31)
        chen = st.number_input("时辰(0~23)", value=10, min_value=0, max_value=23)
    ben_gua = input_ben.strip() if input_ben.strip() else sel_ben
    bian_gua = input_bian.strip() if input_bian.strip() else sel_bian

with tab2:
    st.subheader("🏠 世爻（代表主队）参数")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        shi_m = st.selectbox("世爻 月建状态", MONTH_STATE)
        shi_d = st.selectbox("世爻 日辰状态", DAY_STATE)
        shi_qin = st.selectbox("世爻六亲", LIUQIN_LIST)
    with sc2:
        shi_san = st.selectbox("世爻 三合局状态", SANHE_STATE)
        shi_db = st.selectbox("世爻 动变情况", DONG_BIAN_STATE)
    with sc3:
        shi_shen = st.selectbox("世爻六神", SHEN_LIST)
        shi_ws = st.selectbox("世爻旺衰判定", WANGSHUAI_FLAG)

    st.divider()
    st.subheader("🏟️ 应爻（代表客队）参数")
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        ying_m = st.selectbox("应爻 月建状态", MONTH_STATE)
        ying_d = st.selectbox("应爻 日辰状态", DAY_STATE)
    with ec2:
        ying_san = st.selectbox("应爻 三合局状态", SANHE_STATE)
        ying_db = st.selectbox("应爻 动变情况", DONG_BIAN_STATE)
    with ec3:
        ying_shen = st.selectbox("应爻六神", SHEN_LIST)
        ying_ws = st.selectbox("应爻旺衰判定", WANGSHUAI_FLAG)

    st.divider()
    sy_rel = st.selectbox("世应五行生克关系", SHI_YING_RELATION)

# 运算触发按钮
if st.button("⚡ 启动量化推演【V2.0完整版】", type="primary"):
    valid = True
    if ben_gua not in GUA_DB:
        st.error(f"本卦【{ben_gua}】名称错误，不在六十四卦库！")
        valid = False
    if bian_gua not in GUA_DB:
        st.error(f"变卦【{bian_gua}】名称错误，不在六十四卦库！")
        valid = False

    if valid:
        st.success("✅ 参数校验通过，开始模型计算")
        shi_score, ying_score, delta, conclusion, tips = calculate_model(
            shi_m, shi_d, shi_san, shi_db, shi_shen, shi_ws, shi_qin,
            ying_m, ying_d, ying_san, ying_db, ying_shen, ying_ws,
            sy_rel
        )
        # 基础档案展示
        st.markdown(f"""
### 📋 推演档案
占问事项：{event_name.strip()}
起卦时间：{nian}-{yue:02d}-{ri:02d} {chen:02d}:00
本卦：{ben_gua}｜{GUA_DB[ben_gua]['gong']}
变卦：{bian_gua}｜{GUA_DB[bian_gua]['gong']}
动爻记录：{dong_info.strip()}
        """)
        st.divider()

        # 得分面板
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("主队｜世爻最终得分")
            st.metric("分数", value=f"{shi_score}")
        with col_b:
            st.subheader("客队｜应爻最终得分")
            st.metric("分数", value=f"{ying_score}")

        st.markdown(f"### ⚖️ 双方分值差 Δ = {delta}")
        st.divider()
        st.subheader("🎯 综合推演结论")
        st.warning(conclusion)
        for t in tips:
            st.info(t)
