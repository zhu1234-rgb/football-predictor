import streamlit as st

# ===================== 基础卦库（64卦 宫位、世爻位置） =====================
GUA_INFO = {
    # 乾宫
    "乾为天": {"gong":"乾宫","shi_pos":6,"shi_wuxing":"金","qin":"兄弟"},
    "天风姤": {"gong":"乾宫","shi_pos":1,"shi_wuxing":"金","qin":"兄弟"},
    "天山遁": {"gong":"乾宫","shi_pos":2,"shi_wuxing":"金","qin":"兄弟"},
    "天地否": {"gong":"乾宫","shi_pos":3,"shi_wuxing":"金","qin":"兄弟"},
    "风地观": {"gong":"乾宫","shi_pos":4,"shi_wuxing":"金","qin":"兄弟"},
    "山地剥": {"gong":"乾宫","shi_pos":5,"shi_wuxing":"金","qin":"兄弟"},
    "火地晋": {"gong":"乾宫","shi_pos":5,"shi_wuxing":"土","qin":"官鬼"},
    "火天大有": {"gong":"乾宫","shi_pos":6,"shi_wuxing":"金","qin":"兄弟"},
    # 兑宫
    "兑为泽": {"gong":"兑宫","shi_pos":6,"shi_wuxing":"金","qin":"兄弟"},
    "泽水困": {"gong":"兑宫","shi_pos":1,"shi_wuxing":"金","qin":"兄弟"},
    "泽地萃": {"gong":"兑宫","shi_pos":2,"shi_wuxing":"金","qin":"兄弟"},
    "泽山咸": {"gong":"兑宫","shi_pos":3,"shi_wuxing":"金","qin":"兄弟"},
    "水山蹇": {"gong":"兑宫","shi_pos":4,"shi_wuxing":"金","qin":"兄弟"},
    "地山谦": {"gong":"兑宫","shi_pos":5,"shi_wuxing":"金","qin":"兄弟"},
    "雷山小过": {"gong":"兑宫","shi_pos":5,"shi_wuxing":"火","qin":"官鬼"},
    "雷泽归妹": {"gong":"兑宫","shi_pos":6,"shi_wuxing":"金","qin":"兄弟"},
    # 离宫
    "离为火": {"gong":"离宫","shi_pos":6,"shi_wuxing":"火","qin":"兄弟"},
    "火山旅": {"gong":"离宫","shi_pos":1,"shi_wuxing":"火","qin":"兄弟"},
    "火风鼎": {"gong":"离宫","shi_pos":2,"shi_wuxing":"火","qin":"兄弟"},
    "火水未济": {"gong":"离宫","shi_pos":3,"shi_wuxing":"火","qin":"兄弟"},
    "山水蒙": {"gong":"离宫","shi_pos":4,"shi_wuxing":"火","qin":"兄弟"},
    "风水涣": {"gong":"离宫","shi_pos":5,"shi_wuxing":"火","qin":"兄弟"},
    "天水讼": {"gong":"离宫","shi_pos":5,"shi_wuxing":"水","qin":"官鬼"},
    "天火同人": {"gong":"离宫","shi_pos":6,"shi_wuxing":"火","qin":"兄弟"},
    # 震宫
    "震为雷": {"gong":"震宫","shi_pos":6,"shi_wuxing":"木","qin":"兄弟"},
    "雷地豫": {"gong":"震宫","shi_pos":1,"shi_wuxing":"木","qin":"兄弟"},
    "雷水解": {"gong":"震宫","shi_pos":2,"shi_wuxing":"木","qin":"兄弟"},
    "雷风恒": {"gong":"震宫","shi_pos":3,"shi_wuxing":"木","qin":"兄弟"},
    "地风升": {"gong":"震宫","shi_pos":4,"shi_wuxing":"木","qin":"兄弟"},
    "水风井": {"gong":"震宫","shi_pos":5,"shi_wuxing":"木","qin":"兄弟"},
    "泽风大过": {"gong":"震宫","shi_pos":5,"shi_wuxing":"金","qin":"官鬼"},
    "泽雷随": {"gong":"震宫","shi_pos":6,"shi_wuxing":"木","qin":"兄弟"},
    # 巽宫
    "巽为风": {"gong":"巽宫","shi_pos":6,"shi_wuxing":"木","qin":"兄弟"},
    "风天小畜": {"gong":"巽宫","shi_pos":1,"shi_wuxing":"木","qin":"兄弟"},
    "风火家人": {"gong":"巽宫","shi_pos":2,"shi_wuxing":"木","qin":"兄弟"},
    "风雷益": {"gong":"巽宫","shi_pos":3,"shi_wuxing":"木","qin":"兄弟"},
    "天雷无妄": {"gong":"巽宫","shi_pos":4,"shi_wuxing":"木","qin":"兄弟"},
    "火雷噬嗑": {"gong":"巽宫","shi_pos":5,"shi_wuxing":"木","qin":"兄弟"},
    "山雷颐": {"gong":"巽宫","shi_pos":5,"shi_wuxing":"土","qin":"官鬼"},
    "山风蛊": {"gong":"巽宫","shi_pos":6,"shi_wuxing":"木","qin":"兄弟"},
    # 坎宫
    "坎为水": {"gong":"坎宫","shi_pos":6,"shi_wuxing":"水","qin":"兄弟"},
    "水泽节": {"gong":"坎宫","shi_pos":1,"shi_wuxing":"水","qin":"兄弟"},
    "水雷屯": {"gong":"坎宫","shi_pos":2,"shi_wuxing":"水","qin":"兄弟"},
    "水火既济": {"gong":"坎宫","shi_pos":3,"shi_wuxing":"水","qin":"兄弟"},
    "泽火革": {"gong":"坎宫","shi_pos":4,"shi_wuxing":"水","qin":"兄弟"},
    "雷火丰": {"gong":"坎宫","shi_pos":5,"shi_wuxing":"水","qin":"兄弟"},
    "地火明夷": {"gong":"坎宫","shi_pos":5,"shi_wuxing":"土","qin":"官鬼"},
    "地水师": {"gong":"坎宫","shi_pos":6,"shi_wuxing":"水","qin":"兄弟"},
    # 艮宫
    "艮为山": {"gong":"艮宫","shi_pos":6,"shi_wuxing":"土","qin":"兄弟"},
    "山火贲": {"gong":"艮宫","shi_pos":1,"shi_wuxing":"土","qin":"兄弟"},
    "山天大畜": {"gong":"艮宫","shi_pos":2,"shi_wuxing":"土","qin":"兄弟"},
    "山泽损": {"gong":"艮宫","shi_pos":3,"shi_wuxing":"土","qin":"兄弟"},
    "火泽睽": {"gong":"艮宫","shi_pos":4,"shi_wuxing":"土","qin":"兄弟"},
    "天泽履": {"gong":"艮宫","shi_pos":5,"shi_wuxing":"土","qin":"兄弟"},
    "风泽中孚": {"gong":"艮宫","shi_pos":5,"shi_wuxing":"木","qin":"官鬼"},
    "风山渐": {"gong":"艮宫","shi_pos":6,"shi_wuxing":"土","qin":"兄弟"},
    # 坤宫
    "坤为地": {"gong":"坤宫","shi_pos":6,"shi_wuxing":"土","qin":"兄弟"},
    "地雷复": {"gong":"坤宫","shi_pos":1,"shi_wuxing":"土","qin":"兄弟"},
    "地泽临": {"gong":"坤宫","shi_pos":2,"shi_wuxing":"土","qin":"兄弟"},
    "地天泰": {"gong":"坤宫","shi_pos":3,"shi_wuxing":"土","qin":"兄弟"},
    "雷天大壮": {"gong":"坤宫","shi_pos":4,"shi_wuxing":"土","qin":"兄弟"},
    "泽天夬": {"gong":"坤宫","shi_pos":5,"shi_wuxing":"土","qin":"兄弟"},
    "水天需": {"gong":"坤宫","shi_pos":5,"shi_wuxing":"水","qin":"官鬼"},
    "水地比": {"gong":"坤宫","shi_pos":6,"shi_wuxing":"土","qin":"兄弟"},
}

