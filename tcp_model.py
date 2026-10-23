"""
TCP Performance & Packet Loss Modeling Engine
Implements the Mathis et al. (1997) analytical throughput model and AIMD Congestion Window simulation.
"""

import math
import random
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np


def mathis_throughput(mss_bytes: int, rtt_ms: float, loss_fraction: float, link_mbps: float) -> float:
    """
    Computes estimated TCP Reno throughput using the Mathis formula:
        Throughput ~ (1.22 * MSS * 8) / (RTT * sqrt(p))
    
    Parameters:
        mss_bytes: Maximum Segment Size in bytes (typically 536 - 1460)
        rtt_ms: Round Trip Time in milliseconds (e.g. 10 - 500 ms)
        loss_fraction: Packet loss rate as decimal (e.g. 0.01 for 1%)
        link_mbps: Physical link capacity in Megabits per second
        
    Returns:
        Estimated throughput in Mbps, capped at link_mbps.
    """
    if loss_fraction <= 0.0:
        return float(link_mbps)
    
    rtt_sec = rtt_ms / 1000.0
    if rtt_sec <= 0:
        return float(link_mbps)
        
    # Mathis constant: C = sqrt(3/2) ~ 1.2247... (conventionally 1.22)
    # MSS in bits = mss_bytes * 8
    # Formula in bits per second:
    bps = (1.22 * (mss_bytes * 8)) / (rtt_sec * math.sqrt(loss_fraction))
    mbps = bps / 1_000_000.0
    
    return min(mbps, float(link_mbps))


def calculate_metrics(
    file_size_mb: float,
    mss_bytes: int,
    rtt_ms: float,
    loss_fraction: float,
    link_mbps: float
) -> Dict[str, Any]:
    """
    Calculates detailed metrics for a file transfer given network parameters.
    """
    throughput_mbps = mathis_throughput(mss_bytes, rtt_ms, loss_fraction, link_mbps)
    
    # File representation in bits and bytes (using decimal standard 1 MB = 10^6 bytes, as in document)
    file_bytes = file_size_mb * 1_000_000
    file_bits = file_bytes * 8
    
    # Transfer time in seconds
    if throughput_mbps > 0:
        transfer_time_sec = file_bits / (throughput_mbps * 1_000_000)
    else:
        transfer_time_sec = float('inf')
        
    # Packet counts
    total_packets = math.ceil(file_bytes / mss_bytes)
    
    # Expected retransmissions:
    # Under independent Bernoulli loss p, average attempts per packet = 1 / (1 - p).
    # Expected retransmissions = packets * p / (1 - p).
    if loss_fraction >= 1.0:
        expected_retransmissions = float('inf')
    else:
        expected_retransmissions = total_packets * (loss_fraction / (1.0 - loss_fraction))
        
    # Utilization percentage
    utilization_pct = (throughput_mbps / link_mbps) * 100.0 if link_mbps > 0 else 0.0
    
    # Extra data wasted due to retransmissions (in MB)
    wasted_mb = (expected_retransmissions * mss_bytes) / 1_000_000 if not math.isinf(expected_retransmissions) else 0.0

    return {
        "throughput_mbps": throughput_mbps,
        "link_mbps": link_mbps,
        "utilization_pct": utilization_pct,
        "transfer_time_sec": transfer_time_sec,
        "total_packets": total_packets,
        "expected_retransmissions": expected_retransmissions,
        "wasted_mb": wasted_mb,
        "file_size_mb": file_size_mb,
        "mss_bytes": mss_bytes,
        "rtt_ms": rtt_ms,
        "loss_fraction": loss_fraction,
        "loss_pct": loss_fraction * 100.0
    }


def simulate_cwnd(
    loss_fraction: float,
    rounds: int = 150,
    seed: int = 42,
    initial_cwnd: int = 10
) -> pd.DataFrame:
    """
    Simulates TCP Reno congestion window (AIMD) evolution over discrete RTT rounds.
    
    Rules:
    - In round i, window has cwnd packets.
    - Probability at least one packet is lost: P_loss = 1 - (1 - p)^cwnd
    - If loss occurs: cwnd = max(1, cwnd // 2) [Multiplicative Decrease]
    - Else: cwnd += 1 [Additive Increase]
    
    Returns:
        DataFrame with columns ['round', 'cwnd', 'loss_event', 'packets_sent']
    """
    random.seed(seed)
    np.random.seed(seed)
    
    cwnd = initial_cwnd
    records = []
    
    for r in range(1, rounds + 1):
        # Probability of at least one loss in this window
        p_window_loss = 1.0 - math.pow(1.0 - loss_fraction, cwnd)
        
        # Determine if loss occurred
        roll = random.random()
        loss_occurred = roll < p_window_loss
        
        records.append({
            "round": r,
            "cwnd": cwnd,
            "loss_event": loss_occurred,
            "packets_sent": cwnd
        })
        
        if loss_occurred:
            cwnd = max(1, cwnd // 2)
        else:
            cwnd = cwnd + 1
            
    return pd.DataFrame(records)


def generate_loss_curve(
    mss_bytes: int,
    rtt_ms: float,
    link_mbps: float,
    points: int = 200,
    max_loss: float = 0.05
) -> pd.DataFrame:
    """
    Generates throughput values across loss rates from 0.01% to max_loss% (e.g., 5%).
    Also includes 0.0% loss point.
    """
    losses = np.linspace(0.0001, max_loss, points)
    losses = np.insert(losses, 0, 0.0)
    
    results = []
    for p in losses:
        th = mathis_throughput(mss_bytes, rtt_ms, p, link_mbps)
        results.append({
            "loss_fraction": p,
            "loss_pct": p * 100.0,
            "throughput_mbps": th
        })
        
    return pd.DataFrame(results)


def generate_comparison_table(
    mss_bytes: int,
    rtt_ms: float,
    link_mbps: float,
    file_size_mb: float,
    loss_percentages: List[float] = [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 5.0]
) -> pd.DataFrame:
    """
    Generates the standard comparison table matching the reference study guide.
    """
    rows = []
    for loss_pct in loss_percentages:
        p = loss_pct / 100.0
        m = calculate_metrics(file_size_mb, mss_bytes, rtt_ms, p, link_mbps)
        
        th = m["throughput_mbps"]
        tt = m["transfer_time_sec"]
        retx = m["expected_retransmissions"]
        
        rows.append({
            "Packet Loss (%)": f"{loss_pct:.1f}%" if loss_pct > 0 else "0% (Ideal)",
            "Loss Rate (p)": p,
            "Throughput (Mbps)": round(th, 2),
            "Link Utilization": f"{m['utilization_pct']:.1f}%",
            "Transfer Time": f"{round(tt)} s" if tt < 120 else f"{tt/60.0:.1f} min ({round(tt)} s)",
            "Transfer Time (s)": round(tt, 1),
            "Expected Retransmissions": round(retx),
            "Wasted Data (MB)": round(m["wasted_mb"], 2)
        })
        
    return pd.DataFrame(rows)
