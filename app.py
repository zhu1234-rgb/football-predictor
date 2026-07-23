import streamlit as st
import datetime

# ---------- 页面配置 ----------
st.set_page_config(page_title="六爻足球预测", layout="centered")
st.title("⚽ 六爻足球胜平负预测")
st.markdown("输入卦象信息，自动断卦")

# ---------- 输入区 ----------
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        main_gua = st.text_input("主卦名", value="天雷无妄", help="如：天雷无妄、火雷噬嗑")
        bian_gua = st.text_input("变卦名", value="天地否", help="如：天地否、火地晋")
        dong_yao_str = st.text_input("动爻", value="1", help="多个动爻用逗号分隔，如 1,3,5，无动则留空")
    with col2:
        year = st.number_input("年份", value=2026, min_value=2000, max_value=2100, step=1)
        month = st.number_input("月份", value=7, min_value=1, max_value=12, step=1)
        day = st.number_input("日期", value=23, min_value=1, max_value=31, step=1)
        hour = st.number_input("小时（24小时制）", value=10, min_value=0, max_value=23, step=1)

    submitted = st.form_submit_button("开始预测")

# ---------- 核心断卦逻辑（与之前完全一致） ----------
TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

BAGUA = {1:'乾', 2:'兑', 3:'离', 4:'震', 5:'巽', 6:'坎', 7:'艮', 8:'坤'}
SYM_TO_NUM = {'天':1, '泽':2, '火':3, '雷':4, '风':5, '水':6, '山':7, '地':8}
BAGUA_WUXING = {
    '乾':'金', '兑':'金',
    '震':'木', '巽':'木',
    '坎':'水',
    '离':'火',
    '艮':'土', '坤':'土'
}
NAJIA_DIZHI = {
    '乾': ['子','寅','辰','午','申','戌'],
    '震': ['子','寅','辰','午','申','戌'],
    '坎': ['寅','辰','午','申','戌','子'],
    '艮': ['辰','午','申','戌','子','寅'],
    '坤': ['未','巳','卯','丑','亥','酉'],
    '巽': ['丑','亥','酉','未','巳','卯'],
    '离': ['卯','丑','亥','酉','未','巳'],
    '兑': ['巳','卯','丑','亥','酉','未']
}

GUA_INFO = {}

def _init_gua_info():
    palaces = {
        1: ['乾为天', '天风姤', '天山遁', '天地否', '风地观', '山地剥', '火地晋', '火天大有'],
        2: ['兑为泽', '泽水困', '泽地萃', '泽山咸', '水山蹇', '地山谦', '雷山小过', '雷泽归妹'],
        3: ['离为火', '火山旅', '火风鼎', '火水未济', '山水蒙', '风水涣', '天水讼', '天火同人'],
        4: ['震为雷', '雷地豫', '雷水解', '雷风恒', '地风升', '水风井', '泽风大过', '泽雷随'],
        5: ['巽为风', '风天小畜', '风火家人', '风雷益', '天雷无妄', '火雷噬嗑', '山雷颐', '山风蛊'],
        6: ['坎为水', '水泽节', '水雷屯', '水火既济', '泽火革', '雷火丰', '地火明夷', '地水师'],
        7: ['艮为山', '山火贲', '山天大畜', '山泽损', '火泽睽', '天泽履', '风泽中孚', '风山渐'],
        8: ['坤为地', '地雷复', '地泽临', '地天泰', '雷天大壮', '泽天夬', '水天需', '水地比']
    }
    shi_pos = [6,1,2,3,4,5,4,3]
    he_list = ['地天泰', '天地否', '泽山咸', '雷风恒', '水泽节', '火山旅', '山泽损', '泽地萃']
    chong_list = ['乾为天', '兑为泽', '离为火', '震为雷', '巽为风', '坎为水', '艮为山', '坤为地']
    for palace, names in palaces.items():
        for idx, name in enumerate(names):
            shi = shi_pos[idx]
            ying = shi + 3
            if ying > 6:
                ying -= 6
            chong = name in chong_list
            he = name in he_list
            if name in ['乾为天','坤为地','坎为水','离为火','震为雷','巽为风','艮为山','兑为泽']:
                upper_sym = name[0]
                lower_sym = name[2]
            else:
                upper_sym = name[0]
                lower_sym = name[1]
            upper_num = SYM_TO_NUM.get(upper_sym)
            lower_num = SYM_TO_NUM.get(lower_sym)
            if upper_num is None:
                upper_num = {v:k for k,v in BAGUA.items()}.get(upper_sym)
            if lower_num is None:
                lower_num = {v:k for k,v in BAGUA.items()}.get(lower_sym)
            GUA_INFO[name] = {
                'upper': upper_num,
                'lower': lower_num,
                'palace': palace,
                'shi': shi,
                'ying': ying,
                'chong': chong,
                'he': he
            }
_init_gua_info()

def wuxing_of_dizhi(dz):
    map_ = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
            '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
    return map_[dz]

