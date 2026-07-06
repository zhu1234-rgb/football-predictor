# -*- coding: utf-8 -*-
"""
六爻足球预测（完整版）—— 第一部分：数据层
包含：六十四卦完整列表、上下卦映射表、八卦五行、卦象吉凶倾向、五行生克函数
"""

# ---------- 1.1 八卦数字映射（乾1兑2离3震4巽5坎6艮7坤8）----------
NUM_TO_GUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤"
}

# ---------- 1.2 六十四卦上下卦组合映射表（完整64条）----------
GUA_MAP = {
    # 乾宫
    ("乾", "乾"): "乾", ("乾", "坤"): "否", ("乾", "震"): "无妄",
    ("乾", "巽"): "姤", ("乾", "坎"): "讼", ("乾", "离"): "同人",
    ("乾", "艮"): "遁", ("乾", "兑"): "履",
    # 坤宫
    ("坤", "乾"): "泰", ("坤", "坤"): "坤", ("坤", "震"): "复",
    ("坤", "巽"): "升", ("坤", "坎"): "师", ("坤", "离"): "明夷",
    ("坤", "艮"): "谦", ("坤", "兑"): "临",
    # 震宫
    ("震", "乾"): "大壮", ("震", "坤"): "豫", ("震", "震"): "震",
    ("震", "巽"): "恒", ("震", "坎"): "解", ("震", "离"): "丰",
    ("震", "艮"): "小过", ("震", "兑"): "归妹",
    # 巽宫
    ("巽", "乾"): "小畜", ("巽", "坤"): "观", ("巽", "震"): "益",
    ("巽", "巽"): "巽", ("巽", "坎"): "涣", ("巽", "离"): "家人",
    ("巽", "艮"): "渐", ("巽", "兑"): "中孚",
    # 坎宫
    ("坎", "乾"): "需", ("坎", "坤"): "比", ("坎", "震"): "屯",
    ("坎", "巽"): "井", ("坎", "坎"): "坎", ("坎", "离"): "既济",
    ("坎", "艮"): "蹇", ("坎", "兑"): "节",
    # 离宫
    ("离", "乾"): "大有", ("离", "坤"): "晋", ("离", "震"): "噬嗑",
    ("离", "巽"): "鼎", ("离", "坎"): "未济", ("离", "离"): "离",
    ("离", "艮"): "旅", ("离", "兑"): "睽",
    # 艮宫
    ("艮", "乾"): "大畜", ("艮", "坤"): "剥", ("艮", "震"): "颐",
    ("艮", "巽"): "蛊", ("艮", "坎"): "蒙", ("艮", "离"): "贲",
    ("艮", "艮"): "艮", ("艮", "兑"): "损",
    # 兑宫
    ("兑", "乾"): "夬", ("兑", "坤"): "萃", ("兑", "震"): "随",
    ("兑", "巽"): "大过", ("兑", "坎"): "困", ("兑", "离"): "革",
    ("兑", "艮"): "咸", ("兑", "兑"): "兑"
}

# ---------- 1.3 八卦五行属性 ----------
GUA_WUXING = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土"
}

# ---------- 1.4 卦象吉凶倾向（预测方向）----------
GUA_JI_XIONG = {
    "乾": "主队有利", "坤": "平局倾向", "屯": "主队有利", "蒙": "客队有利",
    "需": "主队有利", "讼": "客队有利", "师": "主队有利", "比": "主队有利",
    "小畜": "主队有利", "履": "主队有利", "泰": "主队有利", "否": "客队有利",
    "同人": "主队有利", "大有": "主队有利", "谦": "主队有利", "豫": "主队有利",
    "随": "主队有利", "蛊": "客队有利", "临": "主队有利", "观": "平局倾向",
    "噬嗑": "客队有利", "贲": "主队有利", "剥": "客队有利", "复": "主队有利",
    "无妄": "主队有利", "大畜": "主队有利", "颐": "平局倾向", "大过": "客队有利",
    "坎": "客队有利", "离": "主队有利", "咸": "主队有利", "恒": "平局倾向",
    "遁": "客队有利", "大壮": "主队有利", "晋": "主队有利", "明夷": "客队有利",
    "家人": "主队有利", "睽": "客队有利", "蹇": "客队有利", "解": "主队有利",
    "损": "客队有利", "益": "主队有利", "夬": "主队有利", "姤": "平局倾向",
    "萃": "主队有利", "升": "主队有利", "困": "客队有利", "井": "平局倾向",
    "革": "客队有利", "鼎": "主队有利", "震": "平局倾向", "艮": "平局倾向",
    "渐": "主队有利", "归妹": "客队有利", "丰": "主队有利", "旅": "客队有利",
    "巽": "平局倾向", "兑": "主队有利", "涣": "客队有利", "节": "平局倾向",
    "中孚": "主队有利", "小过": "客队有利", "既济": "主队有利", "未济": "客队有利"
}

