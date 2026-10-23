# TCP Performance on Packet Loss Simulator 🚀

An interactive analytical simulator and educational presentation suite demonstrating how packet loss impacts TCP Reno throughput and congestion window dynamics.

Developed based on the landmark **Mathis Analytical Model** (*ACM SIGCOMM Computer Communication Review, 1997*) and discrete **AIMD Congestion Control** principles.

---

## 🌟 Key Highlights & Features

- **Mathis Analytical Engine:** Real-time calculation of TCP Reno throughput upper-bound:  
  $$\text{Throughput} \approx \min\left(\frac{1.22 \times \text{MSS} \times 8}{\text{RTT} \times \sqrt{p}}, \text{Link Bandwidth}\right)$$
- **Discrete-Event AIMD CWND Simulation:** Simulates TCP congestion window evolution over RTT rounds with true Additive Increase (+1 MSS) and Multiplicative Decrease (halving on loss $1 - (1-p)^{cwnd}$).
- **Interactive Plotly Visualizations:**
  - $1/\sqrt{p}$ Throughput vs. Loss steep decay curve with dynamic operating point marker.
  - Realistic Congestion Window Sawtooth graph highlighting packet loss drop events.
- **Dynamic File Transfer Metrics:** Calculates transfer time, link efficiency, total packet counts, and probability-based expected retransmissions $\frac{p}{1-p}$.
- **Loss Comparison Benchmark Table:** Instant benchmark across $0\%, 0.1\%, 0.5\%, 1.0\%, 2.0\%, 3.0\%, 5.0\%$ loss rates with 1-click **CSV Export**.
- **1-Click Demo Presets:** Pre-configured scenarios including *"The 0.1% Shock"*, *"Satellite Link"*, *"Data Center LAN"*, and *"Flaky Mobile Link"*.
- **Comprehensive Viva & Faculty Defense Suite:** Built-in 2-minute speaking script, five core definitions, and detailed answers to top faculty viva questions.
- **Modern TCP Comparison:** Insightful analysis comparing classical TCP Reno with **TCP CUBIC** and Google's **BBR**.

---

## 📂 Project Directory Structure

```
CNproject/
├── app.py                   # Streamlit web application & interactive UI
├── tcp_model.py             # Core mathematical formulas & simulation engine
├── test_tcp_model.py        # Automated test suite (100% benchmark validation)
├── requirements.txt         # Project dependencies
├── run.bat                  # 1-click Windows launcher (Batch)
├── run.ps1                  # 1-click Windows PowerShell launcher
├── presentation_guide.md    # Full viva script, Q&A, and study guide
└── README.md                # Project documentation
```

---

## 🚀 Quick Start (Running Locally)

### Option 1: Double-Click Launcher (Windows)
Simply double-click [`run.bat`](file:///c:/Users/anike/Desktop/CNproject/run.bat).

### Option 2: Command Line / PowerShell
1. Open PowerShell or Terminal in the project folder:
   ```powershell
   cd c:\Users\anike\Desktop\CNproject
   ```

2. Run the Streamlit application:
   ```powershell
   python -m streamlit run app.py
   ```
3. Open your browser at the displayed URL (typically `http://localhost:8501`).

---

## 🧪 Running the Verification Test Suite

Verify all mathematical calculations and reference benchmarks by running:
```powershell
python -m unittest test_tcp_model.py
```

All 5 unit tests validate:
- Page 2 worked example ($\text{MSS}=1460$, $\text{RTT}=100\text{ms}$, $p=0.01 \implies 1.425\text{ Mbps}$, $692\text{ retransmissions}$, $561\text{ s}$).
- Link capacity bounding & zero loss handling.
- AIMD sawtooth window constraints.
- Full 7-point benchmark table values.

---

## 📊 Core Mathematical Reference

### 1. Mathis Formula (1997)
$$\text{Throughput} \approx \frac{1.22 \times \text{MSS} \times 8}{\text{RTT} \times \sqrt{p}}$$
- $\text{MSS} \times 8$: Bits per packet.
- Dividing by $\text{RTT}$: Normalizes transfer to rate per second.
- Dividing by $\sqrt{p}$: Loss penalty derived from the triangular geometry of the AIMD window.
- $1.22 \approx \sqrt{1.5}$: Constant factor from the average window height $\sqrt{3/2}$.

### 2. Expected Retransmissions
$$\mathbb{E}[\text{Retransmissions}] = N \times \frac{p}{1 - p}$$
Where $N = \lceil \frac{\text{File Size}}{\text{MSS}} \rceil$ is total packets.

---

## 👨‍🏫 3-Step Demo for Faculty Presentation

1. **Step 1: Baseline Test**
   - Set Loss = $1.0\%$, RTT = $100\text{ ms}$, Link = $100\text{ Mbps}$, File = $100\text{ MB}$.
   - **Point out:** The connection only achieves **$1.43\text{ Mbps}$** ($1.4\%$ link utilization), requiring **$9.4\text{ minutes}$** to transfer.
2. **Step 2: The 0.1% Shock**
   - Lower Loss to **$0.1\%$**.
   - **Point out:** Throughput jumps to **$4.51\text{ Mbps}$**, and transfer time drops to **$3\text{ minutes}$**. This visibly proves the steep $1/\sqrt{p}$ decay curve.
3. **Step 3: RTT Sensitivity**
   - Change RTT from $100\text{ ms}$ to $200\text{ ms}$.
   - **Point out:** Throughput halves from $4.51\text{ Mbps}$ to $2.25\text{ Mbps}$, confirming that throughput is strictly inversely proportional to latency ($1/\text{RTT}$).

---

## 📜 References & Citations
- **Mathis, M., Semke, J., Mahdavi, J., & Ott, T. (1997).** *The Macroscopic Behavior of the TCP Congestion Avoiding Algorithm.* ACM SIGCOMM Computer Communication Review, 27(3), 67-82.
- **Chiu, D. M., & Jain, R. (1989).** *Analysis of the Increase and Decrease Algorithms for Congestion Avoidance in Computer Networks.* Computer Networks and ISDN Systems, 17(1), 1-14.
- **RFC 5681:** *TCP Congestion Control (Allman, Paxson, Blanton).*
- **RFC 6928:** *Increasing TCP's Initial Window (Chu, Dukkipati, Cheng, Mathis).*
