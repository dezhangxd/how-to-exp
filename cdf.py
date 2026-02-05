#!/usr/bin/env python3
# generated with the help of LLM. 
"""Read specified CSV and plot CDF of time (separated by solver curves)."""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Read CSV and plot CDF of solving time")
    parser.add_argument("csv", help="Path to input CSV file (must contain 'time' column)")
    parser.add_argument("-o", "--output", default="cdf.png", help="Output image path (default: cdf.png)")
    parser.add_argument("-c", "--cutoff", type=float, default=None, help="X-axis upper limit (time in seconds); use full range if not specified")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df.columns = df.columns.str.strip()  # Strip leading/trailing whitespace from column names
    # Ensure 'time' is numeric
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])

    # Set figure ratio: y-axis : x-axis = 4 : 3 (height : width)
    plt.figure(figsize=(6, 8))

    # Sort solvers by mean time; legend will follow this order; the mean is computed using all samples, independent of -c
    mean_time = df.groupby("solver")["time"].mean()
    solvers_ordered = mean_time.sort_values().index.tolist()

    markers = ["o", "s", "^", "D", "v", "p", "*", "X"]
    for i, solver in enumerate(solvers_ordered):
        times = df[df["solver"] == solver]["time"].sort_values().values
        n = len(times)
        # Number of instances in legend: if -c is given, strictly less than cutoff; otherwise, all
        n_legend = int((times < args.cutoff).sum()) if args.cutoff is not None else n
        avg = mean_time[solver]  # Average time of this solver over all samples
        # Legend: solver name + number of solved instances + average time (rounded to two decimals)
        label = f"{solver} ({n_legend}, {avg:.2f})"
        y = np.arange(1, n + 1)
        # Draw a marker at each solved instance (each data point)
        plt.step(
            times, y, where="post", label=label,
            marker=markers[i % len(markers)], markersize=5, markevery=1,
            markerfacecolor="none", markeredgewidth=1.5
        )

    # Both x and y axes start from 0; y-axis upper limit is 1.05 times the largest value, rounded up
    plt.xlim(0, args.cutoff if args.cutoff is not None else None)
    if args.cutoff is not None:
        max_y = df[df["time"] < args.cutoff].groupby("solver").size().max()
    else:
        max_y = df.groupby("solver").size().max()
    y_top = int(np.ceil(max_y * 1.05))
    plt.ylim(0, y_top)

    plt.xlabel("Time (s)")
    plt.ylabel("Number of instances solved")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    plt.show()

if __name__ == "__main__":
    main()