# ---------- 1.5 五行生克函数（返回权重）----------
def wuxing_sheng_ke(wo, ta):
    """
    五行生克关系
    wo: 体卦五行, ta: 用卦五行
    返回值: 正=主队有利, 负=客队有利, 0=平衡
    """
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if wo == ta:
        return 0.0
    elif sheng[wo] == ta:   # 体生用 → 主队耗损，客队有利
        return -0.2
    elif ke[wo] == ta:      # 体克用 → 主队有利
        return 0.3
    elif sheng[ta] == wo:   # 用生体 → 主队有利
        return 0.25
    elif ke[ta] == wo:      # 用克体 → 客队有利
        return -0.3
    else:
        return 0.0
        # -*- coding: utf-8 -*-
"""
六爻足球预测（完整版）—— 第二部分：逻辑层
包含：队名哈希取卦、时间定动爻、变卦生成、体用判定、胜平负综合决策
"""

import datetime

# 从第一段导入数据（实际合并时可直接保留所有定义，此处仅为逻辑划分）
# 假设第一段所有变量和函数已定义

def get_unicode_sum(text):
    """
    取队名前两个字符的Unicode码点之和（若不足两字则补0）
    """
    if not text:
        return 0
    chars = list(text.strip())[:2]
    total = 0
    for ch in chars:
        total += ord(ch)
    return total

def build_ben_gua(shang_num, xia_num):
    """
    根据上下卦数字（1~8）返回本卦名
    """
    shang = NUM_TO_GUA[shang_num]
    xia = NUM_TO_GUA[xia_num]
    return GUA_MAP.get((shang, xia), "未知")

def get_ben_gua_from_names(home, away):
    """
    根据主客队名直接算出本卦（不包含动爻）
    """
    shang_num = get_unicode_sum(home) % 8
    xia_num = get_unicode_sum(away) % 8
    if shang_num == 0: shang_num = 8
    if xia_num == 0: xia_num = 8
    shang = NUM_TO_GUA[shang_num]
    xia = NUM_TO_GUA[xia_num]
    ben = GUA_MAP.get((shang, xia), "未知")
    return ben, shang, xia

def get_dong_yao(dt):
    """
    根据比赛时间（datetime对象）计算动爻索引（0~5）
    使用年+月+日+时+分 之和取模6
    """
    total = dt.year + dt.month + dt.day + dt.hour + dt.minute
    return total % 6

def get_zhi_gua(ben, dong):
    """
    根据本卦和动爻位置（0~5）生成变卦名
    思路：将本卦拆成上下卦，根据动爻所在位置（0~2在下卦，3~5在上卦）
    将对应爻阴阳互换，然后重新组成新上下卦数字，再查表。
    但本卦我们只有卦名，没有六爻阴阳，所以无法真正变卦。
    因此采用简化方法：若动爻在下卦（0~2），则下卦变为其错卦；若在上卦（3~5），则上卦变为错卦。
    错卦：乾↔坤，兑↔艮，离↔坎，震↔巽（即八卦的对冲）
    """
    # 八卦错卦映射
    CUO = {
        "乾": "坤", "坤": "乾",
        "兑": "艮", "艮": "兑",
        "离": "坎", "坎": "离",
        "震": "巽", "巽": "震"
    }
    # 为了得到本卦的上下卦，我们需要从GUA_MAP反查，因为映射是双向的，我们建立反向字典
    # 由于调用频繁，我们可以在外层构建，此处为了独立，临时构建
    rev_map = {v: k for k, v in GUA_MAP.items()}
    if ben not in rev_map:
        return ben  # 无法反查则不变
    shang, xia = rev_map[ben]
    if dong < 3:  # 动在下卦
        new_xia = CUO.get(xia, xia)
        new_shang = shang
    else:         # 动在上卦
        new_shang = CUO.get(shang, shang)
        new_xia = xia
    return GUA_MAP.get((new_shang, new_xia), ben)

def get_ti_yong(ben, dong):
    """
    根据动爻位置判定体卦和用卦
    动爻在初、二、三爻（索引0,1,2）→ 用卦在下，体卦在上
    动爻在四、五、上爻（索引3,4,5）→ 用卦在上，体卦在下
    返回 (体卦, 用卦)
    """
    rev_map = {v: k for k, v in GUA_MAP.items()}
    if ben not in rev_map:
        return "乾", "坤"  # 默认
    shang, xia = rev_map[ben]
    if dong < 3:
        return shang, xia   # 体为上，用为下
    else:
        return xia, shang   # 体为下，用为上

