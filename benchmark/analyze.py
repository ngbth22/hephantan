"""
analyze.py - Phan tich thong ke va ve 6 bieu do so sanh tu file CSV benchmark.
"""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import ALGORITHMS, SIZE_LABELS, SIZES


def load_and_validate(csv_path: str) -> pd.DataFrame:
    """Doc va kiem tra tinh hop le cua file ket qua CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Khong tim thay file ket qua: {csv_path}")
    df = pd.read_csv(csv_path, keep_default_na=False)
    # Chuyen cot success ve kieu boolean chuan
    df["success"] = df["success"].astype(str).str.strip().str.lower() == "true"
    print(f"[*] Da doc {len(df)} dong du lieu tu {csv_path}")
    return df


def compute_statistics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Tinh toan thong ke theo yeu cau:
    - success_rate = successful / total theo tung to hop (ke ca fail)
    - Mean/Median/Min/Max/Std chi tinh tren cac luot co success == True
    """
    # Tinh ti le thanh cong cho moi to hop
    rate_records = []
    for algo in ALGORITHMS:
        for sz in SIZES:
            sub = df[(df["algorithm"] == algo) & (df["size_bytes"] == sz)]
            tot = len(sub)
            succ = sub["success"].sum() if tot > 0 else 0
            rate = (succ / tot * 100.0) if tot > 0 else 0.0
            rate_records.append({
                "algorithm": algo,
                "size_bytes": sz,
                "size_label": SIZE_LABELS.get(sz, f"{sz}B"),
                "total_runs": tot,
                "success_runs": succ,
                "success_rate_pct": round(rate, 2),
            })
    df_rates = pd.DataFrame(rate_records)

    # Loc chi lay cac luot thanh cong cho thong ke thoi gian
    df_valid = df[df["success"] == True].copy()

    metrics = [
        "encryption_ms",
        "decrypt_ms",
        "verify_ms",
        "rtt_ms",
        "total_ms",
        "throughput_kbps",
        "enc_cpu_pct",
        "dec_cpu_pct",
        "enc_ram_mb",
        "dec_ram_mb",
        "enc_ram_delta_kb",
        "dec_ram_delta_kb",
    ]
    stat_records = []

    for algo in ALGORITHMS:
        for sz in SIZES:
            sub = df_valid[(df_valid["algorithm"] == algo) & (df_valid["size_bytes"] == sz)]
            if len(sub) == 0:
                continue

            rec = {
                "algorithm": algo,
                "size_bytes": sz,
                "size_label": SIZE_LABELS.get(sz, f"{sz}B"),
                "valid_samples": len(sub),
                "ciphertext_size_bytes": int(sub["ciphertext_size_bytes"].iloc[0]),
                "packet_size_bytes": int(sub["packet_size_bytes"].iloc[0]),
            }

            for m in metrics:
                desc = sub[m].describe()
                med = sub[m].median()
                rec[f"{m}_mean"] = round(float(desc["mean"]), 3)
                rec[f"{m}_std"] = round(float(desc["std"]), 3)
                rec[f"{m}_min"] = round(float(desc["min"]), 3)
                rec[f"{m}_max"] = round(float(desc["max"]), 3)
                rec[f"{m}_median"] = round(float(med), 3)

            stat_records.append(rec)

    df_stats = pd.DataFrame(stat_records)
    return df_rates, df_stats


