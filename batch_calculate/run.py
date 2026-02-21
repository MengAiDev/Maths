#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import signal
from threading import Thread, Event

# -------------------- 配置参数 --------------------
TOTAL_START = 1000003745670997
TOTAL_END   = 1000201510016365   
NUM_SEGMENTS = 4
OVERLAP = 2004
CHECKPOINT_INTERVAL = 600      
PROGRESS_STEP_PRIMES = 10_000_000  
# -------------------------------------------------

# 全局事件，用于通知所有线程停止
stop_event = Event()
# 存储每个段的结果
results = [None] * NUM_SEGMENTS
# 保存所有子进程对象，以便强制终止
processes = []

def worker(seg_id, start, end, checkpoint_file):
    """在单独线程中运行一个 C++ 子进程，并实时处理输出"""
    cmd = [
        "./prime_search",
        str(start),
        str(end),
        checkpoint_file,
        str(CHECKPOINT_INTERVAL)
    ]
    # 启动子进程，管道连接 stdout/stderr
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    processes.append(process)   # 记录以便全局终止

    # 实时读取 stdout
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if line.startswith("PROGRESS:"):
            prime = line.split(":")[1]
            print(f"[段 {seg_id:2d}] 当前素数: {prime}")
            sys.stdout.flush()
        elif line.startswith("SUCCESS:"):
            n = line.split(":")[1].strip()
            print(f"\n🎉 段 {seg_id} 找到解: n = {n}")
            results[seg_id] = n
            stop_event.set()          # 通知所有线程停止
            process.terminate()        # 自己结束
            break
        # 其他输出（如错误信息）可忽略或打印
        else:
            if line:
                print(f"[段 {seg_id} 信息] {line}")

    process.wait()  # 等待进程真正结束
    # 移除已结束的进程
    if process in processes:
        processes.remove(process)

def main():
    print("="*60)
    print("自动并行素数窗口搜索")
    print(f"总范围: [{TOTAL_START}, {TOTAL_END}]")
    print(f"并发段数: {NUM_SEGMENTS} (每个段重叠 {OVERLAP})")
    print("="*60)

    # 计算每个段的长度（数值范围）
    total_len = TOTAL_END - TOTAL_START
    seg_len = total_len // NUM_SEGMENTS

    threads = []
    for i in range(NUM_SEGMENTS):
        # 本段核心范围 [seg_start, seg_end]
        seg_start = TOTAL_START + i * seg_len
        seg_end = TOTAL_START + (i+1) * seg_len - 1 if i < NUM_SEGMENTS-1 else TOTAL_END
        # 扩展边界以包含重叠
        ext_start = max(TOTAL_START, seg_start - OVERLAP)
        ext_end = min(TOTAL_END, seg_end + OVERLAP)
        checkpoint = f"checkpoint_{i}.bin"
        print(f"启动段 {i:2d}: 核心 [{seg_start}, {seg_end}] 扩展 [{ext_start}, {ext_end}] 检查点 {checkpoint}")

        t = Thread(target=worker, args=(i, ext_start, ext_end, checkpoint))
        t.start()
        threads.append(t)
        # 错开启动，避免同时大量输出
        time.sleep(0.5)

    # 等待所有线程结束或被 stop_event 终止
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
            if stop_event.is_set():
                print("\n检测到解，正在终止所有子进程...")
                for p in processes:
                    p.terminate()
                break
    except KeyboardInterrupt:
        print("\n用户中断，正在终止所有子进程...")
        stop_event.set()
        for p in processes:
            p.terminate()

    # 等待所有线程结束
    for t in threads:
        t.join()

    # 输出最终结果
    found = [res for res in results if res is not None]
    if found:
        print("\n✅ 找到的最小解:", min(found))
    else:
        print("\n❌ 在指定范围内未找到解。")

if __name__ == "__main__":
    main()
