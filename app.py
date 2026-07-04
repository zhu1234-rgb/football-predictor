import streamlit as st
import math
import hashlib
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·纯卦象预测", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 纯卦象预测引擎")
st.caption("五维推演：体用生克 | 卦象属性 | 动爻位置 | 卦气旺衰 | 卦名吉凶 | 队名起卦")

# ============================================================
# 2. 赛事列表
# ============================================================
LEAGUE_AVG_TOTAL = {
    "英超": 2.8, "西甲": 2.6, "德甲": 2.9, "意甲": 2.5, "法甲": 2.5,
    "欧冠": 2.6, "欧联": 2.5, "欧协联": 2.4,
    "日职": 2.4, "日乙": 2.3, "K联赛": 2.3, "K2联赛": 2.2,
    "世界杯": 2.2, "亚洲杯": 2.2, "非洲杯": 2.1, "美洲杯": 2.3, "欧洲杯": 2.4,
    "芬超": 2.4, "芬甲": 2.3, "挪甲": 2.4, "瑞典超": 2.5, "冰岛超": 2.4,
    "爱超": 2.3, "爱甲": 2.2, "苏超": 2.5, "英冠": 2.6, "英甲": 2.5, "英乙": 2.4,
    "荷甲": 2.7, "荷乙": 2.6, "葡超": 2.5, "比甲": 2.5, "土超": 2.4, "俄超": 2.3,
    "奥甲": 2.4, "瑞士超": 2.4, "丹超": 2.5, "波超": 2.3, "克甲": 2.3,
    "巴西甲": 2.4, "巴西乙": 2.3, "阿甲": 2.3, "美职联": 2.6, "墨超": 2.4,
    "中超": 2.5, "澳超": 2.6, "沙特联": 2.5, "阿联酋超": 2.4, "卡塔尔联": 2.3,
    "女足世界杯": 2.0, "女足英超": 2.2,
}

# ============================================================
# 3. 战意系数
# ============================================================
ZHAN_YI_LIST = [
    ("🏆 决赛生死战", 1.45),
    ("🔥 出线/保级生死战", 1.40),
    ("⚔️ 洲际资格卡位战", 1.25),
    ("💢 德比复仇大战", 1.22),
    ("🏅 淘汰赛", 1.20),
    ("📈 刷净胜球卡位战", 1.10),
    ("⚽ 普通联赛", 1.00),
    ("🏠 主场荣誉轮换", 0.90),
    ("😐 无欲无求", 0.85),
    ("🧪 提前出线练兵", 0.78),
    ("📉 已降级摆烂", 0.70),
    ("🤝 友谊赛/热身赛", 0.65),
]

# ============================================================
# 4. 卦象数据
# ============================================================
GUA_LEI_XIANG = {
    "乾": {"五行":"金","人物":"领导、父亲、冠军","比赛":"冠军、强势方、大胜"},
    "坤": {"五行":"土","人物":"母亲、老妇、民众","比赛":"被动挨打、防守反击"},
    "震": {"五行":"木","人物":"长男、军人、新秀","比赛":"新锐冲击、快速反击"},
    "巽": {"五行":"木","人物":"长女、教师、替补","比赛":"边路传中、定位球"},
    "坎": {"五行":"水","人物":"中男、医生、守门员","比赛":"防守稳固、点球大战"},
    "离": {"五行":"火","人物":"中女、文人、核心球员","比赛":"核心发挥、进球大战"},
    "艮": {"五行":"土","人物":"少男、后卫、替补","比赛":"防守反击、铁桶阵"},
    "兑": {"五行":"金","人物":"少女、歌手、边锋","比赛":"边路突破、点球决胜"}
}
GUA_XING_QING = {
    "乾": "刚健主动，冠军气质，进攻为主",
    "坤": "柔顺被动，防守反击，稳扎稳打",
    "震": "活跃冲动，快速反击，冲击力强",
    "巽": "灵活多变，边路渗透，定位球战术",
    "坎": "沉稳防守，门将神勇，点球决胜",
    "离": "华丽进攻，核心球员，进球大战",
    "艮": "坚固防守，密集阵型，小胜格局",
    "兑": "边路突破，点球机会，伤病隐患"
}
def get_gua_style(gua):
    return GUA_XING_QING.get(gua, "常规打法")

