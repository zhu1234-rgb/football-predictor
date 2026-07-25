import streamlit as st
import datetime
import pandas as pd

# ---------- 页面配置 ----------
st.set_page_config(page_title="六爻足球预测", layout="wide")
st.title("⚽ 六爻足球胜平负预测")
st.markdown("基于野鹤派核心思路，手动输入卦象与时间，自动排盘并展示多维度断卦过程。")

# ====================== 基础数据 ======================
TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
DZ_WX = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE    = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

# 八卦基本象
BAGUA = {1:'乾', 2:'兑', 3:'离', 4:'震', 5:'巽', 6:'坎', 7:'艮', 8:'坤'}
SYM2NUM = {'天':1,'泽':2,'火':3,'雷':4,'风':5,'水':6,'山':7,'地':8}
GUA_WX = {'乾':'金','兑':'金','震':'木','巽':'木','坎':'水','离':'火','艮':'土','坤':'土'}

# 纳甲地支
NAJIA = {
    '乾': ['子','寅','辰','午','申','戌'],
    '震': ['子','寅','辰','午','申','戌'],
    '坎': ['寅','辰','午','申','戌','子'],
    '艮': ['辰','午','申','戌','子','寅'],
    '坤': ['未','巳','卯','丑','亥','酉'],
    '巽': ['丑','亥','酉','未','巳','卯'],
    '离': ['卯','丑','亥','酉','未','巳'],
    '兑': ['巳','卯','丑','亥','酉','未']
}

# ====================== 64卦数据库 ======================
GUA_DB = {}

def _init_db():
    palaces = {
        1: ['乾为天','天风姤','天山遁','天地否','风地观','山地剥','火地晋','火天大有'],
        2: ['兑为泽','泽水困','泽地萃','泽山咸','水山蹇','地山谦','雷山小过','雷泽归妹'],
        3: ['离为火','火山旅','火风鼎','火水未济','山水蒙','风水涣','天水讼','天火同人'],
        4: ['震为雷','雷地豫','雷水解','雷风恒','地风升','水风井','泽风大过','泽雷随'],
        5: ['巽为风','风天小畜','风火家人','风雷益','天雷无妄','火雷噬嗑','山雷颐','山风蛊'],
        6: ['坎为水','水泽节','水雷屯','水火既济','泽火革','雷火丰','地火明夷','地水师'],
        7: ['艮为山','山火贲','山天大畜','山泽损','火泽睽','天泽履','风泽中孚','风山渐'],
        8: ['坤为地','地雷复','地泽临','地天泰','雷天大壮','泽天夬','水天需','水地比']
    }
    shi_pos = [6,1,2,3,4,5,4,3]  # 世爻位置（从初爻到上爻，1-indexed）
    for pal, names in palaces.items():
        for idx, name in enumerate(names):
            if len(name) == 3:
                upper_sym = name[0]
                lower_sym = name[2]
            else:
                upper_sym = name[0]
                lower_sym = name[1]
            upper_num = SYM2NUM.get(upper_sym)
            lower_num = SYM2NUM.get(lower_sym)
            if upper_num is None or lower_num is None:
                continue
            shi = shi_pos[idx]
            ying = shi + 3
            if ying > 6:
                ying -= 6
            GUA_DB[name] = {
                'upper': upper_num, 'lower': lower_num,
                'palace': pal,
                'shi': shi, 'ying': ying,
                'chong': name in ['乾为天','兑为泽','离为火','震为雷','巽为风','坎为水','艮为山','坤为地'],
                'he': name in ['地天泰','天地否','泽山咸','雷风恒','水泽节','火山旅','山泽损','泽地萃']
            }
_init_db()

def get_liuqin(yao_wx, gong_wx):
    if yao_wx == gong_wx: return '兄弟'
    if SHENG[yao_wx] == gong_wx: return '父母'
    if SHENG[gong_wx] == yao_wx: return '子孙'
    if KE[yao_wx] == gong_wx: return '官鬼'
    if KE[gong_wx] == yao_wx: return '妻财'
    return ''

