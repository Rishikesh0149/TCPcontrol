# TCP Performance on Packet Loss — Study & Presentation Guide

> **Project Title:** TCP Performance on Packet Loss Simulator  
> **Course:** Computer Networks  
> **Framework:** Python, Streamlit, Plotly, Pandas, NumPy  

---

## 1. The Idea in One Line

> *"When a network drops packets, TCP slows itself down. My program shows how much it slows down for different network conditions."*

**The Intuitive Analogy:**  
TCP is like a driver on an open highway. When it sees an accident (packet loss), it brakes hard. The more accidents (higher loss rate $p$) or the longer the road (higher Round Trip Time RTT), the lower the average cruising speed.

---

## 2. Background: The Five Core Terms

| Term | Symbol / Unit | Meaning |
| :--- | :---: | :--- |
| **TCP** | — | **Reliable transport protocol.** Guarantees ordered delivery; lost packets are detected and retransmitted. |
| **Packet Loss** | $p$ (%) | **Fraction of packets that fail to arrive.** $1\%$ loss means 1 out of every 100 packets is dropped. |
| **Round Trip Time** | $\text{RTT}$ (ms) | **Round-trip latency.** Time taken for a packet to reach the receiver plus the acknowledgment (ACK) to return. |
| **Maximum Segment Size** | $\text{MSS}$ (Bytes) | **Maximum payload per TCP packet.** Standard Ethernet MTU (1500 B) minus 40 B headers = 1460 Bytes. |
| **Congestion Window** | $cwnd$ (Packets) | **Sender-side buffer limit.** The maximum number of packets TCP may inject into the network without waiting for ACKs. |

### How TCP Reacts to Loss: AIMD
TCP Reno uses **Additive Increase / Multiplicative Decrease (AIMD)**:
- **Additive Increase (AI):** For every RTT where all packets are successfully ACKed, $cwnd$ increases by **$+1\text{ MSS}$**.
- **Multiplicative Decrease (MD):** The moment a packet is lost, $cwnd$ is cut **in half** ($\frac{1}{2} cwnd$).
- This produces the classic, famous **sawtooth pattern**.

---

## 3. The Core Mathematical Model (Mathis Formula)

In 1997, Matthew Mathis, Jeffrey Semke, Jamshid Mahdavi, and Teunis Ott published:  
*“The Macroscopic Behavior of the TCP Congestion Avoiding Algorithm” (ACM SIGCOMM CCR)*.

$$\text{Throughput} \approx \frac{1.22 \times \text{MSS} \times 8}{\text{RTT} \times \sqrt{p}}$$

### Formula Breakdown:
1. **$\text{MSS} \times 8$**: Converts payload bytes to bits.
2. **Dividing by $\text{RTT}$**: Gives transmission rate if 1 packet were sent per round trip.
3. **Dividing by $\sqrt{p}$**: The packet loss penalty factor (more loss $\implies$ lower speed).
4. **$1.22 \approx \sqrt{1.5}$**: Geometric constant derived from the area under AIMD sawtooth cycles.
5. **Physical Cap**: Throughput is bounded by the physical link: $\min(\text{Estimate}, \text{Link Bandwidth})$.

### Worked Benchmark Example:
- $\text{MSS} = 1460\text{ bytes}$
- $\text{RTT} = 0.1\text{ s } (100\text{ ms})$
- $p = 0.01\text{ } (1\%)$
- $\text{Physical Link} = 100\text{ Mbps}$

$$\text{Numerator} = 1.22 \times 1460 \times 8 = 14,249.6\text{ bits}$$
$$\text{Denominator} = 0.1 \times \sqrt{0.01} = 0.1 \times 0.1 = 0.01\text{ s}$$
$$\text{Throughput} = \frac{14,249.6}{0.01} = 1,424,960\text{ bps} \approx \mathbf{1.425\text{ Mbps}}$$

> **Takeaway:** Even though the link is $100\text{ Mbps}$, TCP achieves only **1.425%** of physical capacity. The loss throttles the speed, not the wire!

---

## 4. Transfer Time & Retransmission Probability

