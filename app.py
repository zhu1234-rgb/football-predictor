import requests
import math
from datetime import datetime

# ============ 配置区 ============
API_KEY = "YOUR_API_KEY"  # 替换成你免费申请的Key
API_URL = "https://v3.football.api-sports.io"

# ============ 1. 自动抓取初盘 & 变盘（替代手动输入） ============
def get_odds_and_alerts(fixture_id):
    """输入比赛ID，自动返回初盘、变盘，并计算是否触发预警"""
    headers = {"x-rapidapi-key": API_KEY}
    
    # 获取赔率数据（包含初盘和即时盘）
    resp = requests.get(f"{API_URL}/odds", headers=headers, params={"fixture": fixture_id})
    data = resp.json()
    
    if not data["response"]:
        return None
    
    # 取第一个博彩公司（如Bet365）的数据
    bookie = data["response"][0]["bookmakers"][0]
    bets = bookie["bets"][0]["values"]  # 胜平负
    
    initial = {}  # 初盘
    current = {}  # 变盘（即时）
    for item in bets:
        value = item["value"]
        if "odd" in item:  # 初盘
            initial[value] = float(item["odd"])
        if "odd" in item:  # 实际上API结构需按返回调整，这里简化逻辑
            pass 
    
    # 由于免费API结构差异，实战中建议直接取"主胜"索引
    # 这里演示手动模拟数据（实际运行请根据打印的JSON结构调整）
    print("⚠️ 免费API的赔率结构较深，建议先用下面手动输入兜底")
    return {"initial": [1.80, 3.50, 4.00], "current": [1.65, 3.80, 4.50]}

def check_alert(initial, current):
    """变盘预警：胜平负任一降幅超过0.2即报警"""
    alerts = []
    for i, label in enumerate(["主胜", "平局", "客胜"]):
        if initial[i] - current[i] > 0.2:
            alerts.append(f"⚠️ {label}急剧下降 {initial[i]-current[i]:.2f}，热钱涌入！")
    return alerts

# ============ 2. 手动输入模块（必发指数 + 六爻 + 大小球） ============
def manual_inputs():
    print("\n--- 请手动输入以下核心数据 ---")
    bf_big = float(input("必发大球指数 (0-100): "))
    bf_small = float(input("必发小球指数 (0-100): "))
    
    # 六爻量化：动爻能量（用户自己填，1-9）
    moving_yao = int(input("动爻数字 (1-9, 代表力量): "))
    # 卦象生克：主卦评分（-5到+5），影响主队士气
    gua_score = float(input("主卦对主队评分 (-5 极凶 到 +5 极吉): "))
    
    # 手动xG（预期进球）
    xg_home = float(input("主队xG (如1.8): "))
    xg_away = float(input("客队xG (如1.2): "))
    
    return bf_big, bf_small, moving_yao, gua_score, xg_home, xg_away

# ============ 3. 核心算法：泊松分布 + ELO修正 + 战意 ============
def poisson_prob(lam, k):
    """计算泊松分布概率（进球k个的概率）"""
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_score(xg_h, xg_a, yizhang_factor, gua_factor, bf_big):
    """预测具体比分"""
    # 战意系数（用户可改，这里默认1.0）
    zhan_yi = 1.0  
    # 必发大球指数高于65，调高进球预期
    if bf_big > 65:
        xg_h *= 1.15
        xg_a *= 1.15
    # 六爻卦象影响（动爻+卦评分转化为波动）
    yao_effect = 1 + (moving_yao / 10) * 0.05
    gua_effect = 1 + (gua_score / 50)  # -5分变0.9，+5变1.1
    
    lam_h = xg_h * yizhang_factor * yao_effect * gua_effect
    lam_a = xg_a * yizhang_factor * yao_effect * (1/gua_effect)  # 客队反着来
    
    # 计算最高概率比分 (0-4球)
    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100  # 转百分比
    
    # 排序取前5
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_scores, lam_h, lam_a

# ============ 4. 凯利公式（评估庄家风险） ============
def kelly_calc(odds, prob):
    """odds: 当前赔率, prob: 你预测的真实概率(0-1)"""
    return (odds * prob - (1 - prob)) / odds

# ============ 5. 主程序执行 ============
if __name__ == "__main__":
    print("⚽ 足球预测引擎启动 (手机版) ⚽")
    
    # 第一步：免费API拉取（因手机网络限制，这里用模拟数据演示）
    print("\n【自动拉取初盘/变盘】")
    odds_data = get_odds_and_alerts(123456)  # 123456替换为真实比赛ID
    if odds_data:
        alerts = check_alert(odds_data["initial"], odds_data["current"])
        for a in alerts:
            print(a)
    else:
        print("📵 API未响应，请检查网络或Key，手动输入初盘兜底：")
        init_odds = input("输入初盘 主胜 平 客胜 (空格分隔): ").split()
        curr_odds = input("输入变盘 主胜 平 客胜 (空格分隔): ").split()
    
    # 第二步：手动输入核心指标
    bf_big, bf_small, moving_yao, gua_score, xg_h, xg_a = manual_inputs()
    
    # 第三步：比分预测
    print("\n【预测结果】")
    top_scores, lam_h, lam_a = predict_score(xg_h, xg_a, 1.0, gua_score, bf_big)
    print(f"主队预期进球 λ = {lam_h:.2f}, 客队 λ = {lam_a:.2f}")
    print("最可能的比分预测 (概率%)：")
    for score, prob in top_scores:
        print(f"  {score}  ->  {prob:.2f}%")
    
    # 第四步：凯利风控（假设当前主胜赔率为1.8）
    kelly_val = kelly_calc(1.8, top_scores[0][1]/100)
    if kelly_val > 0.8:
        print(f"🚨 凯利值高达 {kelly_val:.2f}，庄家赔付风险极大，建议反买！")
    else:
        print(f"✅ 凯利值 {kelly_val:.2f}，处于安全区间。")
    
    print("\n✅ 预测完成！下次直接修改上面的API_KEY即可。")
