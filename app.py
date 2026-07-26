import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="⚽六爻足球预测", layout="wide")
st.title("六爻足球胜平负预测系统")
st.markdown("野鹤派六爻量化打分模型，无第三方农历依赖，云端直接运行")

# =====================基础常量=====================
TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
DZ_WX = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE    = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
MU_KU = {'木':'未','火':'戌','金':'丑','土':'辰','水':'辰'}

BAGUA = {1:'乾',2:'兑',3:'离',4:'震',5:'巽',6:'坎',7:'艮',8:'坤'}
SYM2NUM = {'天':1,'泽':2,'火':3,'雷':4,'风':5,'水':6,'山':7,'地':8}
GUA_WX = {'乾':'金','兑':'金','震':'木','巽':'木','坎':'水','离':'火','艮':'土','坤':'土'}
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

# =====================64卦库=====================
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
    youhun_idx = [5,5,5,5,5,5,5,5]
    guihun_idx = [7,7,7,7,7,7,7,7]
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
            if ying > 6: ying -= 6
            is_youhun = (idx == youhun_idx[pal-1])
            is_guihun = (idx == guihun_idx[pal-1])
            chong_gua = ['乾为天','兑为泽','离为火','震为雷','巽为风','坎为水','艮为山','坤为地']
            he_gua = ['地天泰','天地否','泽山咸','雷风恒','水泽节','火山旅','山泽损','泽地萃']
            GUA_DB[name] = {
                'upper': upper_num, 'lower': lower_num,
                'palace': pal,
                'shi': shi, 'ying': ying,
                'chong': name in chong_gua,
                'he': name in he_gua,
                'youhun': is_youhun,
                'guihun': is_guihun
            }
_init_db()

# =====================通用工具函数=====================
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

# =====================【重点】内置节气换算 替代lunardate=====================
# 二十四节气交接日近似表(公历年区间2000~2050适用)，推算月令
def get_month_zhi_by_solar(year, month, day):
    # 节气对应地支：寅月立春~卯月惊蛰...
    # 寅=1,卯=2,辰=3,巳=4,午=5,未=6,申=7,酉=8,戌=9,亥=10,子=11,丑=0
    jieqi_dates = [
        ("立春",2,4,1), ("惊蛰",3,6,2), ("清明",4,5,3), ("立夏",5,6,4),
        ("芒种",6,6,5), ("小暑",7,7,6), ("立秋",8,8,7), ("白露",9,8,8),
        ("寒露",10,9,9), ("立冬",11,8,10), ("大雪",12,7,11), ("小寒",1,6,0)
    ]
    current_dt = datetime.date(year,month,day)
    zhi_idx = None
    for jq_name,m,d,idx in jieqi_dates:
        jq_year = year
        if m == 1:
            jq_year = year+1
        jq_dt = datetime.date(jq_year, m, d)
        if current_dt >= jq_dt:
            zhi_idx = idx
    if zhi_idx is None:
        zhi_idx = 0
    return DI_ZHI[zhi_idx]

# 日干支简易推算
def day_gz_index(year, month, day):
    base = datetime.date(2000,1,1)
    target = datetime.date(year,month,day)
    delta = (target - base).days
    base_gz = 54
    return (base_gz + delta) % 60

# 时干支
def hour_gz(ri_gan, hour):
    start_map = {
        '甲':'甲','乙':'丙','丙':'戊','丁':'庚','戊':'壬',
        '己':'甲','庚':'丙','辛':'戊','壬':'庚','癸':'壬'
    }
    gan_start = start_map[ri_gan]
    gan_idx = TIAN_GAN.index(gan_start)
    zhi_idx = (hour + 1)//2 % 12
    real_gan = TIAN_GAN[(gan_idx + zhi_idx) % 10]
    real_zhi = DI_ZHI[zhi_idx]
    return real_gan + real_zhi

# 旬空计算
def get_xunkong(ri_gan, ri_zhi):
    g_idx = TIAN_GAN.index(ri_gan)
    z_idx = DI_ZHI.index(ri_zhi)
    xun_head = (z_idx - g_idx) % 12
    k1 = DI_ZHI[(xun_head - 2) %12]
    k2 = DI_ZHI[(xun_head -1) %12]
    return (k1,k2)

# 六神排序
def liu_shen(ri_gan):
    start_map = {
        '甲':'青龙','乙':'青龙','丙':'朱雀','丁':'朱雀',
        '戊':'勾陈','己':'螣蛇','庚':'白虎','辛':'白虎',
        '壬':'玄武','癸':'玄武'
    }
    order = ['青龙','朱雀','勾陈','螣蛇','白虎','玄武']
    start = start_map[ri_gan]
    pos = order.index(start)
    return order[pos:] + order[:pos]