# 月建五行映射（简易干支五行，后续可完善完整万年历）
MONTH_WUXING = {1:"木",2:"木",3:"土",4:"火",5:"火",6:"土",7:"金",8:"金",9:"土",10:"水",11:"水",12:"土"}

# ===================== 自动解析函数：卦象→世爻全套参数 =====================
def parse_shi_ying_param(main_gua_name, month, day, shi_pos_in_gua, dong_text):
    """
    输入：本卦名称、月份、日、世爻爻位、动爻文字
    输出：世爻全套旺衰参数（自动匹配下拉选项）
    """
    base = GUA_INFO[main_gua_name]
    shi_wuxing = base["shi_wuxing"]
    shi_qin = base["shi_qin"]
    yue_wuxing = MONTH_WUXING[month]

    # ========= 自动判定月建状态 =========
    if shi_wuxing == yue_wuxing:
        yue_state = "临月建(+2)"
    elif (yue_wuxing == "木" and shi_wuxing in ["火"]) or \
         (yue_wuxing == "火" and shi_wuxing in ["土"]) or \
         (yue_wuxing == "土" and shi_wuxing in ["金"]) or \
         (yue_wuxing == "金" and shi_wuxing in ["水"]) or \
         (yue_wuxing == "水" and shi_wuxing in ["木"]):
        yue_state = "月生(+1)"
    elif (yue_wuxing == "木" and shi_wuxing in ["土"]) or \
         (yue_wuxing == "火" and shi_wuxing in ["金"]) or \
         (yue_wuxing == "土" and shi_wuxing in ["水"]) or \
         (yue_wuxing == "金" and shi_wuxing in ["木"]) or \
         (yue_wuxing == "水" and shi_wuxing in ["火"]):
        yue_state = "月克(-1)"
    else:
        yue_state = "休囚(0)"

    # ========= 动变简易判定（从文本识别进退，你输入动爻文本自动识别） =========
    if "化进" in dong_text:
        dong_state = "动而化进神(+1.0)"
    elif "化退" in dong_text:
        dong_state = "动而化退神(-1.0)"
    elif "化回头生" in dong_text:
        dong_state = "动化回头生(+1.5)"
    elif "化回头克" in dong_text:
        dong_state = "动化回头克(-1.5)"
    elif "静爻" in dong_text or dong_text == "无动爻":
        dong_state = "静爻(0)"
    else:
        dong_state = "动无进退(+0.5)"

    # 初始默认，后续可接入日辰完整干支库、三合局、六神自动算法
    ri_state = "普通(0)"
    sanhe_state = "无三合局(0)"
    liushen = "青龙"

    return {
        "shi_wuxing":shi_wuxing,
        "shi_qin":shi_qin,
        "yue_state":yue_state,
        "ri_state":ri_state,
        "sanhe_state":sanhe_state,
        "dong_state":dong_state,
        "liushen":liushen
    }

