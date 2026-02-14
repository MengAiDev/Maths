#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <iomanip>

using namespace std;
using namespace chrono;

class PrimeIntervalFinder {
private:
    const int LENGTH = 2004;
    const int TARGET = 12;
    long long limit;
    vector<bool> is_prime;
    
    // 埃拉托色尼筛法
    void sieve(long long n) {
        cout << "Sieving up to " << n << "..." << endl;
        auto start_time = high_resolution_clock::now();
        
        is_prime.assign(n + 1, true);
        if (n >= 0) is_prime[0] = false;
        if (n >= 1) is_prime[1] = false;
        
        long long sqrt_n = sqrt(n);
        for (long long i = 2; i <= sqrt_n; ++i) {
            if (is_prime[i]) {
                for (long long j = i * i; j <= n; j += i) {
                    is_prime[j] = false;
                }
            }
        }
        
        auto end_time = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end_time - start_time);
        cout << "Sieving completed in " << duration.count() << " ms" << endl;
    }
    
    // 验证区间内的素数
    void verify_interval(long long start, int count) {
        cout << "\nVerifying interval [" << start << ", " << start + LENGTH - 1 << "]:" << endl;
        cout << "Found " << count << " primes" << endl;
        
        if (count <= 20) {  // 如果素数不多，列出它们
            cout << "Prime numbers: ";
            int printed = 0;
            for (long long i = start; i < start + LENGTH && printed < 20; ++i) {
                if (is_prime[i]) {
                    cout << i << " ";
                    printed++;
                }
            }
            if (count > 20) cout << "...";
            cout << endl;
        }
    }
    
public:
    PrimeIntervalFinder() : limit(1000000) {}
    
    void find() {
        cout << "=========================================" << endl;
        cout << "Finding " << LENGTH << " consecutive integers" << endl;
        cout << "that contain exactly " << TARGET << " primes" << endl;
        cout << "=========================================" << endl;
        
        auto program_start = high_resolution_clock::now();
        long long start = 1;
        int prime_count = 0;
        long long iterations = 0;
        
        // 初始筛法
        sieve(limit + LENGTH);
        
        // 计算第一个区间
        cout << "Initializing first interval..." << endl;
        for (long long i = start; i <= start + LENGTH - 1; ++i) {
            if (is_prime[i]) prime_count++;
        }
        
        cout << "Initial prime count in [1, 2004]: " << prime_count << endl;
        
        // 搜索
        cout << "\nSearching... (this may take a while)" << endl;
        auto last_report = high_resolution_clock::now();
        
        while (true) {
            iterations++;
            
            // 每100万次迭代报告进度
            if (iterations % 1000000 == 0) {
                auto now = high_resolution_clock::now();
                auto elapsed = duration_cast<seconds>(now - last_report);
                cout << "Checked " << start << " (" << prime_count << " primes) - "
                     << "Progress: " << fixed << setprecision(2) 
                     << (start * 100.0 / limit) << "%" << endl;
                last_report = now;
            }
            
            if (prime_count == TARGET) {
                auto end_time = high_resolution_clock::now();
                auto total_time = duration_cast<seconds>(end_time - program_start);
                
                cout << "\n✓ FOUND SOLUTION!" << endl;
                cout << "=========================================" << endl;
                cout << "Interval: [" << start << ", " << start + LENGTH - 1 << "]" << endl;
                cout << "Contains exactly " << prime_count << " primes" << endl;
                cout << "Found after checking " << iterations << " intervals" << endl;
                cout << "Time taken: " << total_time.count() << " seconds" << endl;
                cout << "=========================================" << endl;
                
                verify_interval(start, prime_count);
                break;
            }
            
            // 滑动窗口
            if (is_prime[start]) prime_count--;
            if (is_prime[start + LENGTH]) prime_count++;
            start++;
            
            // 需要扩大筛法范围
            if (start + LENGTH > limit) {
                cout << "\n⚠ Reached sieve limit. Expanding..." << endl;
                long long old_limit = limit;
                limit *= 2;
                cout << "Expanding from " << old_limit << " to " << limit << endl;
                
                // 重新筛法
                sieve(limit + LENGTH);
                
                // 重新计算当前区间的素数个数
                prime_count = 0;
                for (long long i = start; i <= start + LENGTH - 1; ++i) {
                    if (i < is_prime.size() && is_prime[i]) prime_count++;
                }
                cout << "Resumed search at " << start << " with " << prime_count << " primes" << endl;
            }
        }
    }
};

int main() {
    try {
        PrimeIntervalFinder finder;
        finder.find();
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}

// MengAiDev 2026
