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
    shi_pos = [6,1,2,3,4,5,4,3]
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
    base = datetime.datetime(1,1,1)
    target = datetime.datetime(year, month, day)
    delta = (target - base).days
    ref = datetime.datetime(2000,1,1)
    ref_delta = (ref - base).days
    ref_gz = 54  # 2000-01-01 戊午 (索引54)
    return (ref_gz + (delta - ref_delta)) % 60

def month_zhi(year, month, day):
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
    start_gan = {
        '甲':'甲','乙':'丙','丙':'戊','丁':'庚','戊':'壬',
        '己':'甲','庚':'丙','辛':'戊','壬':'庚','癸':'壬'
    }
    gan = start_gan[day_gan]
    gan_idx = TIAN_GAN.index(gan)
    zhi_idx = (hour + 1) // 2 % 12
    real_gan = TIAN_GAN[(gan_idx + zhi_idx) % 10]
    real_zhi = DI_ZHI[zhi_idx]
    return real_gan + real_zhi

def get_xunkong(ri_zhi):
    xun_start = (DI_ZHI.index(ri_zhi) // 2) * 2
    if xun_start == 0: return ('戌','亥')
    elif xun_start == 2: return ('子','丑')
    elif xun_start == 4: return ('寅','卯')
    elif xun_start == 6: return ('辰','巳')
    elif xun_start == 8: return ('午','未')
    else: return ('申','酉')

def liu_shen(ri_gan):
    start = {
        '甲':'青龙','乙':'青龙','丙':'朱雀','丁':'朱雀',
        '戊':'勾陈','己':'螣蛇','庚':'白虎','辛':'白虎',
        '壬':'玄武','癸':'玄武'
    }
    order = ['青龙','朱雀','勾陈','螣蛇','白虎','玄武']
    idx = order.index(start[ri_gan])
    return order[idx:] + order[:idx]

# ====================== 排盘 ======================
def pai_pan(main_name, bian_name, year, month, day, hour):
    yue_idx = month_zhi(year, month, day)
    yue_zhi = DI_ZHI[yue_idx]
    day_gz = day_gz_index(year, month, day)
    ri_gan = TIAN_GAN[day_gz % 10]
    ri_zhi = DI_ZHI[day_gz % 12]
    shi_chen = hour_gz(ri_gan, hour)
    kong = get_xunkong(ri_zhi)
    liushen = liu_shen(ri_gan)

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

    bian = GUA_DB.get(bian_name)
    if not bian:
        raise ValueError(f"变卦{bian_name}不存在")
    b_upper_name = BAGUA[bian['upper']]
    b_lower_name = BAGUA[bian['lower']]
    bian_dz = NAJIA[b_lower_name][:3] + NAJIA[b_upper_name][:3]
    bian_gong_wx = GUA_WX[BAGUA[bian['palace']]]
    bian_lq = [get_liuqin(DZ_WX[dz], bian_gong_wx) for dz in bian_dz]

    return {
        'yue_zhi': yue_zhi,
        'ri_gan': ri_gan, 'ri_zhi': ri_zhi,
        'shi_chen': shi_chen, 'kong': kong,
        'liushen': liushen,
        'main': {
            'name': main_name,
            'dizhi': main_dz, 'liuqin': main_lq,
            'shi_ying': shi_ying, 'shi': shi, 'ying': ying,
            'chong': main['chong'], 'he': main['he'],
            'gong_wx': gong_wx
        },
        'bian': {
            'name': bian_name,
            'dizhi': bian_dz, 'liuqin': bian_lq,
            'chong': bian['chong'], 'he': bian['he']
        }
    }

# ====================== 多维度断卦引擎 ======================
def duan_gua_detail(pan, dong_yao_list):
    m = pan['main']
    b = pan['bian']
    yue_zhi = pan['yue_zhi']
    ri_zhi = pan['ri_zhi']
    kong = pan['kong']
    liushen = pan['liushen']

    shi_idx = m['shi'] - 1
    ying_idx = m['ying'] - 1
    shi_dz = m['dizhi'][shi_idx]
    ying_dz = m['dizhi'][ying_idx]
    shi_wx = DZ_WX[shi_dz]
    ying_wx = DZ_WX[ying_dz]

    # 初始化维度分数
    scores = {
        '月令提纲': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '日辰决断': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '世应生克': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '动爻影响': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '三合三会': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '空亡真假': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '六冲/六合': {'主': 0, '客': 0, '主评': '', '客评': ''},
        '六神取象': {'主': 0, '客': 0, '主评': '', '客评': ''}
    }

    # 1. 月令提纲
    yue_sk_shi = shengke(DZ_WX[yue_zhi], shi_wx)
    if yue_sk_shi == '生': scores['月令提纲']['主'] = 1; scores['月令提纲']['主评'] = '得月生'
    elif yue_sk_shi == '克': scores['月令提纲']['主'] = -1; scores['月令提纲']['主评'] = '被月克'
    elif yue_sk_shi == '比和': scores['月令提纲']['主'] = 0.5; scores['月令提纲']['主评'] = '月比和'
    else: scores['月令提纲']['主评'] = '平'

    yue_sk_ying = shengke(DZ_WX[yue_zhi], ying_wx)
    if yue_sk_ying == '生': scores['月令提纲']['客'] = 1; scores['月令提纲']['客评'] = '得月生'
    elif yue_sk_ying == '克': scores['月令提纲']['客'] = -1; scores['月令提纲']['客评'] = '被月克'
    elif yue_sk_ying == '比和': scores['月令提纲']['客'] = 0.5; scores['月令提纲']['客评'] = '月比和'
    else: scores['月令提纲']['客评'] = '平'

    # 2. 日辰决断
    ri_sk_shi = shengke(DZ_WX[ri_zhi], shi_wx)
    if ri_sk_shi == '生': scores['日辰决断']['主'] = 1; scores['日辰决断']['主评'] = '得日生'
    elif ri_sk_shi == '克': scores['日辰决断']['主'] = -1; scores['日辰决断']['主评'] = '被日克'
    elif ri_sk_shi == '比和': scores['日辰决断']['主'] = 0.5; scores['日辰决断']['主评'] = '日比和'
    else: scores['日辰决断']['主评'] = '平'

    ri_sk_ying = shengke(DZ_WX[ri_zhi], ying_wx)
    if ri_sk_ying == '生': scores['日辰决断']['客'] = 1; scores['日辰决断']['客评'] = '得日生'
    elif ri_sk_ying == '克': scores['日辰决断']['客'] = -1; scores['日辰决断']['客评'] = '被日克'
    elif ri_sk_ying == '比和': scores['日辰决断']['客'] = 0.5; scores['日辰决断']['客评'] = '日比和'
    else: scores['日辰决断']['客评'] = '平'

    # 3. 世应生克
    sk = shengke(shi_wx, ying_wx)
    if sk == '克':
        scores['世应生克']['主'] = 1.5
        scores['世应生克']['客'] = -0.5
        scores['世应生克']['主评'] = '世克应'
        scores['世应生克']['客评'] = '被克'
    elif sk == '生':
        scores['世应生克']['主'] = -1.5
        scores['世应生克']['客'] = 0.5
        scores['世应生克']['主评'] = '世生应'
        scores['世应生克']['客评'] = '受生'
    else:
        scores['世应生克']['主'] = 0
        scores['世应生克']['客'] = 0
        scores['世应生克']['主评'] = '比和'
        scores['世应生克']['客评'] = '比和'

    # 4. 动爻影响
    dong_eff_shi = 0
    dong_eff_ying = 0
    dong_notes = []
    for dong in dong_yao_list:
        idx = dong - 1
        main_dz = m['dizhi'][idx]
        main_wx = DZ_WX[main_dz]
        bian_dz = b['dizhi'][idx]
        bian_wx = DZ_WX[bian_dz]

        factor = 1.0
        note = f"动爻{main_dz}"

        # 回头生克
        htsk = shengke(bian_wx, main_wx)
        if htsk == '克':
            factor *= 0.3
            note += f"化{bian_dz}回头克"
        elif htsk == '生':
            factor *= 1.8
            note += f"化{bian_dz}回头生"
        # 化进/退神
        if main_wx == bian_wx:
            if DI_ZHI.index(bian_dz) == (DI_ZHI.index(main_dz) + 1) % 12:
                factor *= 1.5
                note += ' 化进神'
            elif DI_ZHI.index(bian_dz) == (DI_ZHI.index(main_dz) - 1) % 12:
                factor *= 0.6
                note += ' 化退神'

        dong_notes.append(note)

        # 动爻对世应的生克
        sk_shi = shengke(main_wx, shi_wx)
        sk_ying = shengke(main_wx, ying_wx)
        if sk_shi == '生': dong_eff_shi += 1.0 * factor
        elif sk_shi == '克': dong_eff_shi -= 1.5 * factor
        if sk_ying == '生': dong_eff_ying += 1.0 * factor
        elif sk_ying == '克': dong_eff_ying -= 1.5 * factor

    scores['动爻影响']['主'] = round(dong_eff_shi, 1)
    scores['动爻影响']['客'] = round(dong_eff_ying, 1)
    scores['动爻影响']['主评'] = '; '.join(dong_notes) if dong_notes else '无动爻'
    scores['动爻影响']['客评'] = ''

    # 5. 三合局检测
    sanhe_list = [('申','子','辰'), ('巳','酉','丑'), ('寅','午','戌'), ('亥','卯','未')]
    all_shi_dz = {shi_dz, ri_zhi}
    all_ying_dz = {ying_dz, ri_zhi}
    for dong in dong_yao_list:
        all_shi_dz.add(m['dizhi'][dong-1])
        all_ying_dz.add(m['dizhi'][dong-1])
    shi_has_he = False; ying_has_he = False
    for h in sanhe_list:
        if set(h).issubset(all_shi_dz):
            scores['三合三会']['主'] = 3
            scores['三合三会']['主评'] = f'三合{"/".join(h)}局成'
            shi_has_he = True
            break
    if not shi_has_he:
        scores['三合三会']['主评'] = '无'
    for h in sanhe_list:
        if set(h).issubset(all_ying_dz):
            scores['三合三会']['客'] = 3
            scores['三合三会']['客评'] = f'三合{"/".join(h)}局成'
            ying_has_he = True
            break
    if not ying_has_he:
        scores['三合三会']['客评'] = '无'

    # 6. 空亡
    if shi_dz in kong:
        scores['空亡真假']['主'] = -2
        scores['空亡真假']['主评'] = '世爻旬空'
    else:
        scores['空亡真假']['主评'] = '不空'
    if ying_dz in kong:
        scores['空亡真假']['客'] = -2
        scores['空亡真假']['客评'] = '应爻旬空'
    else:
        scores['空亡真假']['客评'] = '不空'

    # 7. 六神取象（仅参考）
    scores['六神取象']['主评'] = f'{liushen[shi_idx]}临世'
    scores['六神取象']['客评'] = f'{liushen[ying_idx]}临应'

    # 8. 计算初步合计（不含六冲/六合修正）
    total_shi = (scores['月令提纲']['主'] + scores['日辰决断']['主'] +
                 scores['世应生克']['主'] + scores['动爻影响']['主'] +
                 scores['三合三会']['主'] + scores['空亡真假']['主'])
    total_ying = (scores['月令提纲']['客'] + scores['日辰决断']['客'] +
                  scores['世应生克']['客'] + scores['动爻影响']['客'] +
                  scores['三合三会']['客'] + scores['空亡真假']['客'])

    # 六冲/六合修正
    chong = m['chong'] or b['chong']
    he = m['he'] or b['he']
    if he:
        avg = (total_shi + total_ying) / 2
        diff = avg - total_shi
        scores['六冲/六合']['主'] = round(diff, 1)
        scores['六冲/六合']['客'] = round(avg - total_ying, 1)
        scores['六冲/六合']['主评'] = '六合拉平'
        scores['六冲/六合']['客评'] = '六合拉平'
        total_shi = avg
        total_ying = avg
    elif chong:
        if total_shi > total_ying:
            bonus = 1
            scores['六冲/六合']['主'] = bonus
            scores['六冲/六合']['客'] = -0.5
            scores['六冲/六合']['主评'] = '六冲扩大优势'
            scores['六冲/六合']['客评'] = '六冲劣势'
            total_shi += bonus
            total_ying -= 0.5
        elif total_ying > total_shi:
            bonus = 1
            scores['六冲/六合']['客'] = bonus
            scores['六冲/六合']['主'] = -0.5
            scores['六冲/六合']['客评'] = '六冲扩大优势'
            scores['六冲/六合']['主评'] = '六冲劣势'
            total_ying += bonus
            total_shi -= 0.5
        else:
            scores['六冲/六合']['主评'] = '六冲均势'
            scores['六冲/六合']['客评'] = '六冲均势'
    else:
        scores['六冲/六合']['主评'] = '无'
        scores['六冲/六合']['客评'] = '无'

    # 最终总分
    final_shi = round(total_shi, 1)
    final_ying = round(total_ying, 1)

    # 判定结果
    diff = final_shi - final_ying
    if diff > 1.0:
        result = "主胜"
        reason = "主队综合优势明显"
    elif diff < -1.0:
        result = "客胜"
        reason = "客队综合优势明显"
    else:
        result = "平局"
        reason = "双方实力接近，平局概率最高"

    # 组装返回
    dimension_table = []
    dim_names = ['月令提纲', '日辰决断', '世应生克', '动爻影响', '三合三会', '空亡真假', '六冲/六合', '六神取象']
    for dim in dim_names:
        s = scores[dim]
        dimension_table.append({
            '维度': dim,
            '世爻 (主队)': f"{s['主']} ({s['主评']})",
            '应爻 (客队)': f"{s['客']} ({s['客评']})",
            '主客差': round(s['主'] - s['客'], 1)
        })
    # 添加合计行
    dimension_table.append({
        '维度': '合计',
        '世爻 (主队)': str(final_shi),
        '应爻 (客队)': str(final_ying),
        '主客差': round(final_shi - final_ying, 1)
    })

    return dimension_table, result, reason, pan

# ====================== UI 界面 ======================
with st.form("predict_form"):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        main_gua = st.text_input("主卦名", "天水讼", help="例如：天水讼")
        bian_gua = st.text_input("变卦名", "天泽履", help="例如：天泽履")
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
        dong_list = []
        if dong_yao_str.strip():
            dong_list = [int(x.strip()) for x in dong_yao_str.split(',') if x.strip()]
            if any(d < 1 or d > 6 for d in dong_list):
                st.error("动爻编号须在1-6之间")
                st.stop()

        pan = pai_pan(main_gua.strip(), bian_gua.strip(), year, month, day, hour)
        dimension_table, result, reason, pan = duan_gua_detail(pan, dong_list)

        # 显示结果
        st.success(f"### 预测结果：{result} ({reason})")

        # 排盘信息
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("月建", pan['yue_zhi'])
        col_info2.metric("日辰", f"{pan['ri_gan']}{pan['ri_zhi']}")
        col_info3.metric("旬空", f"{pan['kong'][0]}、{pan['kong'][1]}")

        # 六爻表格
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
        st.subheader("📈 多维度评分详情")
        st.table(pd.DataFrame(dimension_table))

    except Exception as e:
        st.error(f"发生错误：{e}")