# ===================== 二十八法推演核心函数 =====================
def liu_yao_28fa_analyse(main_gua, bian_gua, shi_param, ying_param):
    tips = []
    result = "待定"
    shi_score = 0
    ying_score = 0

    # 分数换算
    score_map = {
        "临月建(+2)":2,"月生(+1)","休囚(0)":0,"月克(-1)":-1,
        "临日/日合起旺(+2)":2,"普通(0)":0,"日克(-1)":-1,
        "三合局中神(+3)":3,"无三合局(0)":0,
        "动而化进神(+1.0)":1,"动化退神(-1.0)":-1,"静爻(0)":0
    }
    shi_score += score_map.get(shi_param["yue_state"],0)
    shi_score += score_map.get(shi_param["ri_state"],0)
    shi_score += score_map.get(shi_param["sanhe_state"],0)
    shi_score += score_map.get(shi_param["dong_state"],0)

    # 格局判定
    liuchong_list = ["乾为天","兑为泽","离为火","震为雷","巽为风","坎为水","艮为山","坤为地","天雷无妄"]
    liuhe_list = ["天地否","地天泰","雷风恒","风泽中孚","山泽损","泽山咸","风火家人","水泽节"]
    if main_gua in liuchong_list:
        tips.append("【格局】本卦六冲：赛事起伏大，波动较强")
    if bian_gua in liuhe_list:
        tips.append("【格局】变卦六合：局势收敛，平局概率上升")

    tips.append(f"【得分统计】主队世爻综合得分：{shi_score}分")

    if shi_score >= 3:
        result = "主队优势，看好主队不败"
    elif shi_score <= -1:
        result = "世爻衰弱，客队占优"
    else:
        result = "双方力量接近，平局风险高"
    return result, tips, shi_score