# ============================================================
# 5. 卦象数据结构
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

# ============================================================
# 6. 卦名吉凶评级
# ============================================================
GUA_JI_XIONG = {
    "泰":"大吉，天地交泰，主队有利",
    "否":"大凶，天地不交，客队有利",
    "谦":"大吉，谦虚谨慎，主队有利",
    "豫":"吉，愉悦和乐，主队有利",
    "随":"吉，随顺从时，主队有利",
    "蛊":"凶，积弊腐败，客队有利",
    "临":"吉，居高临下，主队有利",
    "观":"中，观察等待，平局倾向",
    "噬嗑":"中，咬合阻碍，客队有利",
    "贲":"中，文饰外表，主队有利",
    "剥":"凶，剥落衰败，客队有利",
    "复":"吉，复归正道，主队有利",
    "无妄":"吉，不妄为，主队有利",
    "大畜":"吉，积蓄力量，主队有利",
    "颐":"中，颐养自守，平局倾向",
    "大过":"凶，过度极端，客队有利",
    "坎":"凶，险陷重重，客队有利",
    "离":"中，依附光明，主队有利",
    "咸":"吉，感应相通，主队有利",
    "恒":"中，恒久不变，平局倾向",
    "遁":"凶，退避隐遁，客队有利",
    "大壮":"吉，壮大强盛，主队有利",
    "晋":"吉，前进发展，主队有利",
    "明夷":"凶，光明受伤，客队有利",
    "家人":"吉，家庭和睦，主队有利",
    "睽":"凶，乖离背反，客队有利",
    "蹇":"凶，艰难险阻，客队有利",
    "解":"吉，解脱化解，主队有利",
    "损":"凶，减损损失，客队有利",
    "益":"吉，增益受益，主队有利",
    "夬":"中，决断果敢，主队有利",
    "姤":"中，相遇邂逅，平局倾向",
    "萃":"吉，聚集荟萃，主队有利",
    "升":"吉，上升进步，主队有利",
    "困":"凶，困顿艰难，客队有利",
    "井":"中，井养不穷，平局倾向",
    "革":"中，变革革新，客队有利",
    "鼎":"吉，鼎立稳固，主队有利",
    "震":"中，震动惊醒，平局倾向",
    "艮":"中，止于当止，平局倾向",
    "渐":"吉，循序渐进，主队有利",
    "归妹":"中，归嫁之象，客队有利",
    "丰":"吉，丰盛壮大，主队有利",
    "旅":"凶，旅居在外，客队有利",
    "巽":"中，谦逊顺从，平局倾向",
    "兑":"吉，喜悦愉悦，主队有利",
    "涣":"凶，涣散离散，客队有利",
    "节":"中，节制有度，平局倾向",
    "中孚":"吉，诚信感化，主队有利",
    "小过":"中，小有超过，客队有利",
    "既济":"吉，事已成就，主队有利",
    "未济":"凶，事未成就，客队有利",
    "乾":"大吉，刚健进取，主队有利",
    "坤":"中，柔顺包容，平局倾向",
}
def get_gua_ji_xiong(gua):
    return GUA_JI_XIONG.get(gua, "中，常规卦象，平局倾向")

