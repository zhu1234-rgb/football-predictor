#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
六爻足球赛事胜平负预测工具（命令行版）
用法：运行后按提示输入比赛时间、主卦、变卦、动爻
输出：世应信息、预测结果（主胜/平局/客胜）及理由
"""

import datetime
import re

# ---------- 基础数据 ----------
TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

BAGUA = {1:'乾', 2:'兑', 3:'离', 4:'震', 5:'巽', 6:'坎', 7:'艮', 8:'坤'}

BAGUA_WUXING = {
    '乾':'金', '兑':'金',
    '震':'木', '巽':'木',
    '坎':'水',
    '离':'火',
    '艮':'土', '坤':'土'
}

# 纳甲地支（初爻到上爻）
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

# 六十四卦世应表 (上卦序号,下卦序号) -> (卦名, 宫序号, 世爻位, 应爻位)
GUA_DATA = {
    (1,1): ('乾', 1, 6, 3),
    (1,2): ('夬', 1, 5, 2),
    (1,3): ('大有', 1, 3, 6),
    (1,4): ('大壮', 1, 4, 1),
    (1,5): ('小畜', 1, 4, 1),
    (1,6): ('需', 1, 4, 1),
    (1,7): ('大畜', 1, 2, 5),
    (1,8): ('泰', 1, 3, 6),
    (2,1): ('履', 2, 5, 2),
    (2,2): ('兑', 2, 6, 3),
    (2,3): ('革', 2, 4, 1),
    (2,4): ('随', 2, 3, 6),
    (2,5): ('大过', 2, 3, 6),
    (2,6): ('困', 2, 2, 5),
    (2,7): ('咸', 2, 4, 1),
    (2,8): ('萃', 2, 4, 1),
    (3,1): ('同人', 3, 4, 1),
    (3,2): ('临', 3, 2, 5),
    (3,3): ('离', 3, 6, 3),
    (3,4): ('噬嗑', 3, 5, 2),
    (3,5): ('鼎', 3, 3, 6),
    (3,6): ('未济', 3, 4, 1),
    (3,7): ('旅', 3, 3, 6),
    (3,8): ('晋', 3, 4, 1),
    (4,1): ('无妄', 4, 4, 1),
    (4,2): ('中孚', 4, 2, 5),
    (4,3): ('家人', 4, 3, 6),
    (4,4): ('震', 4, 6, 3),
    (4,5): ('益', 4, 4, 1),
    (4,6): ('屯', 4, 2, 5),
    (4,7): ('颐', 4, 3, 6),
    (4,8): ('复', 4, 1, 4),
    (5,1): ('姤', 5, 1, 4),
    (5,2): ('大过', 5, 3, 6),   # 重复名，但宫不同
    (5,3): ('鼎', 5, 3, 6),    # 重复名
    (5,4): ('恒', 5, 4, 1),
    (5,5): ('巽', 5, 6, 3),
    (5,6): ('井', 5, 5, 2),
    (5,7): ('蛊', 5, 3, 6),
    (5,8): ('升', 5, 4, 1),
    (6,1): ('讼', 6, 4, 1),
    (6,2): ('困', 6, 2, 5),
    (6,3): ('未济', 6, 4, 1),
    (6,4): ('解', 6, 2, 5),
    (6,5): ('涣', 6, 3, 6),
    (6,6): ('坎', 6, 6, 3),
    (6,7): ('蒙', 6, 2, 5),
    (6,8): ('师', 6, 3, 6),
    (7,1): ('遁', 7, 2, 5),
    (7,2): ('咸', 7, 4, 1),
    (7,3): ('旅', 7, 3, 6),
    (7,4): ('小过', 7, 4, 1),
    (7,5): ('渐', 7, 3, 6),
    (7,6): ('蹇', 7, 4, 1),
    (7,7): ('艮', 7, 6, 3),
    (7,8): ('谦', 7, 5, 2),
    (8,1): ('否', 8, 3, 6),
    (8,2): ('萃', 8, 4, 1),
    (8,3): ('晋', 8, 4, 1),
    (8,4): ('豫', 8, 2, 5),
    (8,5): ('观', 8, 4, 1),
    (8,6): ('比', 8, 3, 6),
    (8,7): ('剥', 8, 5, 2),
    (8,8): ('坤', 8, 6, 3)
}

LIU_CHONG = {'乾','兑','离','震','巽','坎','艮','坤'}   # 八纯卦
LIU_HE = {'泰','否','咸','恒','节','旅','损','萃'}     # 常用六合卦

# ---------- 辅助函数 ----------
def wuxing_of_dizhi(dz):
    """地支五行"""
    map_ = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
            '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
    return map_[dz]

def sheng_ke(wx1, wx2):
    """
    判断五行生克 (wx1 对 wx2)
    返回: '生' | '克' | '比和' | '无关'
    """
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
    """根据爻五行和宫位五行确定六亲"""
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

# ---------- 干支计算 ----------
def get_yue_zhi(year, month, day):
    """
    粗略按节气确定月建地支序号 (0=子, 1=丑, ...)
    """
    # 节气日期近似
    if (month == 1 and day >= 6) or (month == 2 and day < 4):
        return 1   # 丑
    elif (month == 2 and day >= 4) or (month == 3 and day < 6):
        return 2   # 寅
    elif (month == 3 and day >= 6) or (month == 4 and day < 5):
        return 3   # 卯
    elif (month == 4 and day >= 5) or (month == 5 and day < 6):
        return 4   # 辰
    elif (month == 5 and day >= 6) or (month == 6 and day < 6):
        return 5   # 巳
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        return 6   # 午
    elif (month == 7 and day >= 7) or (month == 8 and day < 8):
        return 7   # 未
    elif (month == 8 and day >= 8) or (month == 9 and day < 8):
        return 8   # 申
    elif (month == 9 and day >= 8) or (month == 10 and day < 8):
        return 9   # 酉
    elif (month == 10 and day >= 8) or (month == 11 and day < 7):
        return 10  # 戌
    elif (month == 11 and day >= 7) or (month == 12 and day < 7):
        return 11  # 亥
    else:
        return 0   # 子

def get_day_gz_index(year, month, day):
    """
    计算日柱序号 (0~59)
    基准: 2000-01-01 为甲午日 (序号30)
    """
    start = datetime.datetime(1,1,1)
    target = datetime.datetime(year, month, day)
    delta = (target - start).days
    days2000 = (datetime.datetime(2000,1,1) - start).days
    offset = (30 - days2000 % 60) % 60
    idx = (delta + offset) % 60
    return idx

# ---------- 排盘核心 ----------
def pai_pan(shang, xia, bian_shang, bian_xia):
    """
    返回 (main_info, bian_info)
    main_info: {name, gong_wuxing, shi_wei, ying_wei, dizhi, liuqin, shi_ying}
    bian_info: {name, dizhi, liuqin}
    """
    # 主卦
    gua_name, gong_idx, shi_wei, ying_wei = GUA_DATA[(shang, xia)]
    gong_wuxing = BAGUA_WUXING[BAGUA[gong_idx]]
    shang_name = BAGUA[shang]
    xia_name = BAGUA[xia]
    # 六爻地支
    dizhi = NAJIA_DIZHI[xia_name][0:3] + NAJIA_DIZHI[shang_name][0:3]
    # 六亲
    liuqin = [get_liuqin(wuxing_of_dizhi(dz), gong_wuxing) for dz in dizhi]
    shi_ying = [''] * 6
    shi_ying[shi_wei-1] = '世'
    shi_ying[ying_wei-1] = '应'

    main_info = {
        'name': gua_name,
        'gong_wuxing': gong_wuxing,
        'shi_wei': shi_wei,
        'ying_wei': ying_wei,
        'dizhi': dizhi,
        'liuqin': liuqin,
        'shi_ying': shi_ying
    }

    # 变卦
    bian_name, bian_gong_idx, _, _ = GUA_DATA[(bian_shang, bian_xia)]
    bian_gong_wuxing = BAGUA_WUXING[BAGUA[bian_gong_idx]]
    bian_shang_name = BAGUA[bian_shang]
    bian_xia_name = BAGUA[bian_xia]
    bian_dizhi = NAJIA_DIZHI[bian_xia_name][0:3] + NAJIA_DIZHI[bian_shang_name][0:3]
    bian_liuqin = [get_liuqin(wuxing_of_dizhi(dz), bian_gong_wuxing) for dz in bian_dizhi]

    bian_info = {
        'name': bian_name,
        'dizhi': bian_dizhi,
        'liuqin': bian_liuqin
    }
    return main_info, bian_info

# ---------- 断卦函数 ----------
def duan_gua(main_info, bian_info, dong_yao_list, yue_zhi, ri_zhi):
    """
    评分法预测胜平负
    yue_zhi, ri_zhi 为地支字符，如'未','酉'
    """
    shi_idx = main_info['shi_wei'] - 1
    ying_idx = main_info['ying_wei'] - 1
    shi_dz = main_info['dizhi'][shi_idx]
    ying_dz = main_info['dizhi'][ying_idx]
    shi_liuqin = main_info['liuqin'][shi_idx]
    ying_liuqin = main_info['liuqin'][ying_idx]

    def score_wang(dz, yue, ri):
        s = 0
        # 月建生克
        sk = sheng_ke(wuxing_of_dizhi(yue), wuxing_of_dizhi(dz))
        if sk == '生':
            s += 1
        elif sk == '克':
            s -= 1
        # 日辰生克
        sk2 = sheng_ke(wuxing_of_dizhi(ri), wuxing_of_dizhi(dz))
        if sk2 == '生':
            s += 1
        elif sk2 == '克':
            s -= 1
        # 临日建加力
        if dz == ri:
            s += 1
        return s

    shi_score = score_wang(shi_dz, yue_zhi, ri_zhi)
    ying_score = score_wang(ying_dz, yue_zhi, ri_zhi)

    # 世应生克 (世对应)
    sk_shi_ying = sheng_ke(wuxing_of_dizhi(shi_dz), wuxing_of_dizhi(ying_dz))
    if sk_shi_ying == '克':
        shi_score += 1
        ying_score -= 1
    elif sk_shi_ying == '生':
        shi_score -= 1
        ying_score += 1
    # 比和则平局倾向，暂不加减

    # 动爻影响
    for dong in dong_yao_list:
        idx = dong - 1
        main_dz = main_info['dizhi'][idx]
        bian_dz = bian_info['dizhi'][idx]
        # 动爻对世应的生克
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
        # 变爻回头生克 (对动爻本身，间接影响世应，简化处理)
        sk_bian = sheng_ke(wuxing_of_dizhi(bian_dz), wuxing_of_dizhi(main_dz))
        if sk_bian == '生':
            # 加强动爻力量
            pass
        elif sk_bian == '克':
            # 削弱动爻力量
            pass

    # 六冲六合格局
    main_name = main_info['name']
    bian_name = bian_info['name']
    is_chong = (main_name in LIU_CHONG) or (bian_name in LIU_CHONG)
    is_he = (main_name in LIU_HE) or (bian_name in LIU_HE)

    if is_chong:
        # 冲则分胜负，拉大差距
        if shi_score > ying_score:
            shi_score += 1
        elif ying_score > shi_score:
            ying_score += 1
    if is_he:
        # 合则平局倾向，双方加分
        shi_score += 0.5
        ying_score += 0.5

    # 决策
    diff = shi_score - ying_score
    if diff > 0.8:
        result = "主胜"
        reason = f"世爻{shi_dz}（{shi_liuqin}）综合评分 {shi_score:.1f} 明显高于应爻{ying_dz}（{ying_liuqin}）评分 {ying_score:.1f}，"
        if sk_shi_ying == '克':
            reason += "世爻克应爻，主动压制。"
        elif sk_shi_ying == '生':
            reason += "世爻生应爻但自身更强，仍可控制局面。"
        else:
            reason += "双方比和但世爻更旺。"
        if is_chong:
            reason += "卦逢六冲，分胜负格局。"
    elif diff < -0.8:
        result = "客胜"
        reason = f"应爻{ying_dz}（{ying_liuqin}）综合评分 {ying_score:.1f} 明显高于世爻{shi_dz}（{shi_liuqin}）评分 {shi_score:.1f}，"
        if sk_shi_ying == '生':
            reason += "应爻生世爻但自身更旺，客队反客为主。"
        elif sk_shi_ying == '克':
            reason += "应爻克世爻，客队压制主队。"
        else:
            reason += "双方比和但应爻更旺。"
        if is_chong:
            reason += "卦逢六冲，客队胜出。"
    else:
        result = "平局"
        reason = f"世应评分接近（主{shi_score:.1f} vs 客{ying_score:.1f}），实力均衡，"
        if is_he:
            reason += "卦逢六合，僵持拉锯。"
        else:
            reason += "难分高下。"

    # 附加动爻信息
    if dong_yao_list:
        reason += f" 动爻：{', '.join(str(x) for x in dong_yao_list)}。"
    else:
        reason += " 六爻安静，维持现状。"

    return result, reason

# ---------- 主程序 ----------
def main():
    print("="*50)
    print("六爻足球赛事胜平负预测")
    print("八卦代号：1乾 2兑 3离 4震 5巽 6坎 7艮 8坤")
    print("="*50)
    try:
        # 输入主卦
        shang = int(input("主卦 上卦（1-8）："))
        xia = int(input("主卦 下卦（1-8）："))
        # 输入变卦
        bian_shang = int(input("变卦 上卦（1-8）："))
        bian_xia = int(input("变卦 下卦（1-8）："))
        # 动爻
        dong_input = input("动爻（如 1,3,5 表示初、三、五爻动，无动则直接回车）：")
        dong_yao_list = []
        if dong_input.strip():
            dong_yao_list = [int(x.strip()) for x in dong_input.split(',') if x.strip()]
            for d in dong_yao_list:
                if d < 1 or d > 6:
                    raise ValueError("动爻编号必须在1~6之间")
        # 时间
        year = int(input("比赛年份（如2026）："))
        month = int(input("比赛月份（1-12）："))
        day = int(input("比赛日期（1-31）："))
        hour = int(input("比赛时间（24小时制，小时如14）："))
        if not (0 <= hour < 24):
            raise ValueError("小时应在0~23之间")

        # 计算月建、日辰
        yue_idx = get_yue_zhi(year, month, day)
        yue_zhi = DI_ZHI[yue_idx]
        day_gz_idx = get_day_gz_index(year, month, day)
        ri_gan = TIAN_GAN[day_gz_idx % 10]
        ri_zhi = DI_ZHI[day_gz_idx % 12]

        # 排盘
        main_info, bian_info = pai_pan(shang, xia, bian_shang, bian_xia)
        # 断卦
        result, reason = duan_gua(main_info, bian_info, dong_yao_list, yue_zhi, ri_zhi)

        # 输出
        print("\n" + "="*50)
        print("排盘结果：")
        print(f"主卦：{main_info['name']}（宫位五行{main_info['gong_wuxing']}） 世爻位：{main_info['shi_wei']}，应爻位：{main_info['ying_wei']}")
        print("六爻信息（爻位 世应 地支 六亲）：")
        for i in range(6):
            print(f"  {i+1}爻 {main_info['shi_ying'][i]:2s} {main_info['dizhi'][i]:2s} {main_info['liuqin'][i]}")
        print(f"变卦：{bian_info['name']}")
        print(f"月建：{yue_zhi}  日辰：{ri_gan}{ri_zhi}")
        print("="*50)
        print(f"预测结果：{result}")
        print("理由：", reason)
        print("="*50)

    except Exception as e:
        print(f"输入错误：{e}")
        print("请重新运行程序。")

if __name__ == '__main__':
    main()
