"""
Unit tests validating Mathis model and TCP performance calculations against reference benchmarks.
"""

import unittest
import math
from tcp_model import mathis_throughput, calculate_metrics, simulate_cwnd, generate_comparison_table


class TestTCPModel(unittest.TestCase):
    def test_mathis_worked_example(self):
        """
        Validates page 2 worked example:
        MSS = 1460 bytes, RTT = 0.1s (100ms), p = 0.01 (1%), Link = 100 Mbps
        Formula: (1.22 * 1460 * 8) / (0.1 * sqrt(0.01)) = 14249.6 / 0.01 = 1,424,960 bps ~ 1.425 Mbps
        """
        th = mathis_throughput(mss_bytes=1460, rtt_ms=100, loss_fraction=0.01, link_mbps=100)
        self.assertAlmostEqual(th, 1.42496, places=2)
        
    def test_metrics_and_retransmissions(self):
        """
        Validates page 2 file transfer:
        100 MB file, MSS=1460, p=0.01 -> ~68,494 packets, ~692 retransmissions, ~561 seconds.
        """
        m = calculate_metrics(file_size_mb=100, mss_bytes=1460, rtt_ms=100, loss_fraction=0.01, link_mbps=100)
        self.assertEqual(m["total_packets"], 68494)
        self.assertAlmostEqual(m["expected_retransmissions"], 691.85, delta=1.0)
        self.assertAlmostEqual(m["transfer_time_sec"], 561.42, delta=2.0)
        self.assertAlmostEqual(m["utilization_pct"], 1.425, places=2)

    def test_zero_loss_cap(self):
        """
        Validates zero loss caps at link bandwidth.
        """
        th = mathis_throughput(mss_bytes=1460, rtt_ms=100, loss_fraction=0.0, link_mbps=100)
        self.assertEqual(th, 100.0)
        
        m = calculate_metrics(file_size_mb=100, mss_bytes=1460, rtt_ms=100, loss_fraction=0.0, link_mbps=100)
        self.assertEqual(m["transfer_time_sec"], 8.0)
        self.assertEqual(m["expected_retransmissions"], 0.0)

    def test_comparison_table_benchmarks(self):
        """
        Validates table from page 3:
        0%: 100 Mbps, 8s
        0.1%: ~4.51 Mbps, ~178s
        0.5%: ~2.02 Mbps, ~397s
        1.0%: ~1.43 Mbps, ~561s
        2.0%: ~1.01 Mbps, ~794s
        3.0%: ~0.82 Mbps, ~972s
        5.0%: ~0.64 Mbps, ~1255s
        """
        df = generate_comparison_table(mss_bytes=1460, rtt_ms=100, link_mbps=100, file_size_mb=100)
        
        expected_benchmarks = {
            0.0: (100.0, 8.0),
            0.001: (4.51, 178.0),
            0.005: (2.02, 397.0),
            0.01: (1.42, 561.0),
            0.02: (1.01, 794.0),
            0.03: (0.82, 972.0),
            0.05: (0.64, 1255.0),
        }
        
        for _, row in df.iterrows():
            p = row["Loss Rate (p)"]
            if p in expected_benchmarks:
                exp_th, exp_time = expected_benchmarks[p]
                self.assertAlmostEqual(row["Throughput (Mbps)"], exp_th, delta=0.05)
                self.assertAlmostEqual(row["Transfer Time (s)"], exp_time, delta=3.0)

    def test_cwnd_simulation_sawtooth(self):
        """
        Validates AIMD simulation characteristics:
        - Begins at initial cwnd = 10
        - cwnd halves on loss
        - cwnd increments by 1 on success
        """
        df = simulate_cwnd(loss_fraction=0.02, rounds=50, seed=42, initial_cwnd=10)
        self.assertEqual(len(df), 50)
        self.assertEqual(df.iloc[0]["cwnd"], 10)
        # cwnd must never drop below 1
        self.assertTrue((df["cwnd"] >= 1).all())


if __name__ == "__main__":
    unittest.main()