def shengke(wx1, wx2):
    if wx1 == wx2: return '比和'
    if SHENG.get(wx1) == wx2: return '生'
    if KE.get(wx1) == wx2: return '克'
    return ''

# ====================== 时间工具 ======================
def day_gz_index(year, month, day):
    """计算日干支在六十甲子中的索引（0-59）"""
    base = datetime.datetime(1,1,1)
    target = datetime.datetime(year, month, day)
    delta = (target - base).days
    ref = datetime.datetime(2000,1,1)
    ref_delta = (ref - base).days
    ref_gz = 54  # 2000-01-01 戊午 (索引54)
    return (ref_gz + (delta - ref_delta)) % 60

def month_zhi(year, month, day):
    """简化的月建节气近似"""
    if (month == 1 and day >= 6) or (month == 2 and day < 4): return 2
    elif (month == 2 and day >= 4) or (month == 3 and day < 6): return 3
    elif (month == 3 and day >= 6) or (month == 4 and day < 5): return 4
    elif (month == 4 and day >= 5) or (month == 5 and day < 6): return 5
    elif (month == 5 and day >= 6) or (month == 6 and day < 6): return 6
    elif (month == 6 and day >= 6) or (month == 7 and day < 7): return 7
    elif (month == 7 and day >= 7) or (month == 8 and day < 8): return 8
    elif (month == 8 and day >= 8) or (month == 9 and day < 8): return 9
    elif (month == 9 and day >= 8) or (month == 10 and day < 8): return 10
    elif (month == 10 and day >= 8) or (month == 11 and day < 7): return 11
    elif (month == 11 and day >= 7) or (month == 12 and day < 7): return 0
    else: return 1

def hour_gz(day_gan, hour):
    """根据日干和小时（0-23）返回时干支"""
    start_gan = {
        '甲': '甲', '乙': '丙', '丙': '戊', '丁': '庚', '戊': '壬',
        '己': '甲', '庚': '丙', '辛': '戊', '壬': '庚', '癸': '壬'
    }
    gan = start_gan[day_gan]
    gan_idx = TIAN_GAN.index(gan)
    zhi_idx = (hour + 1) // 2 % 12  # 0-1子时，2-3丑时...
    gan_shift = zhi_idx
    real_gan = TIAN_GAN[(gan_idx + gan_shift) % 10]
    real_zhi = DI_ZHI[zhi_idx]
    return real_gan + real_zhi