# =====================排盘函数=====================
def pai_pan(main_name, bian_name, year, month, day, hour):
    yue_zhi = get_month_zhi_by_solar(year, month, day)
    day_gz = day_gz_index(year, month, day)
    ri_gan = TIAN_GAN[day_gz % 10]
    ri_zhi = DI_ZHI[day_gz % 12]
    shi_chen = hour_gz(ri_gan, hour)
    kong = get_xunkong(ri_gan, ri_zhi)
    liushen = liu_shen(ri_gan)

    main = GUA_DB.get(main_name)
    if not main: raise ValueError(f"主卦【{main_name}】不存在，请核对名称！")
    gong_name = BAGUA[main['palace']]
    gong_wx = GUA_WX[gong_name]
    upper_name = BAGUA[main['upper']]
    lower_name = BAGUA[main['lower']]
    main_dz = NAJIA[lower_name][:3] + NAJIA[upper_name][:3]
    main_lq = [get_liuqin(DZ_WX[dz], gong_wx) for dz in main_dz]
    shi_ying = ['']*6
    shi_ying[main['shi']-1] = '世'
    shi_ying[main['ying']-1] = '应'

    bian = GUA_DB.get(bian_name)
    if not bian: raise ValueError(f"变卦【{bian_name}】不存在，请核对名称！")
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
            'name': main_name, 'dizhi': main_dz, 'liuqin': main_lq,
            'shi_ying': shi_ying, 'shi': main['shi'], 'ying': main['ying'],
            'chong': main['chong'], 'he': main['he'], 'gong_wx': gong_wx,
            'youhun': main['youhun'], 'guihun': main['guihun']
        },
        'bian': {
            'name': bian_name, 'dizhi': bian_dz, 'liuqin': bian_lq,
            'chong': bian['chong'], 'he': bian['he']
        }
    }