For a file of size $S_{\text{MB}}$:
- **$\text{File Bits} = S_{\text{MB}} \times 10^6 \times 8$**
- **$\text{Transfer Time} = \frac{\text{File Bits}}{\text{Throughput (bps)}}$**
- **$\text{Total Packets } N = \lceil \frac{S_{\text{Bytes}}}{\text{MSS}} \rceil$**
- **$\text{Expected Retransmissions} = N \times \frac{p}{1 - p}$**

*Why $\frac{p}{1-p}$?*  
Under independent Bernoulli packet loss $p$, the number of attempts until success follows a geometric distribution. The expected number of failed attempts per packet is $\frac{1}{1-p} - 1 = \frac{p}{1-p}$.  
For a 100 MB transfer with MSS=1460 B and $p=0.01$:
$$N = 68,494\text{ packets}$$
$$R = 68,494 \times \frac{0.01}{0.99} \approx \mathbf{692\text{ retransmissions}}$$

---

## 5. Benchmark Comparison Table

Evaluated with standard baseline: **$\text{MSS} = 1460\text{ B}$, $\text{RTT} = 100\text{ ms}$, $\text{Link} = 100\text{ Mbps}$, $\text{File} = 100\text{ MB}$**:

| Packet Loss ($p$) | TCP Throughput | Physical Link Utilization | Transfer Time | Expected Retransmissions |
| :---: | :---: | :---: | :---: | :---: |
| **0% (Ideal)** | **100 Mbps** | 100.0% | **8 seconds** | 0 pkts |
| **0.1%** | **~4.51 Mbps** | 4.5% | **~178 seconds (~3 min)** | 69 pkts |
| **0.5%** | **~2.02 Mbps** | 2.0% | **~397 seconds (~6.6 min)** | 344 pkts |
| **1.0%** | **~1.43 Mbps** | 1.4% | **~561 seconds (~9.4 min)** | 692 pkts |
| **2.0%** | **~1.01 Mbps** | 1.0% | **~794 seconds (~13.2 min)** | 1,398 pkts |
| **3.0%** | **~0.82 Mbps** | 0.8% | **~972 seconds (~16.2 min)** | 2,118 pkts |
| **5.0%** | **~0.64 Mbps** | 0.6% | **~1,255 seconds (~20.9 min)** | 3,605 pkts |

> [!IMPORTANT]
> **Key point for presentation:** Introducing merely **0.1% packet loss** collapses throughput by **95.5%** (from 100 Mbps to 4.5 Mbps), slowing down the transfer by a factor of **22x**!

---

## 6. The 2-Minute Speaking Script

*(Speak clearly, calmly, and maintain eye contact with the faculty)*

> "Respected faculty, TCP guarantees reliable delivery over unreliable networks. When a packet is lost in transit, TCP must retransmit that packet, but more importantly, it interprets the loss as a signal of network congestion and aggressively throttles its transmission rate. My project studies and simulates this exact penalty.
>
> I developed an interactive simulator in Python based on the classical Mathis Analytical Model. The formula shows that TCP throughput is inversely proportional to Round Trip Time multiplied by the square root of packet loss: $\text{Throughput} \propto \frac{1}{\text{RTT} \times \sqrt{p}}$.
>
> In our simulator, the user can adjust five key network parameters: packet loss, RTT, MSS, physical link bandwidth, and file size.
>
> In addition to calculating throughput and transfer time, our project simulates the AIMD congestion window dynamics—where $cwnd$ increases by 1 packet per round and cuts in half on any loss event, producing the classic sawtooth pattern.
>
> The most critical takeaway our program demonstrates is that even a minuscule loss rate of 0.1% collapses a 100 Mbps connection down to just 4.5 Mbps.
>
> Finally, this is an analytical steady-state model for TCP Reno; modern algorithms like CUBIC or BBR handle loss and high-delay networks differently. Thank you, and I would be delighted to demonstrate the simulation."

---

## 7. Likely Faculty Viva Questions & Model Answers

### Q1: Why is throughput proportional to $1/\sqrt{p}$ and not $1/p$?
**Answer:**  
Because of the triangular geometry of the AIMD sawtooth:
1. In TCP Reno, $cwnd$ increases by 1 packet per RTT until a loss occurs.
2. The average number of packets delivered between two loss events is $\frac{1}{p}$.
3. The number of packets sent under the sawtooth is the area under the window:
   $$\text{Area} \approx \frac{1}{2} \times w_{\max} \times \frac{w_{\max}}{2} = \frac{3}{8} w_{\max}^2 \approx \frac{1}{p}$$
