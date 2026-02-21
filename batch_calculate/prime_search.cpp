#include <primesieve.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <deque>
#include <cstdint>
#include <chrono>
#include <csignal>
#include <atomic>
#include <cstring>

// 全局原子标志，用于响应 Ctrl+C
std::atomic<bool> keep_running(true);
void signal_handler(int) { keep_running = false; }

// 进度输出间隔（每处理这么多素数输出一次当前素数）
const uint64_t PROGRESS_STEP = 10'000'000;

// 窗口大小（连续素数个数）
const size_t WINDOW_SIZE = 12;

// 区间长度（2004 个整数）
const uint64_t INTERVAL_LEN = 2004;

// 检查点文件格式：先写入 last_prime（8字节），再写入窗口大小（8字节），然后依次写入窗口中的每个素数（每个8字节）
bool save_checkpoint(const std::deque<uint64_t>& window, uint64_t last_prime,
                     const std::string& filename) {
    std::ofstream ofs(filename, std::ios::binary);
    if (!ofs) return false;
    size_t size = window.size();
    ofs.write(reinterpret_cast<const char*>(&last_prime), sizeof(last_prime));
    ofs.write(reinterpret_cast<const char*>(&size), sizeof(size));
    for (uint64_t p : window) {
        ofs.write(reinterpret_cast<const char*>(&p), sizeof(p));
    }
    return true;
}

bool load_checkpoint(std::deque<uint64_t>& window, uint64_t& last_prime,
                     const std::string& filename) {
    std::ifstream ifs(filename, std::ios::binary);
    if (!ifs) return false;
    size_t size;
    ifs.read(reinterpret_cast<char*>(&last_prime), sizeof(last_prime));
    ifs.read(reinterpret_cast<char*>(&size), sizeof(size));
    window.clear();
    for (size_t i = 0; i < size; ++i) {
        uint64_t p;
        ifs.read(reinterpret_cast<char*>(&p), sizeof(p));
        window.push_back(p);
    }
    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <start> <end> [checkpoint_file] [save_interval_seconds]\n";
        return 1;
    }

    uint64_t start = std::stoull(argv[1]);
    uint64_t end   = std::stoull(argv[2]);
    std::string checkpoint_file = (argc >= 4) ? argv[3] : "";
    int save_interval = (argc >= 5) ? std::stoi(argv[4]) : 3600; // 默认1小时

    // 注册信号处理
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    std::cout << "Searching from " << start << " to " << end << "\n"
              << "Checkpoint: " << (checkpoint_file.empty() ? "disabled" : checkpoint_file) << "\n"
              << "Save interval: " << save_interval << " seconds\n"
              << "Press Ctrl+C to interrupt gracefully.\n"
              << "Progress output every " << PROGRESS_STEP << " primes.\n";

    primesieve::iterator it;
    std::deque<uint64_t> window;
    uint64_t last_prime = 0;
    bool checkpoint_loaded = false;

    // 尝试加载检查点
    if (!checkpoint_file.empty()) {
        if (load_checkpoint(window, last_prime, checkpoint_file)) {
            std::cout << "Loaded checkpoint. Last prime: " << last_prime
                      << ", window size: " << window.size() << std::endl;
            // 将迭代器定位到 last_prime 之后的下一个素数
            it.jump_to(last_prime);
            it.next_prime();   // 移动到下一个素数（因为 last_prime 已经处理过）
            checkpoint_loaded = true;
        }
    }

    // 如果没有检查点，从 start 开始
    if (!checkpoint_loaded) {
        it.jump_to(start);
        uint64_t p = it.next_prime();
        while (p < start) {   // 确保 p >= start（理论不会发生，但以防万一）
            p = it.next_prime();
        }
        last_prime = p - 1;   // 使循环中第一个 p 成为新素数（稍后会在循环中处理）
        // 但更好的做法是：将 last_prime 设为 start-1，这样循环中会正确处理第一个素数
        // 这里我们直接让 last_prime 记录最新处理的素数，窗口初始为空
        last_prime = 0;        // 标记尚未处理任何素数，窗口为空
        window.clear();
        std::cout << "Starting fresh. First prime will be read." << std::endl;
    }

    uint64_t prime_count = 0;           // 用于进度计数
    auto last_save = std::chrono::steady_clock::now();

    while (keep_running) {
        // 获取下一个素数
        uint64_t p = it.next_prime();
        if (p > end) {
            std::cout << "Reached end of range." << std::endl;
            break;
        }

        last_prime = p;
        prime_count++;

        // 更新窗口
        window.push_back(p);
        if (window.size() > WINDOW_SIZE) {
            window.pop_front();
        }

        // 当窗口填满12个时检查条件
        if (window.size() == WINDOW_SIZE) {
            uint64_t span = window.back() - window.front();
            if (span <= INTERVAL_LEN - 1) {   // 跨度 ≤ 2003 才能放入长度2004的区间
                // 需要检查下一个素数是否超出区间 [window.front(), window.front()+2003]
                uint64_t next_p = it.next_prime();
                it.prev_prime();   // 回退，保持迭代器不变
                if (next_p > window.front() + (INTERVAL_LEN - 1)) {
                    // 找到候选解 n = window.front()
                    std::cout << "SUCCESS:" << window.front() << std::endl;
                    return 0;   // 直接退出程序
                }
            }
        }

        // 定期输出进度（每 PROGRESS_STEP 个素数）
        if (prime_count % PROGRESS_STEP == 0) {
            std::cout << "PROGRESS:" << p << std::endl;
            std::cout.flush();
        }

        // 定期保存检查点
        auto now = std::chrono::steady_clock::now();
        if (!checkpoint_file.empty() &&
            std::chrono::duration_cast<std::chrono::seconds>(now - last_save).count() >= save_interval) {
            if (save_checkpoint(window, last_prime, checkpoint_file)) {
                std::cout << "Checkpoint saved at prime " << last_prime << std::endl;
            } else {
                std::cerr << "Failed to save checkpoint!" << std::endl;
            }
            last_save = now;
        }
    }

    // 正常结束或中断，保存最终检查点
    if (!checkpoint_file.empty()) {
        save_checkpoint(window, last_prime, checkpoint_file);
        std::cout << "Final checkpoint saved." << std::endl;
    }
    return 0;
}