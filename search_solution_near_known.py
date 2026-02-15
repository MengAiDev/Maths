#!/usr/bin/env python3
import gmpy2
from gmpy2 import mpz, is_prime
import random

# 已知解
KNOWN_N = mpz("283652129125808400513278476301455085008845288816557395539337194639631785")
RADIUS = 10**8  
TOTAL_SAMPLES = 50000

def count_primes_in_window(start: mpz) -> int:
    count = 0
    for i in range(2004):
        if is_prime(start + i):
            count += 1
            if count > 12:
                break
    return count

def main():
    print(f"🔍 在已知解 N₀ ± {RADIUS} 范围内密集搜索...")
    found = 0
    with open("local_solutions.txt", "a") as f:
        for i in range(TOTAL_SAMPLES):
            # 随机偏移 [-RADIUS, RADIUS]
            offset = random.randint(-RADIUS, RADIUS)
            candidate = KNOWN_N + offset
            
            if candidate < 1:
                continue
                
            count = count_primes_in_window(candidate)
            if count == 12:
                f.write(f"N={candidate}\n")
                f.flush()
                found += 1
                print(f"🎉 找到局部解 #{found}: N = {candidate}")
            
            if i % 100000 == 0:
                print(f"  进度: {i}/{TOTAL_SAMPLES}", end="\r")

    print(f"\n✅ 完成！找到 {found} 个局部解。")

if __name__ == "__main__":
    main()
