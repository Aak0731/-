import random
from math import pow

TRIALS = 100_000
HARD_PITY = 90
BASE_PROB_OLD = 0.006

target_exp = (1 - pow(1 - BASE_PROB_OLD, HARD_PITY)) / BASE_PROB_OLD
target_p80 = 0.38 + 0.18

def new_mechanism_stats(p0, p89_end):
    k = (p89_end - p0) / 16.0
    exp_val = 0.0
    surv = 1.0
    p80 = 0.0
    for n in range(1, 90):
        prob = p0 if n <= 73 else p0 + k * (n - 73)
        prob = min(prob, 1.0)
        exp_val += surv * prob * n
        if n <= 80:
            p80 += surv * prob
        surv *= (1.0 - prob)
    exp_val += surv * 90.0
    return exp_val, p80

best_p0 = best_p89 = None
best_p80_error = float('inf')

for p89_end in [x / 200 for x in range(20, 181)]:
    lo, hi = 0.001, 0.01
    for _ in range(40):
        mid = (lo + hi) / 2
        exp_mid, _ = new_mechanism_stats(mid, p89_end)
        if exp_mid > target_exp:
            lo = mid
        else:
            hi = mid
    p0 = (lo + hi) / 2
    exp_check, p80_check = new_mechanism_stats(p0, p89_end)
    if abs(exp_check - target_exp) > 0.015:
        continue
    err = abs(p80_check - target_p80)
    if err < best_p80_error:
        best_p80_error = err
        best_p0, best_p89 = p0, p89_end

k_val = (best_p89 - best_p0) / 16.0

def prob_new(n):
    if n <= 73:
        return best_p0
    if n <= 89:
        return best_p0 + k_val * (n - 73)
    return 1.0

def simulate_old():
    for n in range(1, HARD_PITY + 1):
        if n == HARD_PITY or random.random() < BASE_PROB_OLD:
            return n
    return HARD_PITY

def simulate_new():
    for n in range(1, HARD_PITY + 1):
        if n == HARD_PITY or random.random() < prob_new(n):
            return n
    return HARD_PITY

old_data = [simulate_old() for _ in range(TRIALS)]
new_data = [simulate_new() for _ in range(TRIALS)]

old_avg = sum(old_data) / TRIALS
new_avg = sum(new_data) / TRIALS
old_before80 = sum(1 for x in old_data if x <= 80) / TRIALS
new_before80 = sum(1 for x in new_data if x <= 80) / TRIALS

print(f"旧机制平均抽取数: {old_avg:.2f} 抽")
print(f"新机制平均抽取数: {new_avg:.2f} 抽")
print(f"期望偏差: {abs(old_avg - new_avg):.4f} 抽")
print(f"旧机制 80 抽前出货概率: {old_before80*100:.2f}%")
print(f"新机制 80 抽前出货概率: {new_before80*100:.2f}%")
print(f"概率提升: {(new_before80 - old_before80)*100:.2f} 个百分点")