# ===================== 页面渲染 =====================
st.set_page_config(page_title="六爻赛事推演系统", layout="wide")
st.title("⚽ 足球赛事六爻推演｜自动提取世爻参数模型")

tab1, tab2 = st.tabs(["📝卦象基础信息","📊世爻/应爻参数录入(自动解析)"])

with tab1:
    match_title = st.text_input("占问事项", value="足球比赛主队能不能赢")
    col1,col2 = st.columns(2)
    with col1:
        main_gua_raw = st.text_input("本卦名称", value="天雷无妄")
        bian_gua_raw = st.text_input("变卦名称", value="天地否")
        dong_info = st.text_input("动爻完整文字信息", value="初爻 父母庚子水 ○动")
    with col2:
        year = st.number_input("年份", value=2026)
        month = st.number_input("月份(1-12)", value=7)
        day = st.number_input("日期", value=23)
        shi_chen = st.number_input("时辰(0~23)", value=10)

    # 清洗空格
    main_gua = main_gua_raw.strip()
    bian_gua = bian_gua_raw.strip()

    if st.button("🔍自动解析卦象参数", use_container_width=True):
        if main_gua not in GUA_INFO:
            st.error(f"本卦【{main_gua}】不存在，请核对！")
        else:
            st.session_state["parsed"] = parse_shi_ying_param(main_gua, month, day, GUA_INFO[main_gua]["shi_pos"], dong_info)
            st.session_state["main_gua"] = main_gua
            st.session_state["bian_gua"] = bian_gua
            st.success("✅卦象解析完成！切换到【世爻/应爻参数录入】查看自动填充结果")

with tab2:
    if "parsed" in st.session_state:
        p = st.session_state["parsed"]
        st.subheader("🏠 世爻(代表主队) 参数【自动填入】")
        shi_yue = st.selectbox("世爻 月建状态",
            ["临月建(+2)","月生(+1)","休囚(0)","月克(-1)"],
            index=["临月建(+2)","月生(+1)","休囚(0)","月克(-1)"].index(p["yue_state"]))

        shi_ri = st.selectbox("世爻 日辰状态",
            ["临日/日合起旺(+2)","普通(0)","日克(-1)"],
            index=["临日/日合起旺(+2)","普通(0)","日克(-1)"].index(p["ri_state"]))

        shi_qin = st.selectbox("世爻六亲",["父母","官鬼","妻财","子孙","兄弟"],
            index=["父母","官鬼","妻财","子孙","兄弟"].index(p["shi_qin"]))

        shi_sanhe = st.selectbox("世爻 三合局状态",["三合局中神(+3)","无三合局(0)"],
            index=["三合局中神(+3)","无三合局(0)"].index(p["sanhe_state"]))

        shi_dong = st.selectbox("世爻 动变情况",
            ["动而化进神(+1.0)","动化退神(-1.0)","动化回头生(+1.5)","动化回头克(-1.5)","静爻(0)"],
            index=["动而化进神(+1.0)","动化退神(-1.0)","动化回头生(+1.5)","动化回头克(-1.5)","静爻(0)"].index(p["dong_state"]))

        shi_liushen = st.selectbox("世爻六神",["青龙","朱雀","勾陈","螣蛇","白虎","玄武"],
            index=["青龙","朱雀","勾陈","螣蛇","白虎","玄武"].index(p["liushen"]))

        # 组装参数，供推演函数调用
        shi_param_final = {
            "yue_state":shi_yue,
            "ri_state":shi_ri,
            "sanhe_state":shi_sanhe,
            "dong_state":shi_dong,
            "qin":shi_qin
        }

        st.divider()
        if st.button("🎯启动二十八法推演预测", use_container_width=True):
            conclusion, detail, score = liu_yao_28fa_analyse(
                st.session_state["main_gua"],
                st.session_state["bian_gua"],
                shi_param_final,
                {}
            )
            st.subheader("📜推演明细")
            for line in detail:
                st.markdown(f"- {line}")
            st.subheader("综合推演结论")
            st.warning(f"{conclusion}")
            st.info("⚠易学推演仅作为模型参考因子，请勿作为投注依据！")
    else:
        st.info("请先切换【卦象基础信息】，点击【自动解析卦象参数】")
