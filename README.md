## **Problem Definition**
This problem appears in a number theory textbook:  
Find the smallest positive integer $N$ such that the interval of $2004$ consecutive integers $[N, N+2003]$ contains **exactly $12$ primes**.

- Preliminary analysis: Expected number of primes = $12$ $\Rightarrow$ $N \approx e^{167} \approx 10^{72.5}$
- Known: Computer verification up to **$10.53$B** found no solution

---

## **Theoretical Analysis: Why Brute Force Is Infeasible**
- For $N \leq 10^{14}$, the expected number of primes $\approx 62$, and the actual minimum $> 40$
- Prime density decreases very slowly, so **the solution must be far larger than $10^{14}$**
- A naive linear scan would require cosmological computing power ( $> 10^{30}$ years)

---

## **Engineering Optimizations**
- Developed a **multi-threaded segmented sieve program** (C++)
- Introduced **fast pre‑screening**: using the first $100$ small primes to estimate the number of "survivors"
- **Result**: Within $10^{14}$, **zero intervals entered the full sieve** $\rightarrow$ confirms no solution

---

## **Shift in Mathematical Approach**
- Abandoned exhaustive search and instead looked for:
  - **Centers of large prime gaps** (from the [Prime Gap List](https://primegap-list-project.github.io/))
  - **Near primorials** ($p\#$, divisible by many small primes)
  - **Near factorials** ($n!$, which contain long chains of composite numbers)

---

## **Breakthrough Using CRT + Admissible Tuples**
- Chose an **admissible $12$‑tuple**:  
  $H = [166, 278, 604, 724, 1096, 1256, 1306, 1492, 1514, 1564, 1574, 1712]$
- For the remaining $1992$ positions $j \in S$, assign a unique small prime $q_j$
- Solve the system of congruences:  
  \[
  N \equiv -j \pmod{q_j} \quad \forall j \in S
  \]
- Obtain a base solution $N_0$ and modulus $M$; then search for $k$ such that all $N = N_0 + kM + h$ are prime (for $h \in H$)

---

## **A Striking Success: Hit on the 10th Random Attempt**
- Sampled randomly near $N \sim 10^{72}$
- **The $10$th attempt hit the target**
- Obtained a candidate solution:  
  $N = 283\,652\,129\,125\,808\,400\,513\,278\,476\,301\,455\,085\,008\,845\,288\,816\,557\,395\,539\,337\,194\,639\,631\,785$ ($72$ digits)
- Our research story: [research story](https://www.bilibili.com/video/BV1hhZWBaEeX)

---

## **Moving Forward**
1. Verify the candidate solution and continue searching near it  
2. Analyze the data:  
   - Number of solutions, their density, distribution of gaps, comparison with theoretical expectations  
   - See details in  
     ![pic](imgs/solutions_analysis.png)  
     ![pic](imgs/solutions_cumulative.png)  
     ![pic](imgs/solutions_density.png)
3. [The proof of the solution](proof.gp)
```
? \r proof.gp
质数偏移量：[1, 89, 143, 349, 427, 443, 589, 743, 1099, 1111, 1241, 1723]
质数个数：12
```
---

## **Smallest Solution**
Still searching for the smallest $N$ with exactly $12$ primes in $[N, N+2003]$
- Current solution: $1006270103859193 < N \leq 55350776431902878$
- Thanks for Kaggle Notebooks!
- [Discussion](https://math.stackexchange.com/questions/5125120/on-the-smallest-n-with-exactly-12-primes-in-n-n2003) on Mathematics