#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import signal
import threading
from threading import Thread, Event
import select
import queue

# -------------------- 配置参数 --------------------
TOTAL_START = 1000560284742167
TOTAL_END   = 2 * (10**15)   
NUM_SEGMENTS = 8
OVERLAP = 2004
CHECKPOINT_INTERVAL = 3600      # 检查点保存间隔（秒），增大以减少磁盘 I/O
PROGRESS_THROTTLE = 10           # 每收到 PROGRESS_THROTTLE 条才打印一次
# -------------------------------------------------

stop_event = Event()
results = [None] * NUM_SEGMENTS
processes = []                   # 保持所有子进程对象
output_queues = []                # 每个子进程对应的输出队列

def reader(seg_id, pipe, queue):
    """从管道读取行，放入队列，避免直接 print 阻塞"""
    for line in iter(pipe.readline, ''):
        queue.put((seg_id, line.strip()))
    pipe.close()

def worker(seg_id, start, end, checkpoint_file):
    """启动子进程，并设置输出队列"""
    # 绑定 CPU 亲和性（假设 64 核，将 seg_id 绑定到对应核心）
    affinity_cmd = ["taskset", "-c", str(seg_id % 64)]
    cmd = affinity_cmd + [
        "./prime_search",
        str(start),
        str(end),
        checkpoint_file,
        str(CHECKPOINT_INTERVAL)
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # 合并 stderr 到 stdout，简化处理
        universal_newlines=True,
        bufsize=1,
        # preexec_fn=lambda: os.nice(10)  # 降低优先级，避免干扰其他进程（可选）
    )
    processes.append(process)
    
    # 创建队列并启动读取线程
    q = queue.Queue()
    output_queues.append(q)
    t = Thread(target=reader, args=(seg_id, process.stdout, q))
    t.daemon = True
    t.start()
    
    # 等待进程结束
    process.wait()
    # 移除进程
    if process in processes:
        processes.remove(process)

def main():
    print("="*60)
    print("优化版自动并行素数窗口搜索")
    print(f"总范围: [{TOTAL_START}, {TOTAL_END}]")
    print(f"并发段数: {NUM_SEGMENTS} (每个段重叠 {OVERLAP})")
    print(f"检查点间隔: {CHECKPOINT_INTERVAL} 秒")
    print("="*60)

    total_len = TOTAL_END - TOTAL_START
    seg_len = total_len // NUM_SEGMENTS

    # 启动所有工作线程
    for i in range(NUM_SEGMENTS):
        seg_start = TOTAL_START + i * seg_len
        seg_end = TOTAL_START + (i+1) * seg_len - 1 if i < NUM_SEGMENTS-1 else TOTAL_END
        ext_start = max(TOTAL_START, seg_start - OVERLAP)
        ext_end = min(TOTAL_END, seg_end + OVERLAP)
        checkpoint = f"checkpoint_{i}.bin"
        print(f"启动段 {i:2d}: 核心 [{seg_start}, {seg_end}] 扩展 [{ext_start}, {ext_end}] 检查点 {checkpoint}")
        
        t = Thread(target=worker, args=(i, ext_start, ext_end, checkpoint))
        t.daemon = True
        t.start()
        time.sleep(0.2)  # 略微错开启动

    # 主循环：收集输出并处理
    progress_counter = 0
    try:
        while not stop_event.is_set():
            # 非阻塞检查所有队列
            any_activity = False
            for q in output_queues:
                try:
                    seg_id, line = q.get_nowait()
                except queue.Empty:
                    continue
                any_activity = True
                
                if line.startswith("PROGRESS:"):
                    progress_counter += 1
                    if progress_counter % PROGRESS_THROTTLE == 0:
                        prime = line.split(":")[1]
                        print(f"[段 {seg_id:2d}] 当前素数: {prime}")
                        sys.stdout.flush()
                elif line.startswith("SUCCESS:"):
                    n = line.split(":")[1].strip()
                    print(f"\n🎉 段 {seg_id} 找到解: n = {n}")
                    results[seg_id] = n
                    stop_event.set()
                    break
                else:
                    # 其他信息（如错误）直接打印
                    if line:
                        print(f"[段 {seg_id} 信息] {line}")
            
            if not any_activity:
                # 没有新输出时，短暂休眠避免 CPU 空转
                time.sleep(0.01)
            
            # 检查是否所有子进程都已结束
            if all(p.poll() is not None for p in processes):
                break
    except KeyboardInterrupt:
        print("\n用户中断，正在终止所有子进程...")
        stop_event.set()

    # 终止所有子进程
    for p in processes:
        try:
            p.terminate()
        except:
            pass
    # 等待所有线程结束
    time.sleep(2)

    # 输出结果
    found = [res for res in results if res is not None]
    if found:
        print("\n✅ 找到的最小解:", min(found))
    else:
        print("\n❌ 在指定范围内未找到解。")

if __name__ == "__main__":
    main()
