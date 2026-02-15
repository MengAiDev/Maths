#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze solution files from local search (e.g., local_solutions.txt)
- Verify each solution
- Calculate gaps between solutions
- Generate statistical reports
- Visualize solution distribution
"""

import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from gmpy2 import mpz, is_prime
from collections import defaultdict
import matplotlib.patches as mpatches
from matplotlib.ticker import ScalarFormatter

# ===== Configuration =====
SOLUTION_FILE = "local_solutions.txt"
KNOWN_N = mpz("283652129125808400513278476301455085008845288816557395539337194639631785")
RADIUS = 10**9
WINDOW_LEN = 2004
TARGET = 12

# Set matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = [14, 8]
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

def parse_solutions(filename):
    """Parse all N values from file"""
    solutions = set()
    pattern = re.compile(r'N\s*=\s*(\d+)')
    try:
        with open(filename, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    solutions.add(mpz(match.group(1)))
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    sol_list = sorted(solutions)
    print(f"Read {len(sol_list)} unique solutions")
    return sol_list

def verify_solution(N):
    """Verify that [N, N+2003] contains exactly 12 primes"""
    count = 0
    for i in range(WINDOW_LEN):
        if is_prime(N + i):
            count += 1
            if count > TARGET:
                return False
    return count == TARGET

def plot_solutions_distribution(verified, KNOWN_N, RADIUS):
    """Plot solution distribution"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Convert to numerical values for plotting
    x_vals = [int(N - KNOWN_N) for N in verified]  # Offset from known solution
    
    # 1. Scatter plot of solutions
    ax1 = axes[0, 0]
    ax1.scatter(x_vals, range(len(x_vals)), c='blue', s=30, alpha=0.6, label='Solution positions')
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label=f'N₀ (known solution)')
    ax1.axvspan(-RADIUS, RADIUS, alpha=0.1, color='gray', label=f'Search radius ±{RADIUS:,}')
    ax1.set_xlabel(f'Offset from N₀')
    ax1.set_ylabel('Solution index')
    ax1.set_title(f'Solution Distribution (total {len(verified)} solutions)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Histogram of offsets
    ax2 = axes[0, 1]
    bins = min(50, len(set(x_vals)) // 2 + 1)
    counts, bins, patches = ax2.hist(x_vals, bins=bins, color='green', alpha=0.7, edgecolor='black')
    ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, label='N₀')
    ax2.set_xlabel(f'Offset from N₀')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Histogram of Solution Offsets')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Gap distribution
    ax3 = axes[1, 0]
    if len(verified) > 1:
        gaps = [verified[i] - verified[i-1] for i in range(1, len(verified))]
        gaps_vals = [int(gap) for gap in gaps]
        
        # Gap sequence
        ax3.plot(range(1, len(gaps)+1), gaps_vals, 'o-', color='purple', alpha=0.6, markersize=4)
        ax3.axhline(y=np.mean(gaps_vals), color='red', linestyle='--', 
                   label=f'Mean gap: {np.mean(gaps_vals):.2e}')
        ax3.set_xlabel('Gap index')
        ax3.set_ylabel('Gap size')
        ax3.set_title('Consecutive Solution Gaps')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')
    
    # 4. Histogram of gaps
    ax4 = axes[1, 1]
    if len(verified) > 1:
        gaps_vals = [int(verified[i] - verified[i-1]) for i in range(1, len(verified))]
        bins_gaps = min(30, len(set(gaps_vals)) // 2 + 1)
        ax4.hist(gaps_vals, bins=bins_gaps, color='orange', alpha=0.7, edgecolor='black')
        ax4.axvline(x=np.mean(gaps_vals), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(gaps_vals):.2e}')
        ax4.axvline(x=np.median(gaps_vals), color='blue', linestyle='--', 
                   label=f'Median: {np.median(gaps_vals):.2e}')
        ax4.set_xlabel('Gap size')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Histogram of Gaps')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        if max(gaps_vals) / min(gaps_vals) > 100:
            ax4.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('solutions_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig

def plot_cumulative_distribution(verified, KNOWN_N, RADIUS):
    """Plot cumulative distribution"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_vals = sorted([int(N - KNOWN_N) for N in verified])
    
    # Cumulative distribution
    ax.step(x_vals, range(1, len(x_vals)+1), where='post', linewidth=2, color='darkblue')
    ax.fill_between(x_vals, range(1, len(x_vals)+1), step='post', alpha=0.3)
    
    # Theoretical uniform distribution
    if len(x_vals) > 1:
        x_uniform = np.linspace(-RADIUS, RADIUS, 100)
        y_uniform = len(x_vals) * (x_uniform + RADIUS) / (2 * RADIUS)
        ax.plot(x_uniform, y_uniform, '--', color='red', alpha=0.7, 
               label='Theoretical uniform distribution')
    
    ax.axvline(x=0, color='green', linestyle='--', linewidth=2, label='N₀')
    ax.set_xlabel(f'Offset from N₀')
    ax.set_ylabel('Cumulative solution count')
    ax.set_title('Cumulative Distribution Function')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('solutions_cumulative.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_density_comparison(verified, KNOWN_N, RADIUS):
    """Plot density comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    x_vals = [int(N - KNOWN_N) for N in verified]
    
    # Left: KDE density estimation
    from scipy import stats
    if len(x_vals) > 3:
        kde = stats.gaussian_kde(x_vals, bw_method='scott')
        x_range = np.linspace(-RADIUS, RADIUS, 500)
        density = kde(x_range)
        
        ax1.plot(x_range, density, 'b-', linewidth=2, label='KDE density estimation')
        ax1.fill_between(x_range, density, alpha=0.3, color='blue')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='N₀')
        ax1.axhline(y=1/(2*RADIUS), color='green', linestyle=':', 
                   label=f'Theoretical mean density: {1/(2*RADIUS):.2e}')
        ax1.set_xlabel(f'Offset from N₀')
        ax1.set_ylabel('Probability density')
        ax1.set_title('Kernel Density Estimation')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # Right: QQ plot vs uniform distribution
    if len(x_vals) > 3:
        # Normalize to [0,1]
        normalized = [(x + RADIUS) / (2 * RADIUS) for x in x_vals]
        theoretical = np.linspace(0, 1, len(normalized))
        
        ax2.scatter(theoretical, sorted(normalized), alpha=0.6, s=30)
        ax2.plot([0, 1], [0, 1], 'r--', linewidth=2, label='Theoretical uniform')
        ax2.set_xlabel('Theoretical quantiles (uniform)')
        ax2.set_ylabel('Sample quantiles')
        ax2.set_title('QQ Plot: Solutions vs Uniform Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('solutions_density.png', dpi=150, bbox_inches='tight')
    plt.show()

def analyze():
    print("Analyzing solution file...")
    solutions = parse_solutions(SOLUTION_FILE)
    if not solutions:
        return

    # Filter solutions within [N0 - R, N0 + R]
    low_bound = KNOWN_N - RADIUS
    high_bound = KNOWN_N + RADIUS
    valid_sols = [N for N in solutions if low_bound <= N <= high_bound]
    print(f"Found {len(valid_sols)} solutions within [{KNOWN_N - RADIUS}, {KNOWN_N + RADIUS}]")

    # Verify solutions
    verified = []
    for i, N in enumerate(valid_sols):
        print(f"  Verifying {i+1}/{len(valid_sols)}: N ~ 1e{len(str(N))-1}", end='\r')
        if verify_solution(N):
            verified.append(N)
    print(f"\nSuccessfully verified {len(verified)} / {len(valid_sols)} solutions")

    if not verified:
        print("No verified solutions found, cannot generate visualizations")
        return

    # Calculate gaps
    gaps = []
    for i in range(1, len(verified)):
        gap = verified[i] - verified[i-1]
        gaps.append(gap)

    # Statistics
    min_gap = min(gaps) if gaps else 0
    max_gap = max(gaps) if gaps else 0
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # Print report
    print("\n" + "="*60)
    print("Solution Distribution Analysis Report")
    print("="*60)
    print(f"Known center solution N₀ = {KNOWN_N}")
    print(f"Search radius      = ±{RADIUS:,}")
    print(f"Number of solutions = {len(verified)}")
    print(f"Solution density    = {len(verified) / (2 * RADIUS):.2e} per integer")
    if gaps:
        print(f"Minimum gap        = {min_gap}")
        print(f"Maximum gap        = {max_gap}")
        print(f"Mean gap           = {avg_gap:.2e}")
        print(f"Median gap         = {sorted([int(g) for g in gaps])[len(gaps)//2]:,}")
    print(f"First solution      = {verified[0]}")
    print(f"Last solution       = {verified[-1]}")

    # Check if original solution is included
    if KNOWN_N in verified:
        print("Original solution N₀ is included in the results")
    else:
        print("Original solution N₀ is not in the verified set")

    # Save verified solutions
    with open("verified_solutions.txt", "w") as f:
        for N in verified:
            f.write(f"N={N}\n")
    print(f"\nSaved {len(verified)} verified solutions to verified_solutions.txt")

    # Generate visualizations
    print("\nGenerating visualizations...")
    
    try:
        # 1. Basic distribution plots
        plot_solutions_distribution(verified, KNOWN_N, RADIUS)
        print("   Generated solutions_analysis.png")
        
        # 2. Cumulative distribution
        if len(verified) > 1:
            plot_cumulative_distribution(verified, KNOWN_N, RADIUS)
            print("   Generated solutions_cumulative.png")
        
        # 3. Density comparison
        if len(verified) > 3:
            plot_density_comparison(verified, KNOWN_N, RADIUS)
            print("   Generated solutions_density.png")
        
        print("\nAll plots saved to current directory")
        
    except ImportError as e:
        print(f"Cannot generate visualizations: {e}")
        print("Please install required packages: pip install matplotlib numpy scipy")
    except Exception as e:
        print(f"Error generating plots: {e}")

if __name__ == "__main__":
    analyze()