def sheng_ke(wx1, wx2):
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke     = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    if wx1 == wx2:
        return '比和'
    elif sheng[wx1] == wx2:
        return '生'
    elif ke[wx1] == wx2:
        return '克'
    else:
        return '无关'

def get_liuqin(wx, gong_wx):
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke    = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    if wx == gong_wx:
        return '兄弟'
    elif sheng[wx] == gong_wx:
        return '父母'
    elif sheng[gong_wx] == wx:
        return '子孙'
    elif ke[wx] == gong_wx:
        return '官鬼'
    elif ke[gong_wx] == wx:
        return '妻财'
    return ''

def get_yue_zhi(year, month, day):
    if (month == 1 and day >= 6) or (month == 2 and day < 4):
        return 1
    elif (month == 2 and day >= 4) or (month == 3 and day < 6):
        return 2
    elif (month == 3 and day >= 6) or (month == 4 and day < 5):
        return 3
    elif (month == 4 and day >= 5) or (month == 5 and day < 6):
        return 4
    elif (month == 5 and day >= 6) or (month == 6 and day < 6):
        return 5
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        return 6
    elif (month == 7 and day >= 7) or (month == 8 and day < 8):
        return 7
    elif (month == 8 and day >= 8) or (month == 9 and day < 8):
        return 8
    elif (month == 9 and day >= 8) or (month == 10 and day < 8):
        return 9
    elif (month == 10 and day >= 8) or (month == 11 and day < 7):
        return 10
    elif (month == 11 and day >= 7) or (month == 12 and day < 7):
        return 11
    else:
        return 0

def get_day_gz_index(year, month, day):
    start = datetime.datetime(1,1,1)
    target = datetime.datetime(year, month, day)
    delta = (target - start).days
    days2000 = (datetime.datetime(2000,1,1) - start).days
    offset = (30 - days2000 % 60) % 60
    idx = (delta + offset) % 60
    return idx

def pai_pan(main_name, bian_name):
    main = GUA_INFO.get(main_name)
    bian = GUA_INFO.get(bian_name)
    if main is None or bian is None:
        raise ValueError(f"卦名不存在：{main_name} 或 {bian_name}")
    main_upper = main['upper']
    main_lower = main['lower']
    main_palace = main['palace']
    main_gong_wuxing = BAGUA_WUXING[BAGUA[main_palace]]
    main_shi = main['shi']
    main_ying = main['ying']
    upper_name = BAGUA[main_upper]
    lower_name = BAGUA[main_lower]
    dizhi = NAJIA_DIZHI[lower_name][0:3] + NAJIA_DIZHI[upper_name][0:3]
    liuqin = [get_liuqin(wuxing_of_dizhi(dz), main_gong_wuxing) for dz in dizhi]
    shi_ying = [''] * 6
    shi_ying[main_shi-1] = '世'
    shi_ying[main_ying-1] = '应'
    main_info = {
        'name': main_name,
        'palace': main_palace,
        'gong_wuxing': main_gong_wuxing,
        'shi': main_shi,
        'ying': main_ying,
        'dizhi': dizhi,
        'liuqin': liuqin,
        'shi_ying': shi_ying,
        'chong': main['chong'],
        'he': main['he']
    }
    bian_upper = bian['upper']
    bian_lower = bian['lower']
    bian_palace = bian['palace']
    bian_gong_wuxing = BAGUA_WUXING[BAGUA[bian_palace]]
    bian_upper_name = BAGUA[bian_upper]
    bian_lower_name = BAGUA[bian_lower]
    bian_dizhi = NAJIA_DIZHI[bian_lower_name][0:3] + NAJIA_DIZHI[bian_upper_name][0:3]
    bian_liuqin = [get_liuqin(wuxing_of_dizhi(dz), bian_gong_wuxing) for dz in bian_dizhi]
    bian_info = {
        'name': bian_name,
        'dizhi': bian_dizhi,
        'liuqin': bian_liuqin,
        'chong': bian['chong'],
        'he': bian['he']
    }
    return main_info, bian_info