# ============================================================
# 7. 自动起卦函数（队名起卦）
# ============================================================
def auto_gua_by_teams(home, away):
    combined = f"{home}_{away}"
    hash_obj = hashlib.md5(combined.encode())
    hex_digest = hash_obj.hexdigest()
    seed = int(hex_digest[:8], 16)
    zhu_index = seed % 64
    bian_index = (seed // 64) % 64
    dong_index = seed % 6
    dong_yao_list = ["初爻","二爻","三爻","四爻","五爻","上爻"]
    dong_yao = dong_yao_list[dong_index]
    return GUA_LIST[zhu_index], GUA_LIST[bian_index], dong_yao

# ============================================================
# 8. 五行生克
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
# 9. 六爻逐爻详解
# ============================================================
def analyze_yaos(zhu_gua, bian_gua, dong_yao):
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    yao_wei_xiang = {
        "初爻": "震位，主足、根基、开端、民众、基层",
        "二爻": "离位，主腹、内心、文书、家宅、中层",
        "三爻": "艮位，主手、门户、兄弟、竞争、转折",
        "四爻": "巽位，主股、妻财、市场、商旅、外联",
        "五爻": "坎位，主耳、君王、道路、官非、中枢",
        "上爻": "兑位，主口、外境、神佛、末路、结果"
    }
    yao_list = []
    for yname in yao_names:
        is_dong = (yname == dong_yao)
        if is_dong:
            dong_detail = {
                "初爻": "动于初爻（震位）：事件根基变动，开局或有变数。",
                "二爻": "动于二爻（离位）：内部或有调整，中场控制关键。",
                "三爻": "动于三爻（艮位）：走势在中段发生变化。",
                "四爻": "动于四爻（巽位）：边路或替补可能成为奇兵。",
                "五爻": "动于五爻（坎位）：核心球员或关键判罚影响全局。",
                "上爻": "动于上爻（兑位）：尾声或有绝杀/绝平。"
            }
            desc = dong_detail.get(yname, "动爻需结合全卦。")
        else:
            static_detail = {
                "初爻": "静于初爻：基础稳定，开局稳健。",
                "二爻": "静于二爻：内部稳定，心态平和。",
                "三爻": "静于三爻：中段僵持。",
                "四爻": "静于四爻：边路稳定。",
                "五爻": "静于五爻：中枢稳固，核心正常发挥。",
                "上爻": "静于上爻：结局平稳。"
            }
            desc = static_detail.get(yname, "静爻常规解读。")
        wei_xiang = yao_wei_xiang.get(yname, "")
        yao_list.append({
            "爻位": yname,
            "是否动爻": is_dong,
            "爻位取象": wei_xiang,
            "解读": desc
        })
    return yao_list

# ============================================================
# 10. 五维推演核心函数
# ============================================================
def five_dimension_analysis(zhu_gua, bian_gua, dong_yao, match_time=None):
    score = 0.0
    details = []
    scores_detail = {}

    # 维度1：体用生克（权重30%）
    if dong_yao == "无动爻":
        details.append("体用生克：无动爻，体用比和，主客均衡")
        scores_detail["体用生克"] = 0
    else:
        dong_idx = {"初爻":0,"二爻":1,"三爻":2,"四爻":3,"五爻":4,"上爻":5}[dong_yao]
        shang, xia = GUA_STRUCT[zhu_gua]
        shang_wu = GUA_WUXING_MAP[shang]
        xia_wu = GUA_WUXING_MAP[xia]
        if dong_idx < 3:
            ti_wu, yong_wu = shang_wu, xia_wu
            detail_add = "（下卦为用，上卦为体）"
        else:
            ti_wu, yong_wu = xia_wu, shang_wu
            detail_add = "（上卦为用，下卦为体）"
        rel = wuxing_sheng_ke(ti_wu, yong_wu)
        if rel == -2:
            score += 0.30
            details.append(f"体用生克：用生体，客生主，主队得利 {detail_add}")
            scores_detail["体用生克"] = 0.30
        elif rel == 2:
            score -= 0.30
            details.append(f"体用生克：用克体，客克主，客队占优 {detail_add}")
            scores_detail["体用生克"] = -0.30
        elif rel == 1:
            score -= 0.15
            details.append(f"体用生克：体生用，主生客，主队消耗大，客队不败 {detail_add}")
            scores_detail["体用生克"] = -0.15
        elif rel == -1:
            score += 0.20
            details.append(f"体用生克：体克用，主克客，主队胜机更大 {detail_add}")
            scores_detail["体用生克"] = 0.20
        else:
            details.append(f"体用生克：比和，主客均衡 {detail_add}")
            scores_detail["体用生克"] = 0

    # 维度2：卦象属性（权重25%）
    attr_score = 0
    attr_detail = []
    if zhu_gua in LIUHE_SET:
        attr_score += 0.15
        attr_detail.append("六合卦→平局倾向高")
    if bian_gua in LIUHE_SET:
        attr_score += 0.10
        attr_detail.append("变卦六合→趋平")
    if zhu_gua in LIUCHONG_SET:
        attr_score -= 0.20
        attr_detail.append("六冲卦→分胜负")
    if zhu_gua in GUIHUN_SET:
        attr_score += 0.10
        attr_detail.append("归魂卦→胶着反复")
    if zhu_gua in YOUHUN_SET:
        attr_score -= 0.15
        attr_detail.append("游魂卦→客不败")
    if zhu_gua == "明夷" or bian_gua == "明夷":
        attr_score -= 0.10
        attr_detail.append("明夷卦→客队有利")
    score += attr_score * 0.8
    details.append(f"卦象属性：{attr_detail[0] if attr_detail else '常规卦象'}")
    scores_detail["卦象属性"] = attr_score

    # 维度3：动爻位置（权重20%）
    dong_score = 0
    if dong_yao == "无动爻":
        details.append("动爻位置：无动爻，局势稳定")
    else:
        yao_effect = {"初爻":0.1,"二爻":0.05,"三爻":0,"四爻":-0.05,"五爻":-0.1,"上爻":-0.15}
        dong_score = yao_effect.get(dong_yao, 0)
        yao_desc = {
            "初爻": "动于初爻：开局定势",
            "二爻": "动于二爻：内部调整",
            "三爻": "动于三爻：中段转折",
            "四爻": "动于四爻：替补变量",
            "五爻": "动于五爻：核心关键",
            "上爻": "动于上爻：终局之变"
        }
        details.append(f"动爻位置：{yao_desc.get(dong_yao, '')}")
    score += dong_score * 0.4
    scores_detail["动爻位置"] = dong_score

    # 维度4：卦气旺衰（权重15%）
    if match_time:
        month = match_time.month
    else:
        month = datetime.now().month
    if month in [1,2]: month_wuxing = "木"
    elif month in [4,5]: month_wuxing = "火"
    elif month in [7,8]: month_wuxing = "金"
    elif month in [10,11]: month_wuxing = "水"
    else: month_wuxing = "土"
    
    shang, xia = GUA_STRUCT[zhu_gua]
    gua_wuxing = GUA_WUXING_MAP[shang]
    sheng = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
    ke = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
    qi_score = 0
    if month_wuxing == gua_wuxing:
        qi_score = 0.05
        details.append(f"卦气旺衰：卦气与月建同五行")
    elif sheng.get(month_wuxing) == gua_wuxing:
        qi_score = 0.10
        details.append(f"卦气旺衰：月建生卦气，主队得势")
    elif ke.get(month_wuxing) == gua_wuxing:
        qi_score = -0.10
        details.append(f"卦气旺衰：月建克卦气，主队受压")
    else:
        details.append(f"卦气旺衰：月建与卦气无生克")
    score += qi_score * 0.5
    scores_detail["卦气旺衰"] = qi_score

    # 维度5：卦名吉凶（权重10%）
    ji_xiong = get_gua_ji_xiong(zhu_gua)
    jx_score = 0
    if "大吉" in ji_xiong or "吉" in ji_xiong:
        jx_score = 0.15
    elif "大凶" in ji_xiong or "凶" in ji_xiong:
        jx_score = -0.15
    else:
        jx_score = 0
    score += jx_score * 0.3
    details.append(f"卦名吉凶：{ji_xiong}")
    scores_detail["卦名吉凶"] = jx_score

    # 综合判断
    ping_ju_base = 1 - min(abs(score) * 0.8, 0.7)
    if zhu_gua in LIUHE_SET:
        ping_ju_tend = min(ping_ju_base + 0.25, 0.95)
    elif bian_gua in LIUHE_SET:
        ping_ju_tend = min(ping_ju_base + 0.15, 0.95)
    else:
        ping_ju_tend = ping_ju_base
    ping_ju_tend = max(0.1, min(0.95, ping_ju_tend))
    
    if ping_ju_tend > 0.55:
        first = "平局"
        second = "客胜" if score < 0 else "主胜"
    elif score > 0.15:
        first = "主胜"
        second = "平局" if ping_ju_tend > 0.4 else "客胜"
    elif score < -0.15:
        first = "客胜"
        second = "平局" if ping_ju_tend > 0.4 else "主胜"
    else:
        first = "平局"
        second = "主胜" if score > 0 else "客胜"

    return {
        "first": first,
        "second": second,
        "score": round(score, 2),
        "ping_ju_tend": round(ping_ju_tend, 2),
        "details": details,
        "scores_detail": scores_detail,
        "month_wuxing": month_wuxing,
        "gua_wuxing": gua_wuxing,
        "ji_xiong": ji_xiong
    }

# ============================================================
# 11. 自动解卦函数
# ============================================================
def auto_jie_gua(zhu_gua, bian_gua, dong_yao):
    gua_analysis = []
    if zhu_gua in LIUHE_SET:
        gua_analysis.append("六合卦：平局倾向高")
    if zhu_gua in GUIHUN_SET:
        gua_analysis.append("归魂卦：胶着反复")
    if zhu_gua in YOUHUN_SET:
        gua_analysis.append("游魂卦：客不败")
    if zhu_gua in LIUCHONG_SET:
        gua_analysis.append("六冲卦：分胜负")
    if bian_gua in LIUHE_SET:
        gua_analysis.append("变卦六合：趋平")
    if bian_gua == "明夷" or zhu_gua == "明夷":
        gua_analysis.append("明夷卦：客队有利")
    zhu_style = get_gua_style(zhu_gua)
    bian_style = get_gua_style(bian_gua)
    gua_analysis.append(f"主卦风格：{zhu_style}")
    gua_analysis.append(f"变卦风格：{bian_style}")
    yao_details = analyze_yaos(zhu_gua, bian_gua, dong_yao)
    return {
        "analysis": " | ".join(gua_analysis) if gua_analysis else "常规卦象",
        "yao_details": yao_details
    }

# ============================================================
# 12. 界面布局
# ============================================================
if 'zhu_gua' not in st.session_state:
    st.session_state.zhu_gua = "乾"
if 'bian_gua' not in st.session_state:
    st.session_state.bian_gua = "坤"
if 'dong_yao' not in st.session_state:
    st.session_state.dong_yao = "无动爻"
if 'liu_result' not in st.session_state:
    st.session_state.liu_result = auto_jie_gua(st.session_state.zhu_gua, st.session_state.bian_gua, st.session_state.dong_yao)

with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("主队名", placeholder="请输入主队名", value="")
        league = st.selectbox("请选择赛事", list(LEAGUE_AVG_TOTAL.keys()))
    with col2:
        away_team = st.text_input("客队名", placeholder="请输入客队名", value="")
        match_time = st.datetime_input("比赛时间", value=datetime.now())

zhan_yi_opt = st.selectbox("⚔️ 战意系数", ZHAN_YI_LIST, format_func=lambda x: x[0])
zhan_yi = zhan_yi_opt[1]

# ============================================================
# 13. 预测按钮 + 手机友好输出
# ============================================================
if st.button("🚀 纯卦象预测", type="primary", use_container_width=True):
    if not home_team.strip() or not away_team.strip():
        st.warning("⚠️ 请输入主队名和客队名！")
    else:
        # 起卦
        zhu, bian, dong = auto_gua_by_teams(home_team, away_team)
        st.session_state.zhu_gua = zhu
        st.session_state.bian_gua = bian
        st.session_state.dong_yao = dong

        # 五维推演
        five_dim = five_dimension_analysis(zhu, bian, dong, match_time)
        
        # 解卦
        liu_factors = auto_jie_gua(zhu, bian, dong)
        st.session_state.liu_result = liu_factors

        zhan_yi_name = zhan_yi_opt[0]
        s = five_dim['scores_detail']
        time_str = match_time.strftime("%Y-%m-%d %H:%M") if match_time else "未设置"
        
        # ----- 手机友好分段显示 -----
        st.markdown("---")
        
        # 标题
        st.markdown(f"### 📊 {home_team} vs {away_team}")
        st.caption(f"{league} | {time_str} | {zhan_yi_name}")
        
        # 首推/次推（大号突出）
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🏆 首推**")
            st.markdown(f"### {five_dim['first']}")
        with col2:
            st.markdown(f"**🥈 次推**")
            st.markdown(f"### {five_dim['second']}")
        
        st.markdown("---")
        
        # 五维得分（紧凑）
        st.markdown("**五维推演**")
        st.caption(f"综合倾向：{five_dim['score']:+.2f}（正=主胜） | 平局倾向：{five_dim['ping_ju_tend']:.2f}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("体用", f"{s.get('体用生克', 0):+.2f}")
        with col2:
            st.metric("卦象", f"{s.get('卦象属性', 0):+.2f}")
        with col3:
            st.metric("动爻", f"{s.get('动爻位置', 0):+.2f}")
        with col4:
            st.metric("卦气", f"{s.get('卦气旺衰', 0):+.2f}")
        with col5:
            st.metric("卦名", f"{s.get('卦名吉凶', 0):+.2f}")
        
        st.markdown("---")
        
        # 推演详情
        st.markdown("**推演详情**")
        for d in five_dim['details']:
            st.caption(f"• {d}")
        
        st.markdown("---")
        
        # 卦象信息
        st.markdown(f"**卦象**：{zhu} → {bian}　|　**动爻**：{dong}")
        st.caption(f"卦气：{five_dim['gua_wuxing']}（月建{five_dim['month_wuxing']}）")
        st.caption(f"卦名吉凶：{five_dim['ji_xiong']}")
        
        # 详细解读（折叠）
        with st.expander("🔮 详细卦象解读（含逐爻详解）"):
            st.write(f"**主卦**：{zhu}　|　**变卦**：{bian}　|　**动爻**：{dong}")
            st.write(f"**综合倾向分**：{five_dim['score']:+.2f}")
            st.write(f"**平局倾向**：{five_dim['ping_ju_tend']:.2f}")
            st.write("**五维得分**：")
            for k, v in s.items():
                st.write(f"  - {k}：{v:+.2f}")
            st.write("**推演详情**：")
            for d in five_dim['details']:
                st.write(f"  - {d}")
            st.write("---")
            st.subheader("📜 六爻逐爻详解")
            for yao in liu_factors['yao_details']:
                dong_tag = "🔥 动爻" if yao['是否动爻'] else "静爻"
                st.write(f"**{yao['爻位']}** ({dong_tag})")
                st.write(f"  - 爻位取象：{yao['爻位取象']}")
                st.write(f"  - 解读：{yao['解读']}")

st.caption("💡 起卦方式：主队名_客队名 → MD5哈希 → 定卦象")