def predict_football(home, away, dt):
    """
    核心预测函数
    输入：主队名、客队名、比赛时间（datetime）
    返回：预测结果（"主胜"/"平局"/"客胜"）以及卦象信息字典
    """
    # 1. 计算本卦及上下卦
    shang_num = get_unicode_sum(home) % 8
    xia_num = get_unicode_sum(away) % 8
    if shang_num == 0: shang_num = 8
    if xia_num == 0: xia_num = 8
    shang = NUM_TO_GUA[shang_num]
    xia = NUM_TO_GUA[xia_num]
    ben = GUA_MAP.get((shang, xia), "未知")

    # 2. 动爻
    dong = get_dong_yao(dt)

    # 3. 变卦（简化，仅用于展示）
    zhi = get_zhi_gua(ben, dong)

    # 4. 体用判定
    ti, yong = get_ti_yong(ben, dong)

    # 5. 卦象吉凶倾向（基准）
    ji = GUA_JI_XIONG.get(ben, "平局倾向")

    # 6. 体用五行生克
    ti_w = GUA_WUXING.get(ti, "土")
    yong_w = GUA_WUXING.get(yong, "土")
    shengke = wuxing_sheng_ke(ti_w, yong_w)

    # 7. 综合决策
    # 基础倾向转数值：主胜=1，平=0，客胜=-1
    if "主队有利" in ji:
        base = 1
    elif "客队有利" in ji:
        base = -1
    else:
        base = 0

    # 五行生克调整
    if shengke > 0.1:
        adjust = 1
    elif shengke < -0.1:
        adjust = -1
    else:
        adjust = 0

    # 如果基础倾向为平，则直接用调整
    if base == 0:
        result = adjust
    else:
        # 若基础与调整方向一致，则强化；若相反，则保守取平
        if base == adjust or adjust == 0:
            result = base
        else:
            result = 0

    # 最终方向
    if result > 0:
        final = "主胜"
    elif result < 0:
        final = "客胜"
    else:
        final = "平局"

    # 8. 组装返回信息
    info = {
        "本卦": ben,
        "变卦": zhi,
        "动爻": f"第{dong+1}爻",
        "体卦": ti,
        "用卦": yong,
        "体五行": ti_w,
        "用五行": yong_w,
        "体用关系": "生" if shengke > 0.1 else ("克" if shengke < -0.1 else "比和"),
        "卦象吉凶": ji,
        "五行权重": shengke
    }
    return final, info
    # -*- coding: utf-8 -*-
"""
六爻足球预测（完整版）—— 第三部分：界面层
基于 Streamlit 的交互界面，输入框无占位文字，仅输出胜平负及卦象详情
"""

import streamlit as st
import datetime

# 从第二段导入预测函数（实际合并时直接使用）
# 假设第二段所有函数已定义

def main():
    st.set_page_config(page_title="六爻足球预测", layout="centered")
    st.title("⚽ 六爻 · 足球胜平负预测")
    st.markdown("基于主客队名前两字 + 比赛时间起卦，纯卦象推演")

    # 输入区域（无示范文字）
    col1, col2 = st.columns(2)
    with col1:
        home = st.text_input("主队名称", value="")
    with col2:
        away = st.text_input("客队名称", value="")

    # 时间选择器
    dt = st.datetime_input(
        "比赛时间",
        value=datetime.datetime.now(),
        format="YYYY-MM-DD HH:mm"
    )

    if st.button("🔮 预测"):
        # 输入校验
        if not home.strip() or not away.strip():
            st.warning("请完整输入主队和客队名称")
            return
        if home.strip() == away.strip():
            st.warning("主队和客队不能相同")
            return

        # 执行预测
        result, info = predict_football(home.strip(), away.strip(), dt)

        # 显示结果
        st.subheader("预测结果")
        if result == "主胜":
            st.success(f"🏆 {home} 胜")
        elif result == "客胜":
            st.success(f"🏆 {away} 胜")
        else:
            st.warning("🤝 平局")

        # 卦象详情（可折叠展开）
        with st.expander("📊 查看卦象详情"):
            col_a, col_b = st.columns(2)
            col_a.metric("本卦", info["本卦"])
            col_b.metric("变卦", info["变卦"])
            st.write(f"**动爻**：{info['动爻']}")
            st.write(f"**体卦**：{info['体卦']}（{info['体五行']}）  **用卦**：{info['用卦']}（{info['用五行']}）")
            st.write(f"**体用关系**：{info['体用关系']}")
            st.write(f"**卦象吉凶**：{info['卦象吉凶']}")
            st.caption(f"五行权重系数：{info['五行权重']:.2f}")

if __name__ == "__main__":
    main()