def generate_charts(df_stats: pd.DataFrame, charts_dir: str) -> list[str]:
    """
    Ve 6 bieu do so sanh voi truc X = Algorithm, nhom theo Size (1 KB / 100 KB / 1 MB):
    1. Encryption Time (ms)
    2. Decryption Time (ms)
    3. RTT (ms)
    4. Total Time (ms)
    5. Packet & Ciphertext Size (Bytes)
    6. Throughput (KB/s)
    """
    os.makedirs(charts_dir, exist_ok=True)
    generated_files = []

    # Thiet lap phong cach ve
    plt.rcParams.update({
        "font.sans-serif": "DejaVu Sans",
        "font.size": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })

    colors = ["#2b5c8f", "#d95f02", "#7570b3"]  # 1KB, 100KB, 1MB
    bar_width = 0.25
    x = np.arange(len(ALGORITHMS))

    # Helper de lay du lieu theo metric
    def get_data_for_metric(metric_name: str, stat_type: str = "mean") -> dict[int, list[float]]:
        data = {}
        for sz in SIZES:
            vals = []
            for algo in ALGORITHMS:
                row = df_stats[(df_stats["algorithm"] == algo) & (df_stats["size_bytes"] == sz)]
                if len(row) > 0:
                    val = row[f"{metric_name}_{stat_type}"].iloc[0]
                    vals.append(val)
                else:
                    vals.append(0.0)
            data[sz] = vals
        return data

    chart_configs = [
        (
            "01_encryption_time.png",
            "1. Thoi gian Ma hoa trung binh (Encryption Time)",
            "encryption_ms",
            "Thoi gian (ms)",
            True,  # Dung log scale neu chenh lech lon
        ),
        (
            "02_decryption_time.png",
            "2. Thoi gian Giai ma trung binh (Decryption Time)",
            "decrypt_ms",
            "Thoi gian (ms)",
            True,
        ),
        (
            "03_rtt.png",
            "3. Thoi gian truyen mang RTT (Round Trip Time)",
            "rtt_ms",
            "Thoi gian RTT (ms)",
            True,
        ),
        (
            "04_total_time.png",
            "4. Tong thoi gian thuc thi (Total Time = Encrypt + RTT)",
            "total_ms",
            "Tong thoi gian (ms)",
            True,
        ),
        (
            "06_throughput.png",
            "6. Bang thong truyen tai he thong (Throughput)",
            "throughput_kbps",
            "Bang thong (KB/s)",
            False,
        ),
    ]

    for filename, title, metric, y_label, use_log in chart_configs:
        fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=300)
        data = get_data_for_metric(metric, "mean")

        for idx, sz in enumerate(SIZES):
            offset = (idx - 1) * bar_width
            bars = ax.bar(
                x + offset,
                data[sz],
                width=bar_width,
                label=SIZE_LABELS[sz],
                color=colors[idx],
                edgecolor="black",
                linewidth=0.6,
            )
            # Ghi gia tri tren dau cot
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    val_str = f"{height:.2f}" if height < 100 else f"{height:.1f}"
                    ax.annotate(
                        val_str,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=7.5,
                        rotation=0 if height < 1000 else 30,
                    )

        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel("Thuat toan (Algorithm)", fontweight="bold", labelpad=8)
        ax.set_ylabel(y_label, fontweight="bold", labelpad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(ALGORITHMS, fontweight="bold")
        ax.legend(title="Kich thuoc du lieu", frameon=True)
        if use_log:
            # Thu kiem tra neu co gia tri chenh lech hang tram lan
            all_vals = [v for vals in data.values() for v in vals if v > 0]
            if len(all_vals) > 0 and (max(all_vals) / min(all_vals)) > 50:
                ax.set_yscale("log")
                ax.set_ylabel(f"{y_label} (Log Scale)")

        fig.tight_layout()
        out_file = os.path.join(charts_dir, filename)
        fig.savefig(out_file)
        plt.close(fig)
        generated_files.append(out_file)
        print(f"[+] Da tao bieu do: {out_file}")

    # Bieu do 5: Packet & Ciphertext Size
    fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=300)
    for idx, sz in enumerate(SIZES):
        offset = (idx - 1) * bar_width
        vals = []
        for algo in ALGORITHMS:
            row = df_stats[(df_stats["algorithm"] == algo) & (df_stats["size_bytes"] == sz)]
            vals.append(row["packet_size_bytes"].iloc[0] if len(row) > 0 else 0)

        bars = ax.bar(
            x + offset,
            vals,
            width=bar_width,
            label=SIZE_LABELS[sz],
            color=colors[idx],
            edgecolor="black",
            linewidth=0.6,
        )
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{height:,}B",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    rotation=30,
                )

    ax.set_title("5. Kich thuoc goi tin truyen tren mang (Packet Size Bytes)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Thuat toan (Algorithm)", fontweight="bold", labelpad=8)
    ax.set_ylabel("Kich thuoc Packet (Bytes - Log Scale)", fontweight="bold", labelpad=8)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(ALGORITHMS, fontweight="bold")
    ax.legend(title="Kich thuoc Plaintext", frameon=True)

    fig.tight_layout()
    out_file5 = os.path.join(charts_dir, "05_sizes.png")
    fig.savefig(out_file5)
    plt.close(fig)
    generated_files.append(out_file5)
    print(f"[+] Da tao bieu do: {out_file5}")

    # Bieu do 7: CPU Usage (Sender vs Receiver)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    for ax, metric, title_sub in [
        (ax1, "enc_cpu_pct", "Sender - Khi Ma hoa (Encryption)"),
        (ax2, "dec_cpu_pct", "Receiver - Khi Giai ma (Decryption)"),
    ]:
        data = get_data_for_metric(metric, "mean")
        for idx, sz in enumerate(SIZES):
            offset = (idx - 1) * bar_width
            bars = ax.bar(
                x + offset,
                data[sz],
                width=bar_width,
                label=SIZE_LABELS[sz],
                color=colors[idx],
                edgecolor="black",
                linewidth=0.6,
            )
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(
                        f"{height:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=7,
                    )
        ax.set_title(title_sub, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Thuat toan (Algorithm)", fontweight="bold", labelpad=8)
        ax.set_ylabel("CPU Utilization (%)", fontweight="bold", labelpad=8)
        ax.set_ylim(0, 105)
        ax.set_xticks(x)
        ax.set_xticklabels(ALGORITHMS, fontweight="bold")
        ax.legend(title="Kich thuoc du lieu", frameon=True)

    fig.suptitle("7. Muc do Su dung CPU (CPU Utilization %)", fontsize=13, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_file7 = os.path.join(charts_dir, "07_cpu_usage.png")
    fig.savefig(out_file7)
    plt.close(fig)
    generated_files.append(out_file7)
    print(f"[+] Da tao bieu do: {out_file7}")

    # Bieu do 8: RAM Usage (Process RSS and Delta for Sender & Receiver)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 9), dpi=300)
    ram_configs = [
        (ax1, "enc_ram_mb", "Sender Process RSS (MB)", "RAM RSS (MB)", False),
        (ax2, "dec_ram_mb", "Receiver Process RSS (MB)", "RAM RSS (MB)", False),
        (ax3, "enc_ram_delta_kb", "Sender Memory Delta (KB)", "Delta RAM (KB)", True),
        (ax4, "dec_ram_delta_kb", "Receiver Memory Delta (KB)", "Delta RAM (KB)", True),
    ]
    for ax, metric, title_sub, y_label, check_log in ram_configs:
        data = get_data_for_metric(metric, "mean")
        for idx, sz in enumerate(SIZES):
            offset = (idx - 1) * bar_width
            bars = ax.bar(
                x + offset,
                data[sz],
                width=bar_width,
                label=SIZE_LABELS[sz],
                color=colors[idx],
                edgecolor="black",
                linewidth=0.6,
            )
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    val_str = f"{height:.1f}M" if "MB" in y_label else f"{height:.0f}K"
                    ax.annotate(
                        val_str,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=7,
                    )
        ax.set_title(title_sub, fontsize=10, fontweight="bold", pad=8)
        ax.set_xlabel("Thuat toan (Algorithm)", fontweight="bold", labelpad=6)
        ax.set_ylabel(y_label, fontweight="bold", labelpad=6)
        ax.set_xticks(x)
        ax.set_xticklabels(ALGORITHMS, fontweight="bold")
        ax.legend(title="Kich thuoc du lieu", frameon=True, fontsize=8)
        if check_log:
            all_vals = [v for vals in data.values() for v in vals if v > 0]
            if len(all_vals) > 0 and (max(all_vals) / min(all_vals)) > 50:
                ax.set_yscale("log")
                ax.set_ylabel(f"{y_label} (Log Scale)")

    fig.suptitle("8. Muc do Tieu thu Bo nho RAM (Memory RSS & Allocation Delta)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_file8 = os.path.join(charts_dir, "08_ram_usage.png")
    fig.savefig(out_file8)
    plt.close(fig)
    generated_files.append(out_file8)
    print(f"[+] Da tao bieu do: {out_file8}")

    return generated_files


def export_markdown_summary(df_rates: pd.DataFrame, df_stats: pd.DataFrame, output_md: str) -> str:
    """Xuat bang tong hop ket qua ra Markdown."""
    lines = [
        "# Bang Tong hop Ket qua Benchmark Ma hoa Mang",
        "",
        "## 1. Ti le thanh cong (Success Rate)",
        "",
        "| Thuat toan | Kich thuoc | Tong so luot | Thanh cong | Ti le (%) |",
        "|---|---|---:|---:|---:|",
    ]
    for _, row in df_rates.iterrows():
        lines.append(
            f"| {row['algorithm']} | {row['size_label']} | {row['total_runs']} | "
            f"{row['success_runs']} | {row['success_rate_pct']:.1f}% |"
        )

    lines.extend([
        "",
        "## 2. Chi tiet cac chi so thoi gian va bang thong (Chi tinh tren luot thanh cong)",
        "",
        "| Thuat toan | Size | Ciphertext (B) | Packet (B) | Encrypt Mean (ms) | Decrypt Mean (ms) | RTT Mean (ms) | Total Mean (ms) | Total Median (ms) | Throughput (KB/s) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])

    for _, row in df_stats.iterrows():
        lines.append(
            f"| {row['algorithm']} | {row['size_label']} | {row['ciphertext_size_bytes']:,} | "
            f"{row['packet_size_bytes']:,} | {row['encryption_ms_mean']:.2f} | "
            f"{row['decrypt_ms_mean']:.2f} | {row['rtt_ms_mean']:.2f} | "
            f"{row['total_ms_mean']:.2f} | {row['total_ms_median']:.2f} | "
            f"{row['throughput_kbps_mean']:.1f} |"
        )

    lines.extend([
        "",
        "## 3. Chi tiet muc su dung CPU va RAM (Chi tinh tren luot thanh cong)",
        "",
        "| Thuat toan | Size | Sender CPU (%) | Receiver CPU (%) | Sender RAM (MB) | Receiver RAM (MB) | Sender Delta (KB) | Receiver Delta (KB) |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])

    for _, row in df_stats.iterrows():
        lines.append(
            f"| {row['algorithm']} | {row['size_label']} | {row['enc_cpu_pct_mean']:.1f}% | "
            f"{row['dec_cpu_pct_mean']:.1f}% | {row['enc_ram_mb_mean']:.1f} MB | "
            f"{row['dec_ram_mb_mean']:.1f} MB | {row['enc_ram_delta_kb_mean']:.1f} KB | "
            f"{row['dec_ram_delta_kb_mean']:.1f} KB |"
        )

    content = "\n".join(lines)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Da xuat bang Markdown: {output_md}")
    return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Data Analysis and Charting")
    parser.add_argument(
        "--csv",
        default="benchmark/results/benchmark_results.csv",
        help="Duong dan file CSV ket qua",
    )
    parser.add_argument(
        "--charts-dir",
        default="benchmark/results/charts",
        help="Thu muc luu bieu do",
    )
    parser.add_argument(
        "--summary-md",
        default="benchmark/results/summary_table.md",
        help="Duong dan xuat bang tom tat Markdown",
    )
    args = parser.parse_args()

    df = load_and_validate(args.csv)
    df_rates, df_stats = compute_statistics(df)
    df_stats.to_csv(os.path.join(os.path.dirname(args.csv), "detailed_statistics.csv"), index=False)
    generate_charts(df_stats, args.charts_dir)
    export_markdown_summary(df_rates, df_stats, args.summary_md)