# =====================量化打分引擎（完全保留原有28法逻辑不变）=====================
def calc_scores(pan, dong_list):
    main = pan['main']
    bian = pan['bian']
    yue_zhi = pan['yue_zhi']
    ri_zhi = pan['ri_zhi']
    kong = pan['kong']

    shi_idx = main['shi'] - 1
    ying_idx = main['ying'] - 1
    shi_dz = main['dizhi'][shi_idx]
    ying_dz = main['dizhi'][ying_idx]
    shi_wx = DZ_WX[shi_dz]
    ying_wx = DZ_WX[ying_dz]
    shi_lq = main['liuqin'][shi_idx]
    ying_lq = main['liuqin'][ying_idx]

    dims = {
        '月建旺衰': {'主':0,'客':0,'主评':'','客评':''},
        '日辰作用': {'主':0,'客':0,'主评':'','客评':''},
        '三合局能量': {'主':0,'客':0,'主评':'','客评':''},
        '世应生克': {'主':0,'客':0,'主评':'','客评':''},
        '动爻影响': {'主':0,'客':0,'主评':'','客评':''},
    }
    extra = {'六神格局': {'主':0,'客':0,'主评':'','客评':''}}

    def yue_score(dz):
        wx = DZ_WX[dz]
        yue_dz = yue_zhi
        if dz == yue_dz:
            return (2, '临月建')
        if DI_ZHI.index(dz) == (DI_ZHI.index(yue_dz) + 6) % 12:
            return (-2, '月破')
        sk = shengke(DZ_WX[yue_dz], wx)
        if sk == '生':
            return (1, '得月生')
        if sk == '克':
            return (-1, '被月克')
        if sk == '比和':
            if yue_dz in ['辰','戌','丑','未']:
                return (0.5, '余气有根')
            else:
                return (1, '月令比和相助')
        return (-1, '休囚无力')

    s, note = yue_score(shi_dz)
    dims['月建旺衰']['主'] = s; dims['月建旺衰']['主评'] = note
    s, note = yue_score(ying_dz)
    dims['月建旺衰']['客'] = s; dims['月建旺衰']['客评'] = note

    def ri_score(dz, wx, yue_power):
        if dz == ri_zhi:
            return (2, '临日辰')
        he_pairs = [('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')]
        if (dz, ri_zhi) in he_pairs or (ri_zhi, dz) in he_pairs:
            return (2, '日合起旺')
        if DI_ZHI.index(dz) == (DI_ZHI.index(ri_zhi) + 6) % 12:
            if yue_power >= 0:
                return (1, '旺相暗动')
            else:
                return (-2, '衰弱日破')
        sk = shengke(DZ_WX[ri_zhi], wx)
        if sk == '生': return (1, '得日生')
        if sk == '克': return (-1, '受日克')
        if MU_KU.get(wx) == ri_zhi:
            return (-1, '入墓受困')
        return (0, '日辰平相')

    shi_yue_score,_ = yue_score(shi_dz)
    ying_yue_score,_ = yue_score(ying_dz)
    s, note = ri_score(shi_dz, shi_wx, shi_yue_score)
    dims['日辰作用']['主'] = s; dims['日辰作用']['主评'] = note
    s, note = ri_score(ying_dz, ying_wx, ying_yue_score)
    dims['日辰作用']['客'] = s; dims['日辰作用']['客评'] = note

    sanhe = [('申','子','辰'), ('巳','酉','丑'), ('寅','午','戌'), ('亥','卯','未')]
    dong_dzs = [main['dizhi'][d-1] for d in dong_list]
    has_dong = len(dong_list) > 0
    shi_sanhe = False; ying_sanhe = False
    shi_zhongshen = False; ying_zhongshen = False

    all_dzs = main['dizhi'] + [ri_zhi] + dong_dzs
    for he in sanhe:
        if set(he).issubset(set(all_dzs)) and has_dong:
            if shi_dz in he:
                shi_sanhe = True
                if shi_dz == he[1]: shi_zhongshen = True
            if ying_dz in he:
                ying_sanhe = True
                if ying_dz == he[1]: ying_zhongshen = True

    if shi_sanhe:
        if shi_zhongshen:
            dims['三合局能量']['主'] = 3
            dims['三合局能量']['主评'] = '三合局中神+3'
        else:
            dims['三合局能量']['主'] = 1.5
            dims['三合局能量']['主评'] = '三合局辅神+1.5'
    else:
        dims['三合局能量']['主评'] = '无有效三合'

    if ying_sanhe:
        if ying_zhongshen:
            dims['三合局能量']['客'] = 3
            dims['三合局能量']['客评'] = '三合局中神+3'
        else:
            dims['三合局能量']['客'] = 1.5
            dims['三合局能量']['客评'] = '三合局辅神+1.5'
    else:
        dims['三合局能量']['客评'] = '无有效三合'

    sk = shengke(shi_wx, ying_wx)
    if sk == '克':
        dims['世应生克']['主'] = 0.5; dims['世应生克']['客'] = -0.5
        dims['世应生克']['主评'] = '世克应'; dims['世应生克']['客评'] = '被克'
    elif sk == '生':
        dims['世应生克']['主'] = -0.5; dims['世应生克']['客'] = 0.5
        dims['世应生克']['主评'] = '世生应'; dims['世应生克']['客评'] = '受生'
    else:
        dims['世应生克']['主评'] = '比和'; dims['世应生克']['客评'] = '比和'

    dong_shi_eff = 0.0
    dong_ying_eff = 0.0
    dong_notes = []
    for dong_wei in dong_list:
        idx = dong_wei - 1
        mdz = main['dizhi'][idx]
        mwx = DZ_WX[mdz]
        bdz = bian['dizhi'][idx]
        bwx = DZ_WX[bdz]
        note = f"动爻{dong_wei}({mdz})"

        if dong_wei == main['shi']:
            dong_shi_eff += 1.0
            note += " 世动+1"
        if dong_wei == main['ying']:
            dong_ying_eff += 1.0
            note += " 应动+1"

        hsk = shengke(bwx, mwx)
        if hsk == '生':
            if dong_wei == main['shi']: dong_shi_eff +=0.5; note+=" 回头生+0.5"
            if dong_wei == main['ying']: dong_ying_eff +=0.5; note+=" 回头生+0.5"
        elif hsk == '克':
            if dong_wei == main['shi']: dong_shi_eff -=0.5; note+=" 回头克-0.5"
            if dong_wei == main['ying']: dong_ying_eff -=0.5; note+=" 回头克-0.5"
        elif SHENG[mwx]==bwx:
            if dong_wei == main['shi']: dong_shi_eff -=0.5; note+=" 化泄-0.5"
            if dong_wei == main['ying']: dong_ying_eff -=0.5; note+=" 化泄-0.5"

        skshi = shengke(mwx, shi_wx)
        skying = shengke(mwx, ying_wx)
        if skshi == '生': dong_shi_eff +=0.5; note += " 生世+0.5"
        if skshi == '克': dong_shi_eff -=0.5; note += " 克世-0.5"
        if skying == '生': dong_ying_eff +=0.5; note += " 生应+0.5"
        if skying == '克': dong_ying_eff -=0.5; note += " 克应-0.5"
        dong_notes.append(note)

    dims['动爻影响']['主'] = round(dong_shi_eff, 1)
    dims['动爻影响']['客'] = round(dong_ying_eff, 1)
    dims['动爻影响']['主评'] = ' | '.join(dong_notes) if dong_notes else '无动爻'

    extra['六神格局']['主评'] = f"{pan['liushen'][shi_idx]}临世"
    extra['六神格局']['客评'] = f"{pan['liushen'][ying_idx]}临应"

    total_shi = round(sum(dims[d]['主'] for d in dims), 2)
    total_ying = round(sum(dims[d]['客'] for d in dims), 2)
    diff = round(total_shi - total_ying, 2)

    chong = main['chong'] or bian['chong']
    he = main['he'] or bian['he']
    youhun = main['youhun']
    guihun = main['guihun']
    chong_he_note = ""
    if chong: chong_he_note += "六冲，易分胜负。"
    if he: chong_he_note += "六合，容易僵持平局。"
    if youhun: chong_he_note += "游魂，局势多变。"
    if guihun: chong_he_note += "归魂，容易守和。"

    liuqin_note = ''
    if shi_lq == '兄弟':
        liuqin_note = '⚠️世爻临兄弟，竞争互相消耗，优先防范平局。'

    if diff > 3:
        result = "主胜"
        reason = f"主队总分{total_shi}，客队{total_ying}，分差{diff:.2f}＞3，主队优势明显。"
    elif diff > 1:
        result = "主队不败，防平局"
        reason = f"主队总分{total_shi}，客队{total_ying}，分差{diff:.2f}（1~3区间），优势方防平。"
    elif diff < -3:
        result = "客胜"
        reason = f"客队总分{total_ying}，主队{total_shi}，分差{diff:.2f}＜-3，客队优势明显。"
    elif diff < -1:
        result = "客队不败，防平局"
        reason = f"客队总分{total_ying}，主队{total_shi}，分差{diff:.2f}（-3~-1区间），优势方防平。"
    else:
        result = "平局优先"
        reason = f"双方分数接近，主{total_shi} 客{total_ying}，分差{diff:.2f}＜1，势均力敌。"

    full_reason = reason + chong_he_note + liuqin_note
    return dims, extra, total_shi, total_ying, diff, result, full_reason

