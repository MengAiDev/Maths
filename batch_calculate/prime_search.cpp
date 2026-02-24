#include <primesieve.hpp>
#include <iostream>
#include <fstream>
#include <array>
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

// 使用固定大小循环数组保存窗口
struct PrimeWindow {
    std::array<uint64_t, WINDOW_SIZE> buf{};
    size_t head = 0;          // 指向窗口第一个素数的索引

    void push(uint64_t p, uint64_t& popped) {
        popped = buf[head];                               // 被覆盖的元素即为弹出的素数
        buf[(head + WINDOW_SIZE - 1) % WINDOW_SIZE] = p;  // 新素数写入尾部
        head = (head + 1) % WINDOW_SIZE;                  // 头部前移
    }

    uint64_t front() const { return buf[head]; }
    uint64_t back() const  { return buf[(head + WINDOW_SIZE - 1) % WINDOW_SIZE]; }

    // 按顺序获取所有元素（从头部到尾部）
    void get_all(uint64_t* out) const {
        for (size_t i = 0; i < WINDOW_SIZE; ++i)
            out[i] = buf[(head + i) % WINDOW_SIZE];
    }

    // 按顺序设置所有元素（假设 head = 0）
    void set_all(const uint64_t* in) {
        std::copy(in, in + WINDOW_SIZE, buf.begin());
        head = 0;
    }
};

bool save_checkpoint(const PrimeWindow& window, uint64_t last_prime, uint64_t prev_prime,
                     const std::string& filename) {
    std::ofstream ofs(filename, std::ios::binary);
    if (!ofs) return false;
    ofs.write(reinterpret_cast<const char*>(&last_prime), sizeof(last_prime));
    ofs.write(reinterpret_cast<const char*>(&prev_prime), sizeof(prev_prime));
    uint64_t buf[WINDOW_SIZE];
    window.get_all(buf);
    ofs.write(reinterpret_cast<const char*>(buf), sizeof(buf));
    return true;
}

bool load_checkpoint(PrimeWindow& window, uint64_t& last_prime, uint64_t& prev_prime,
                     const std::string& filename) {
    std::ifstream ifs(filename, std::ios::binary);
    if (!ifs) return false;
    // 检查读取是否完整
    if (!ifs.read(reinterpret_cast<char*>(&last_prime), sizeof(last_prime)) ||
        !ifs.read(reinterpret_cast<char*>(&prev_prime), sizeof(prev_prime))) {
        return false;
    }
    uint64_t buf[WINDOW_SIZE];
    if (!ifs.read(reinterpret_cast<char*>(buf), sizeof(buf))) {
        return false;
    }
    window.set_all(buf);
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
    PrimeWindow window;
    uint64_t last_prime = 0;
    uint64_t prev_prime = 0;
    uint64_t next_prime = 0;      // 当前窗口最后一个素数的下一个素数
    bool checkpoint_loaded = false;

    // 尝试从检查点恢复
    if (!checkpoint_file.empty()) {
        if (load_checkpoint(window, last_prime, prev_prime, checkpoint_file)) {
            std::cout << "Loaded checkpoint. Last prime: " << last_prime
                      << ", prev_prime: " << prev_prime << std::endl;
            it.jump_to(last_prime);
            // 正确获取 last_prime 的下一个素数（窗口后的第一个素数）
            next_prime = it.next_prime();
            checkpoint_loaded = true;
        }
    }

    if (!checkpoint_loaded) {
        // 全新搜索：定位到 start，填充初始窗口
        it.jump_to(start);
        uint64_t first = it.next_prime();
        while (first < start) first = it.next_prime(); // 确保 first >= start

        // 获取 first 的前一个素数
        prev_prime = it.prev_prime();
        it.next_prime();  // 回到 first

        // 填充窗口：first 及其后 WINDOW_SIZE-1 个素数
        window.buf[0] = first;
        for (size_t i = 1; i < WINDOW_SIZE; ++i)
            window.buf[i] = it.next_prime();
        window.head = 0;  // 头部指向第一个元素

        last_prime = window.back();
        next_prime = it.next_prime();  // 获取最后一个素数的下一个素数

        std::cout << "Starting fresh. First window: first prime = " << window.front()
                  << ", prev_prime = " << prev_prime << std::endl;
    }

    uint64_t prime_count = 0;
    auto last_save = std::chrono::steady_clock::now();

    while (keep_running) {
        uint64_t p = next_prime;          // 要加入窗口的素数
        if (p > end) break;               // 超出范围，退出

        next_prime = it.next_prime();      // 获取 p 的下一个素数，供下一轮使用
        last_prime = p;
        ++prime_count;

        // 滑动窗口：弹出最前一个，并更新 prev_prime
        uint64_t popped;
        window.push(p, popped);
        // 窗口始终保持 WINDOW_SIZE 个素数，首次填充后 popped 即为被弹出的素数
        prev_prime = popped;

        // 快速失败：仅当 p12 - 2003 <= p1 时才需计算完整条件
        uint64_t p1 = window.front();
        uint64_t p12 = p;  // 刚加入的 p 即为窗口最后一个
        // 防止无符号整数减法回绕
        if (p12 >= INTERVAL_LEN - 1 && p12 - (INTERVAL_LEN - 1) <= p1) {
            uint64_t p13 = next_prime;     // p12 的下一个素数
            if (p13 >= INTERVAL_LEN) {     // 确保 p13 - INTERVAL_LEN 不溢出
                uint64_t L = std::max(prev_prime + 1, p12 - (INTERVAL_LEN - 1));
                uint64_t R = std::min(p1, p13 - INTERVAL_LEN);
                if (L <= R) {
                    std::cout << "SUCCESS:" << L << std::endl;
                    return 0;
                }
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

    // 程序结束或被中断，保存最终检查点
    if (!checkpoint_file.empty()) {
        save_checkpoint(window, last_prime, prev_prime, checkpoint_file);
        std::cout << "Final checkpoint saved." << std::endl;
    }
    return 0;
}