4. Solving for $w_{\max}$:
   $$w_{\max} \propto \frac{1}{\sqrt{p}}$$
5. Throughput is average window divided by RTT, yielding $\frac{1}{\text{RTT} \sqrt{p}}$.

### Q2: Why cap the throughput at link bandwidth?
**Answer:**  
The Mathis equation is an unconstrained theoretical model. In the real world, no transport protocol can physically transmit data faster than the bottleneck link rate (e.g. 100 Mbps cable cannot transmit at 150 Mbps). Thus: $\text{Throughput} = \min(\text{Mathis}, \text{Link Bandwidth})$.

### Q3: Why does zero loss return the link bandwidth?
**Answer:**  
At $p = 0$, dividing by $\sqrt{0}$ is mathematically undefined (tends to infinity). When there is zero loss, TCP is not loss-constrained; it is constrained only by link capacity or receiver buffer window ($rwnd$).

### Q4: Why halve cwnd on loss instead of reducing by 1?
**Answer:**  
According to Chiu & Jain's mathematical analysis of distributed congestion control, **Additive Increase / Multiplicative Decrease (AIMD)** is the only linear control scheme that guarantees convergence to **efficiency and fairness** among competing flows. Halving cwnd backs off drastically to clear router queues quickly.

### Q5: Is this simulation real TCP?
**Answer:**  
No. This is an analytical and discrete-event mathematical model of AIMD and Mathis behavior. A real TCP stack in the OS kernel includes three-way handshakes, Slow Start, selective acknowledgments (SACK), duplicate ACK thresholds, fast retransmit/fast recovery, and timer retransmission backoffs.

---

## 8. Limitations (State These Upfront)

1. **Analytical model, not physical packet sniffer:** Assumes steady-state congestion avoidance.
2. **Random Bernoulli loss assumption:** Assumes independent loss; real network drops often occur in bursts when router buffers overflow.
3. **Ignores connection setup overhead:** Excludes TCP 3-way handshake (SYN, SYN-ACK, ACK) and TLS negotiation delays.
4. **TCP Reno specific:** Modern OSes default to TCP CUBIC (Linux/macOS) or TCP BBR (Google), which do not follow $1/\sqrt{p}$.

---

## 9. Modern TCP Comparison (Bonus Marks)

| Protocol | Algorithm Type | Congestion Metric | Window Growth Function | High-BDP Link Recovery |
| :--- | :--- | :--- | :--- | :--- |
| **TCP Reno (1988)** | Loss-based AIMD | Packet Drop | Linear ($+1\text{ MSS} / \text{RTT}$) | Extremely slow (Hours on 10G link) |
| **TCP CUBIC (2006)** | Loss-based Cubic | Packet Drop | Cubic polynomial $W(t) = C(t-K)^3 + W_{\max}$ | Fast recovery, independent of RTT |
| **Google BBR (2016)** | Model-based Rate Pacing | Max Delivery Rate & Min RTT | Pacing at bottleneck bandwidth | Ignores random wireless loss; solves Bufferbloat |

---

## 10. Live Demo Checklist for Viva

1. **Preset 1:** Select **Standard Reference (1% Loss)**.
   - Point out: Throughput is only ~1.43 Mbps on a 100 Mbps link!
2. **Preset 2:** Select **The 0.1% Shock**.
   - Point out: Just reducing loss from 1% to 0.1% boosts throughput to 4.51 Mbps, illustrating the steep $1/\sqrt{p}$ curve.
3. **Preset 3:** Move RTT slider from $100\text{ ms}$ to $200\text{ ms}$.
   - Point out: Doubling RTT cuts throughput in half (proves inverse proportionality to RTT).
4. **Tab 1:** Show the **AIMD Sawtooth** chart and point out the red drop markers where cwnd halved.
5. **Tab 2:** Show the **Comparison Table** and download the CSV.
6. **Tab 3:** Walk through the **Live Step-by-Step Calculation**.