def get_xunkong(ri_zhi):
    """日辰旬空"""
    xun_start = (DI_ZHI.index(ri_zhi) // 2) * 2
    if xun_start == 0: return ('戌','亥')
    elif xun_start == 2: return ('子','丑')
    elif xun_start == 4: return ('寅','卯')
    elif xun_start == 6: return ('辰','巳')
    elif xun_start == 8: return ('午','未')
    else: return ('申','酉')

def liu_shen(ri_gan):
    """按日干起六神顺序（初爻起）"""
    start = {
        '甲': '青龙', '乙': '青龙',
        '丙': '朱雀', '丁': '朱雀',
        '戊': '勾陈', '己': '螣蛇',
        '庚': '白虎', '辛': '白虎',
        '壬': '玄武', '癸': '玄武'
    }
    order = ['青龙','朱雀','勾陈','螣蛇','白虎','玄武']
    idx = order.index(start[ri_gan])
    rotated = order[idx:] + order[:idx]
    return rotated  # 从初爻到上爻

# ====================== 排盘 ======================
def pai_pan(main_name, bian_name, year, month, day, hour):
    # 时间处理
    yue_idx = month_zhi(year, month, day)
    yue_zhi = DI_ZHI[yue_idx]
    day_gz = day_gz_index(year, month, day)
    ri_gan = TIAN_GAN[day_gz % 10]
    ri_zhi = DI_ZHI[day_gz % 12]
    shi_chen = hour_gz(ri_gan, hour)
    kong = get_xunkong(ri_zhi)
    liushen = liu_shen(ri_gan)

    # 主卦
    main = GUA_DB.get(main_name)
    if not main:
        raise ValueError(f"主卦{main_name}不存在")
    gong_name = BAGUA[main['palace']]
    gong_wx = GUA_WX[gong_name]
    upper_name = BAGUA[main['upper']]
    lower_name = BAGUA[main['lower']]
    main_dz = NAJIA[lower_name][:3] + NAJIA[upper_name][:3]
    main_lq = [get_liuqin(DZ_WX[dz], gong_wx) for dz in main_dz]
    shi = main['shi']
    ying = main['ying']
    shi_ying = ['']*6
    shi_ying[shi-1] = '世'
    shi_ying[ying-1] = '应'
    # 伏神（简单处理：若卦中缺少宫位六亲子孙或妻财，则本宫八纯卦对应爻位伏神）
    # 此处略，仅做显示用

    # 变卦
    bian = GUA_DB.get(bian_name)
    if not bian:
        raise ValueError(f"变卦{bian_name}不存在")
    b_upper_name = BAGUA[bian['upper']]
    b_lower_name = BAGUA[bian['lower']]
    bian_dz = NAJIA[b_lower_name][:3] + NAJIA[b_upper_name][:3]
    bian_gong_wx = GUA_WX[BAGUA[bian['palace']]]
    bian_lq = [get_liuqin(DZ_WX[dz], bian_gong_wx) for dz in bian_dz]

    pan = {
        'year': year, 'month': month, 'day': day, 'hour': hour,
        'yue_zhi': yue_zhi, 'ri_gan': ri_gan, 'ri_zhi': ri_zhi,
        'shi_chen': shi_chen, 'kong': kong, 'liushen': liushen,
        'main': {
            'name': main_name, 'dizhi': main_dz, 'liuqin': main_lq,
            'shi_ying': shi_ying, 'shi': shi, 'ying': ying,
            'chong': main['chong'], 'he': main['he'],
            'gong_wx': gong_wx
        },
        'bian': {
            'name': bian_name, 'dizhi': bian_dz, 'liuqin': bian_lq,
            'chong': bian['chong'], 'he': bian['he']
        }
    }
    return pan

# ====================== 断卦引擎（多维度评分） ======================
def duan_gua_detail(pan, dong_yao_list):
    m = pan['main']
    b = pan['bian']
    shi_idx = m['shi'] - 1
    ying_idx = m['ying'] - 1
    shi_dz = m['dizhi'][shi_idx]
    ying_dz = m['dizhi'][ying_idx]
    shi_wx = DZ_WX[shi_dz]
    ying_wx = DZ_WX[ying_dz]
    shi_lq = m['liuqin'][shi_idx]
    ying_lq = m['liuqin'][ying_idx]
    yue_zhi = pan['yue_zhi']
    ri_zhi = pan['ri_zhi']
    kong = pan['kong']

    # 初始化分数表
    scores = {
        '月令提纲': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '日辰决断': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '世应生克': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '动爻影响': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '三合三会': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '空亡真假': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '六冲/六合': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '六神取象': {'主': 0, '客': 0, '主评': '参考', '客评': '参考'},
        '合计': {'主': 0, '客': 0, '主评': '', '客评': ''}
    }

    # 辅助函数：旺衰打分基数
    def wang_score(dz, yue, ri):
        s = 0
        note = ''
        ysk = shengke(DZ_WX[yue], DZ_WX[dz])
        if ysk == '生': s += 1; note += '得月生 '
        elif ysk == '克': s -= 1; note += '被月克 '
        elif ysk == '比和': s += 0.5; note += '月比和 '
        rsk = shengke(DZ_WX[ri], DZ_WX[dz])
        if rsk == '生': s += 1; note += '得日生 '
        elif rsk == '克': s -= 1; note += '被日克 '
        elif rsk == '比和': s += 0.5; note += '日比和 '
        # 日墓
        if DZ_WX[ri] == '土' and DZ_WX[dz] == '火':  # 火墓在戌，但日支为戌？简化
            pass
        return s, note.strip()

    shi_yue_ri, note_shi = wang_score(shi_dz, yue_zhi, ri_zhi)
    ying_yue_ri, note_ying = wang_score(ying_dz, yue_zhi, ri_zhi)

    scores['月令提纲']['主'] = shi_yue_ri
    scores['月令提纲']['客'] = ying_yue_ri
    scores['月令提纲']['主评'] = note_shi
    scores['月令提纲']['客评'] = note_ying

    # 世应生克
    sk = shengke(shi_wx, ying_wx)
    if sk == '克':
        scores['世应生克']['主'] = 1.5
        scores['世应生克']['客'] = -0.5
        scores['世应生克']['主评'] = '世克应，主队压制'
        scores['世应生克']['客评'] = '被克，被动'
    elif sk == '生':
        scores['世应生克']['主'] = -1.5
        scores['世应生克']['客'] = 0.5
        scores['世应生克']['主评'] = '世生应，泄气'
        scores['世应生克']['客评'] = '受生得益'
    else:
        scores['世应生克']['主'] = 0
        scores['世应生克']['客'] = 0
        scores['世应生克']['主评'] = '比和'
        scores['世应生克']['客评'] = '比和'

    # 动爻影响
    dong_eff_shis = 0
    dong_eff_yings = 0
    dong_notes = []
    for dong in dong_yao_list:
        idx = dong - 1
        main_dz = m['dizhi'][idx]
        main_wx = DZ_WX[main_dz]
        bian_dz = b['dizhi'][idx]
        bian_wx = DZ_WX[bian_dz]
        # 回头生克
        htsk = shengke(bian_wx, main_wx)
        huitou_str = ''
        if htsk == '克':
            huitou_str = '回头克，动爻失力'
            dong_notes.append(f'动爻{main_dz}化{bian_dz}回头克')
            # 动爻被克，自身力量大减，对世应的作用打折
            factor = 0.2
        elif htsk == '生':
            huitou_str = '回头生，动爻增力'
            dong_notes.append(f'动爻{main_dz}化{bian_dz}回头生')
            factor = 2
        else:
            factor = 1

        # 化进/退
        if DZ_WX[main_dz] == DZ_WX[bian_dz]:
            if DI_ZHI.index(bian_dz) == (DI_ZHI.index(main_dz) + 1) % 12:
                dong_notes.append('化进神，力量递增')
                factor *= 1.5
            elif DI_ZHI.index(bian_dz) == (DI_ZHI.index(main_dz) - 1) % 12:
                dong_notes.append('化退神，力量衰减')
                factor *= 0.5

        # 动爻对世应的作用
        sk_shi = shengke(main_wx, shi_wx)
        sk_ying = shengke(main_wx, ying_wx)
        add_shi = 0
        add_ying = 0
        if sk_shi == '生': add_shi = 1 * factor
        elif sk_shi == '克': add_shi = -1.5 * factor
        if sk_ying == '生': add_ying = 1 * factor
        elif sk_ying == '克': add_ying = -1.5 * factor
        dong_eff_shis += add_shi
        dong_eff_yings += add_ying

    scores['动爻影响']['主'] = round(dong_eff_shis, 1)
    scores['动爻影响']['客'] = round(dong_eff_yings, 1)
    scores['动爻影响']['主评'] = '; '.join(dong_notes) if dong_notes else '无动爻'
    scores['动爻影响']['客评'] = ''

    # 空亡
    shi_kong = shi_dz in kong
    ying_kong = ying_dz in kong
    if shi_kong:
        scores['空亡真假']['主'] = -2
        scores['空亡真假']['主评'] = '世爻旬空，无力'
    else:
        scores['空亡真假']['主'] = 0
        scores['空亡真假']['主评'] = '不空'
    if ying_kong:
        scores['空亡真假']['客'] = -2
        scores['空亡真假']['客评'] = '应爻旬空，无力'
    else:
        scores['空亡真假']['客'] = 0
        scores['空亡真假']['客评'] = '不空'

    # 三合局检测（世爻、应爻、日辰、动爻参与）
    sanhe_list = [('申','子','辰'), ('巳','酉','丑'), ('寅','午','戌'), ('亥','卯','未')]
    def has_sanhe(dz_set):
        for h in sanhe_list:
            if set(h).issubset(dz_set):
                return True, h
        return False, None
    all_dz_shi = {shi_dz, ri_zhi}
    all_dz_ying = {ying_dz, ri_zhi}
    for dong in dong_yao_list:
        all_dz_shi.add(m['dizhi'][dong-1])
        all_dz_ying.add(m['dizhi'][dong-1])
    shi_sanhe, he_shi = has_sanhe(all_dz_shi)
    ying_sanhe, he_ying = has_sanhe(all_dz_ying)
    if shi_sanhe:
        scores['三合三会']['主'] = 3
        scores['三合三会']['主评'] = f'三合{he_shi}局成，大旺'
    else:
        scores['三合三会']['主'] = 0
        scores['三合三会']['主评'] = '无'
    if ying_sanhe:
        scores['三合三会']['客'] = 3
        scores['三合三会']['客评'] = f'三合{he_ying}局成，大旺'
    else:
        scores['三合三会']['客'] = 0
        scores['三合三会']['客评'] = '无'

    # 六冲/六合
    chong = m['chong'] or b['chong']
    he = m['he'] or b['he']
    if chong:
        scores['六冲/六合']['主评'] = '六冲卦，拉大差距'
        scores['六冲/六合']['客评'] = '六冲卦'
        # 不加减分，仅在合计时体现倾向
    if he:
        scores['六冲/六合']['主评'] = '六合卦，趋向平衡'
        scores['六冲/六合']['客评'] = '六合卦'
        # 六合拉平
        avg = (scores['月令提纲']['主'] + scores['月令提纲']['客'] +
               scores['日辰决断']['主'] + scores['日辰决断']['客'] +
               scores['世应生克']['主'] + scores['世应生克']['客'] +
               scores['动爻影响']['主'] + scores['动爻影响']['客']) / 2
        # 后期统一处理

    # 六神取象（仅参考，不计分）
    liushen = pan['liushen']
    shi_ls = liushen[shi_idx]
    ying_ls = liushen[ying_idx]
    scores['六神取象']['主评'] = f'{shi_ls}临世'
    scores['六神取象']['客评'] = f'{ying_ls}临应'

    # 合计
    total_shi = (scores['月令提纲']['主'] + scores['日辰决断']['主'] +
                 scores['世应生克']['主'] + scores['动爻影响']['主'] +
                 scores['三合三会']['主'] + scores['空亡真假']['主'])
    total_ying = (scores['月令提纲']['客'] + scores['日辰决断']['客'] +
                  scores['世应生克']['客'] + scores['动爻影响']['客'] +
                  scores['三合三会']['客'] + scores['空亡真假']['客'])

    # 六合修正
    if he:
        avg_total = (total_shi + total_ying) / 2
        total_shi = avg_total
        total_ying = avg_total
        scores['六冲/六合']['主'] = round(avg_total - total_shi, 1)
        scores['六冲/六合']['客'] = round(avg_total - total_ying, 1)
        total_shi = avg_total
        total_ying = avg_total
    # 六冲修正
    elif chong:
        if total_shi > total_ying:
            bonus = 1
            total_shi += bonus
            total_ying -= 0.5
            scores['六冲/六合']['主'] = bonus
            scores['六冲/六合']['客'] = -0.5
        elif total_ying > total_shi:
            bonus = 1
            total_ying += bonus
            total_shi -= 0.5
            scores['六冲/六合']['客'] = bonus
            scores['六冲/六合']['主'] = -0.5
        else:
            scores['六冲/六合']['主'] = 0
            scores['六冲/六合']['客'] = 0

    scores['合计']['主'] = round(total_shi, 1)
    scores['合计']['客'] = round(total_ying, 1)

    # 判定
    diff = total_shi - total_ying
    if diff > 1.5:
        result = "主胜"
        reason = "主队综合优势明显"
    elif diff < -1.5:
        result = "客胜"
        reason = "客队综合优势明显"
    else:
        result = "平局"
        reason = "双方实力接近，平局概率高"

    return scores, result, reason

# ====================== UI 界面 ======================
with st.form("predict_form"):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        main_gua = st.text_input("主卦名", "天水讼", help="如：天水讼、天雷无妄")
        bian_gua = st.text_input("变卦名", "天泽履", help="如：天泽履、天地否")
    with col2:
        dong_yao_str = st.text_input("动爻 (逗号分隔, 如 1,3)", "1", help="多个动爻用逗号分隔，无动爻留空")
    with col3:
        year = st.number_input("年", 2026, 2000, 2100, 1)
        month = st.number_input("月", 4, 1, 12, 1)
        day = st.number_input("日", 18, 1, 31, 1)
        hour = st.number_input("时(0-23)", 15, 0, 23, 1)

    submitted = st.form_submit_button("⚡ 开始预测")

if submitted:
    try:
        # 解析动爻
        dong_list = []
        if dong_yao_str.strip():
            dong_list = [int(x.strip()) for x in dong_yao_str.split(',') if x.strip()]
            if any(d < 1 or d > 6 for d in dong_list):
                st.error("动爻编号须在1-6之间")
                st.stop()

        # 排盘
        pan = pai_pan(main_gua.strip(), bian_gua.strip(), year, month, day, hour)
        scores, result, reason = duan_gua_detail(pan, dong_list)

        # ---------- 结果展示 ----------
        st.success(f"### 预测结果：{result} ({reason})")

        # 排盘信息
        st.subheader("📊 排盘信息")
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("月建", pan['yue_zhi'])
        col_info2.metric("日辰", f"{pan['ri_gan']}{pan['ri_zhi']}")
        col_info3.metric("旬空", f"{pan['kong'][0]}、{pan['kong'][1]}")

        # 六爻表
        import pandas as pd
        df_rows = []
        for i in range(6):
            df_rows.append({
                '爻位': i+1,
                '世应': pan['main']['shi_ying'][i],
                '地支': pan['main']['dizhi'][i],
                '六亲': pan['main']['liuqin'][i],
                '变地支': pan['bian']['dizhi'][i],
                '变六亲': pan['bian']['liuqin'][i],
                '六神': pan['liushen'][i]
            })
        st.table(pd.DataFrame(df_rows))

        # 多维度评分表
        st.subheader("📈 多维度评分详情（示例格式）")
        score_table = []
        for dim in ['月令提纲', '日辰决断', '世应生克', '动爻影响', '三合三会', '空亡真假', '六冲/六合', '六神取象', '合计']:
            s = scores[dim]
            score_table.append([
                dim,
                f"{s['主']} ({s['主评']})",
                f"{s['客']} ({s['客评']})",
                round(s['主'] - s['客'], 1)
            ])
        st.table(pd.DataFrame(score_table, columns=["维度", "世爻 (主队)", "应爻 (客队)", "主客差"]))

        # 最终判断
        st.subheader("🎯 综合结论")
        st.write(f"**{result}**：{reason}")
        if result == "主胜":
            st.info("主队综合评分占优，赢面较大。")
        elif result == "客胜":
            st.info("客队综合评分占优，赢面较大。")
        else:
            st.info("双方实力均衡，平局概率最高。")

    except Exception as e:
        st.error(f"发生错误：{e}")
