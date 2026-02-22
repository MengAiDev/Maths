#include <primesieve.hpp>
#include <iostream>
#include <fstream>
#include <deque>
#include <cstdint>
#include <chrono>
#include <csignal>
#include <atomic>
#include <algorithm>

std::atomic<bool> keep_running(true);
void signal_handler(int) { keep_running = false; }

const uint64_t PROGRESS_STEP = 10'000'000;
const size_t WINDOW_SIZE = 12;
const uint64_t INTERVAL_LEN = 2004;

// 保存检查点：增加 prev_prime 的存储
bool save_checkpoint(const std::deque<uint64_t>& window, uint64_t last_prime, uint64_t prev_prime,
                     const std::string& filename) {
    std::ofstream ofs(filename, std::ios::binary);
    if (!ofs) return false;
    size_t size = window.size();
    ofs.write(reinterpret_cast<const char*>(&last_prime), sizeof(last_prime));
    ofs.write(reinterpret_cast<const char*>(&prev_prime), sizeof(prev_prime));
    ofs.write(reinterpret_cast<const char*>(&size), sizeof(size));
    for (uint64_t p : window) {
        ofs.write(reinterpret_cast<const char*>(&p), sizeof(p));
    }
    return true;
}

// 加载检查点：同时恢复 prev_prime
bool load_checkpoint(std::deque<uint64_t>& window, uint64_t& last_prime, uint64_t& prev_prime,
                     const std::string& filename) {
    std::ifstream ifs(filename, std::ios::binary);
    if (!ifs) return false;
    size_t size;
    ifs.read(reinterpret_cast<char*>(&last_prime), sizeof(last_prime));
    ifs.read(reinterpret_cast<char*>(&prev_prime), sizeof(prev_prime));
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
    int save_interval = (argc >= 5) ? std::stoi(argv[4]) : 3600;

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
    uint64_t prev_prime = 0;   // 当前窗口第一个素数的前一个素数
    bool checkpoint_loaded = false;

    // 尝试从检查点恢复
    if (!checkpoint_file.empty()) {
        if (load_checkpoint(window, last_prime, prev_prime, checkpoint_file)) {
            std::cout << "Loaded checkpoint. Last prime: " << last_prime
                      << ", prev_prime: " << prev_prime
                      << ", window size: " << window.size() << std::endl;
            it.jump_to(last_prime);
            it.next_prime();   // 移动到下一个素数
            checkpoint_loaded = true;
        }
    }

    if (!checkpoint_loaded) {
        // 全新搜索：定位到 start，并初始化窗口和 prev_prime
        it.jump_to(start);
        // 获取第一个 >= start 的素数
        uint64_t first = it.next_prime();
        while (first < start) {
            first = it.next_prime();
        }
        // 获取 first 的前一个素数（可能为 0，表示不存在）
        uint64_t p0 = it.prev_prime();
        it.next_prime();  // 回到 first
        // 用 first 作为窗口的第一个素数，再读 WINDOW_SIZE-1 个后续素数填满窗口
        window.push_back(first);
        for (size_t i = 1; i < WINDOW_SIZE; ++i) {
            window.push_back(it.next_prime());
        }
        prev_prime = p0;
        last_prime = window.back();
        std::cout << "Starting fresh. First window: first prime = " << window.front()
                  << ", prev_prime = " << prev_prime << std::endl;
    }

    uint64_t prime_count = 0;
    auto last_save = std::chrono::steady_clock::now();

    while (keep_running) {
        uint64_t p = it.next_prime();
        if (p > end) {
            std::cout << "Reached end of range." << std::endl;
            break;
        }

        last_prime = p;
        prime_count++;

        // 滑动窗口：先弹出最前面的素数（该素数将成为新窗口的 prev_prime）
        if (window.size() == WINDOW_SIZE) {
            uint64_t popped = window.front();
            window.pop_front();
            prev_prime = popped;   // 更新为被弹出的素数
        }
        window.push_back(p);

        // 窗口填满时检查条件
        if (window.size() == WINDOW_SIZE) {
            uint64_t p1 = window.front();
            uint64_t p12 = window.back();

            // 获取下一个素数 p13（暂时前移，然后回退）
            uint64_t p13 = it.next_prime();
            it.prev_prime();

            // 计算可能的起始点范围
            uint64_t L = std::max(prev_prime + 1, p12 - (INTERVAL_LEN - 1)); // p12 - 2003
            uint64_t R = std::min(p1, p13 - INTERVAL_LEN);                   // p13 - 2004

            if (L <= R) {
                // 找到解，输出最小的可行起始点 L
                std::cout << "SUCCESS:" << L << std::endl;
                return 0;
            }
        }

        // 进度输出
        if (prime_count % PROGRESS_STEP == 0) {
            std::cout << "PROGRESS:" << p << std::endl;
            std::cout.flush();
        }

        // 定期保存检查点
        auto now = std::chrono::steady_clock::now();
        if (!checkpoint_file.empty() &&
            std::chrono::duration_cast<std::chrono::seconds>(now - last_save).count() >= save_interval) {
            if (save_checkpoint(window, last_prime, prev_prime, checkpoint_file)) {
                std::cout << "Checkpoint saved at prime " << last_prime << std::endl;
            } else {
                std::cerr << "Failed to save checkpoint!" << std::endl;
            }
            last_save = now;
        }
    }

    // 程序正常结束或被中断，保存最终检查点
    if (!checkpoint_file.empty()) {
        save_checkpoint(window, last_prime, prev_prime, checkpoint_file);
        std::cout << "Final checkpoint saved." << std::endl;
    }
    return 0;
}