def duan_gua(main_info, bian_info, dong_yao_list, yue_zhi, ri_zhi):
    shi_idx = main_info['shi'] - 1
    ying_idx = main_info['ying'] - 1
    shi_dz = main_info['dizhi'][shi_idx]
    ying_dz = main_info['dizhi'][ying_idx]
    shi_liuqin = main_info['liuqin'][shi_idx]
    ying_liuqin = main_info['liuqin'][ying_idx]

    def score_wang(dz, yue, ri):
        s = 0
        sk = sheng_ke(wuxing_of_dizhi(yue), wuxing_of_dizhi(dz))
        if sk == '生':
            s += 1
        elif sk == '克':
            s -= 1
        sk2 = sheng_ke(wuxing_of_dizhi(ri), wuxing_of_dizhi(dz))
        if sk2 == '生':
            s += 1
        elif sk2 == '克':
            s -= 1
        if dz == ri:
            s += 1
        return s

    shi_score = score_wang(shi_dz, yue_zhi, ri_zhi)
    ying_score = score_wang(ying_dz, yue_zhi, ri_zhi)

    sk_shi_ying = sheng_ke(wuxing_of_dizhi(shi_dz), wuxing_of_dizhi(ying_dz))
    if sk_shi_ying == '克':
        shi_score += 1
        ying_score -= 1
    elif sk_shi_ying == '生':
        shi_score -= 1
        ying_score += 1

    for dong in dong_yao_list:
        idx = dong - 1
        if idx < 0 or idx > 5:
            continue
        main_dz = main_info['dizhi'][idx]
        if idx < len(bian_info['dizhi']):
            bian_dz = bian_info['dizhi'][idx]
        else:
            bian_dz = main_dz
        sk_shi = sheng_ke(wuxing_of_dizhi(main_dz), wuxing_of_dizhi(shi_dz))
        sk_ying = sheng_ke(wuxing_of_dizhi(main_dz), wuxing_of_dizhi(ying_dz))
        if sk_shi == '生':
            shi_score += 0.5
        elif sk_shi == '克':
            shi_score -= 0.5
        if sk_ying == '生':
            ying_score += 0.5
        elif sk_ying == '克':
            ying_score -= 0.5

    is_chong = main_info['chong'] or bian_info['chong']
    is_he = main_info['he'] or bian_info['he']

    if is_chong:
        if shi_score > ying_score:
            shi_score += 1
        elif ying_score > shi_score:
            ying_score += 1
    if is_he:
        shi_score += 0.5
        ying_score += 0.5

    diff = shi_score - ying_score
    if diff > 0.8:
        result = "主胜"
        reason = f"世爻{shi_dz}（{shi_liuqin}）评分 {shi_score:.1f} 高于应爻{ying_dz}（{ying_liuqin}）评分 {ying_score:.1f}，"
        if sk_shi_ying == '克':
            reason += "世爻克应爻，主动压制。"
        elif sk_shi_ying == '生':
            reason += "世爻生应爻但自身更强。"
        else:
            reason += "双方比和但世爻更旺。"
        if is_chong:
            reason += "卦逢六冲。"
    elif diff < -0.8:
        result = "客胜"
        reason = f"应爻{ying_dz}（{ying_liuqin}）评分 {ying_score:.1f} 高于世爻{shi_dz}（{shi_liuqin}）评分 {shi_score:.1f}，"
        if sk_shi_ying == '生':
            reason += "应爻生世爻但自身更旺，反客为主。"
        elif sk_shi_ying == '克':
            reason += "应爻克世爻，客队压制。"
        else:
            reason += "双方比和但应爻更旺。"
        if is_chong:
            reason += "卦逢六冲，客队胜出。"
    else:
        result = "平局"
        reason = f"世应评分接近（主{shi_score:.1f} vs 客{ying_score:.1f}），实力均衡，"
        if is_he:
            reason += "卦逢六合，僵持。"
        else:
            reason += "难分高下。"

    if dong_yao_list:
        reason += f" 动爻：{', '.join(str(x) for x in dong_yao_list)}。"
    else:
        reason += " 六爻安静。"
    return result, reason

# ---------- 处理提交 ----------
if submitted:
    try:
        # 解析动爻
        dong_yao = []
        if dong_yao_str.strip():
            dong_yao = [int(x.strip()) for x in dong_yao_str.split(',') if x.strip()]
            # 简单校验
            for d in dong_yao:
                if d < 1 or d > 6:
                    st.error("动爻编号必须在 1~6 之间")
                    st.stop()

        # 计算月建日辰
        yue_idx = get_yue_zhi(year, month, day)
        yue_zhi = DI_ZHI[yue_idx]
        day_gz_idx = get_day_gz_index(year, month, day)
        ri_gan = TIAN_GAN[day_gz_idx % 10]
        ri_zhi = DI_ZHI[day_gz_idx % 12]

        main_info, bian_info = pai_pan(main_gua.strip(), bian_gua.strip())
        result, reason = duan_gua(main_info, bian_info, dong_yao, yue_zhi, ri_zhi)

        # ---------- 显示结果 ----------
        st.success(f"预测结果：**{result}**")
        with st.expander("查看详细排盘与断因"):
            st.write(f"**主卦**：{main_info['name']}（宫位五行 {main_info['gong_wuxing']}）")
            st.write(f"**变卦**：{bian_info['name']}")
            st.write(f"**世爻位**：{main_info['shi']}，**应爻位**：{main_info['ying']}")
            st.write("**六爻信息（爻位 世应 地支 六亲）**：")
            table = []
            for i in range(6):
                table.append([i+1, main_info['shi_ying'][i], main_info['dizhi'][i], main_info['liuqin'][i]])
            st.table(table)
            st.write(f"**月建**：{yue_zhi}　**日辰**：{ri_gan}{ri_zhi}")
            st.write(f"**断因**：{reason}")

    except Exception as e:
        st.error(f"发生错误：{e}")
        st.stop()