# =====================页面UI=====================
with st.form("predict_form"):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        main_gua = st.text_input("主卦名", "天雷无妄", help="例如：天雷无妄、火地晋")
        bian_gua = st.text_input("变卦名", "天地否", help="例如：天地否")
    with col2:
        dong_yao_str = st.text_input("动爻 (逗号分隔)", "1", help="多个动爻：1,3；无动爻留空")
    with col3:
        year = st.number_input("年", 2026, 2000, 2050, 1)
        month = st.number_input("月", 7, 1, 12, 1)
        day = st.number_input("日", 24, 1, 31, 1)
        hour = st.number_input("时辰(0-23)", 18, 0, 23, 1)

    submitted = st.form_submit_button("⚡ 开始预测计算")

if submitted:
    try:
        main_gua = main_gua.strip()
        bian_gua = bian_gua.strip()
        dong_list = []
        if dong_yao_str.strip():
            dong_list = [int(x.strip()) for x in dong_yao_str.split(',') if x.strip()]
            if any(not (1 <= d <=6) for d in dong_list):
                st.error("动爻范围只能是1~6！")
                st.stop()

        pan = pai_pan(main_gua, bian_gua, year, month, day, hour)
        dims, extra, total_shi, total_ying, diff, result, reason = calc_scores(pan, dong_list)

        st.success(f"## 预测结论：{result}")
        st.info(reason)

        colA, colB, colC = st.columns(3)
        colA.metric("月建", pan['yue_zhi'])
        colB.metric("日辰", f"{pan['ri_gan']}{pan['ri_zhi']}")
        colC.metric("旬空", f"{pan['kong'][0]}、{pan['kong'][1]}")

        rows = []
        for i in range(6):
            rows.append({
                '爻位': i+1,
                '世应': pan['main']['shi_ying'][i],
                '地支': pan['main']['dizhi'][i],
                '六亲': pan['main']['liuqin'][i],
                '变爻地支': pan['bian']['dizhi'][i],
                '变六亲': pan['bian']['liuqin'][i],
                '六神': pan['liushen'][i]
            })
        st.subheader("完整卦盘")
        st.table(pd.DataFrame(rows))

        st.subheader("📊 五维量化评分明细")
        score_rows = []
        for dim_name, s in dims.items():
            score_rows.append({
                '维度': dim_name,
                '世爻(主队)': f"{s['主']}｜{s['主评']}",
                '应爻(客队)': f"{s['客']}｜{s['客评']}",
                '单项差值': round(s['主'] - s['客'],2)
            })
        score_rows.append({
            '维度': '六神格局（仅参考不计分）',
            '世爻(主队)': extra['六神格局']['主评'],
            '应爻(客队)': extra['六神格局']['客评'],
            '单项差值': "-"
        })
        score_rows.append({
            '维度': '总分合计',
            '世爻(主队)': total_shi,
            '应爻(客队)': total_ying,
            '单项差值': diff
        })
        st.table(pd.DataFrame(score_rows))

    except Exception as e:
        st.error(f"运行异常：{str(e)}")
