"""
TCP Performance on Packet Loss - Interactive Simulator & Presentation Suite
Based on the Mathis Model & AIMD Congestion Control.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
from tcp_model import (
    mathis_throughput,
    calculate_metrics,
    simulate_cwnd,
    generate_loss_curve,
    generate_comparison_table
)

# Page configuration
st.set_page_config(
    page_title="TCP Performance on Packet Loss | Simulator & Study Guide",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Global modern clean aesthetic */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    
    /* Header card */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        line-height: 1.4;
    }
    .hero-tag {
        display: inline-block;
        background: #3b82f6;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* KPI metric cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    .accent-blue { color: #38bdf8; }
    .accent-amber { color: #fbbf24; }
    .accent-rose { color: #f43f5e; }
    .accent-emerald { color: #34d399; }

    /* Speaking script & Notes box */
    .script-box {
        background: #0f172a;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 1.2rem;
        color: #e2e8f0;
        font-size: 1.0rem;
        line-height: 1.6;
        font-style: italic;
        margin-bottom: 1rem;
    }
    .tip-box {
        background: #1e293b;
        border-left: 4px solid #10b981;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.8rem;
        color: #cbd5e1;
    }
    .warn-box {
        background: #1e293b;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.8rem;
        color: #cbd5e1;
    }
    
    /* Formula card */
    .formula-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR & PRESETS -----------------
st.sidebar.markdown("### 🎛️ Simulation Parameters")

preset = st.sidebar.selectbox(
    "📌 Quick Preset Scenarios",
    [
        "Standard Reference (1% Loss, 100ms, 100M)",
        "The 0.1% Shock (Tiny Loss Demonstration)",
        "Satellite Link (High RTT: 400ms)",
        "Data Center LAN (Low RTT: 10ms, 1Gbps)",
        "Flaky Mobile Link (3.5% Loss, 120ms)",
        "Ideal Zero-Loss Link (0% Loss)",
        "Custom Settings"
    ],
    index=0
)

# Preset mapping
preset_values = {
    "Standard Reference (1% Loss, 100ms, 100M)": {"loss": 1.0, "rtt": 100, "mss": 1460, "link": 100, "file": 100},
    "The 0.1% Shock (Tiny Loss Demonstration)": {"loss": 0.1, "rtt": 100, "mss": 1460, "link": 100, "file": 100},
    "Satellite Link (High RTT: 400ms)": {"loss": 0.5, "rtt": 400, "mss": 1460, "link": 50, "file": 100},
    "Data Center LAN (Low RTT: 10ms, 1Gbps)": {"loss": 0.05, "rtt": 10, "mss": 1460, "link": 1000, "file": 500},
    "Flaky Mobile Link (3.5% Loss, 120ms)": {"loss": 3.5, "rtt": 120, "mss": 1460, "link": 50, "file": 100},
    "Ideal Zero-Loss Link (0% Loss)": {"loss": 0.0, "rtt": 100, "mss": 1460, "link": 100, "file": 100},
    "Custom Settings": {"loss": 1.0, "rtt": 100, "mss": 1460, "link": 100, "file": 100}
}

p_conf = preset_values[preset]

# Sliders
loss_pct = st.sidebar.slider(
    "Packet Loss (%)",
    min_value=0.00,
    max_value=5.00,
    value=float(p_conf["loss"]),
    step=0.05,
    help="Fraction of transmitted packets dropped by the network (0% to 5%)."
)

rtt_ms = st.sidebar.slider(
    "Round Trip Time - RTT (ms)",
    min_value=10,
    max_value=500,
    value=int(p_conf["rtt"]),
    step=10,
    help="Time taken for a packet to reach destination and ACK to return."
)

mss_bytes = st.sidebar.slider(
    "Maximum Segment Size - MSS (Bytes)",
    min_value=536,
    max_value=1460,
    value=int(p_conf["mss"]),
    step=4,
    help="Maximum payload bytes inside each TCP packet (Standard Ethernet MTU 1500 - 40 header = 1460)."
)

link_mbps = st.sidebar.slider(
    "Physical Link Bandwidth (Mbps)",
    min_value=1,
    max_value=1000,
    value=int(p_conf["link"]),
    step=10,
    help="Physical channel bottleneck speed (physical upper bound)."
)

file_size_mb = st.sidebar.slider(
    "File Size (MB)",
    min_value=1,
    max_value=1000,
    value=int(p_conf["file"]),
    step=10,
    help="Total payload size to be transferred."
)

with st.sidebar.expander("⚙️ Advanced CWND Simulation Settings", expanded=False):
    sim_rounds = st.slider("Simulation RTT Rounds", min_value=50, max_value=300, value=150, step=10)
    sim_seed = st.number_input("Random Seed (for repeatability)", min_value=1, max_value=9999, value=42)
    initial_cwnd = st.number_input("Initial cwnd (packets)", min_value=1, max_value=32, value=10)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **💡 Quick Presentation Tip:**  
    *Demonstrate 1% loss first (~1.43 Mbps), then switch to 0.1% loss (~4.51 Mbps), then show 0% loss (100 Mbps).*
    """
)

# ----------------- CALCULATIONS -----------------
loss_fraction = loss_pct / 100.0
metrics = calculate_metrics(file_size_mb, mss_bytes, rtt_ms, loss_fraction, link_mbps)

th_val = metrics["throughput_mbps"]
tt_val = metrics["transfer_time_sec"]
retx_val = metrics["expected_retransmissions"]
util_val = metrics["utilization_pct"]
wasted_mb = metrics["wasted_mb"]

# Format transfer time nicely
if tt_val < 60:
    tt_str = f"{tt_val:.1f} s"
elif tt_val < 3600:
    minutes = int(tt_val // 60)
    seconds = int(tt_val % 60)
    tt_str = f"{minutes}m {seconds}s"
else:
    hours = tt_val / 3600.0
    tt_str = f"{hours:.2f} hrs"

# ----------------- HERO BANNER -----------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-tag">Computer Networks Project</div>
    <div class="hero-title">TCP Performance on Packet Loss Simulator</div>
    <div class="hero-subtitle">
        An interactive analytical study exploring how packet loss triggers TCP congestion control (AIMD), 
        drastically throttling throughput according to the <strong>Mathis Model</strong>: 
        <em>Throughput ∝ 1 / (RTT · √p)</em>.
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TOP METRIC CARDS -----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Estimated Throughput</div>
        <div class="metric-value accent-blue">{th_val:.2f} <span style="font-size:1rem; font-weight:normal;">Mbps</span></div>
        <div class="metric-sub">Cap: {link_mbps} Mbps ({util_val:.1f}% Link Utilized)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Transfer Time ({file_size_mb} MB)</div>
        <div class="metric-value accent-amber">{tt_str}</div>
        <div class="metric-sub">Ideal at full link: {(file_size_mb * 8 / link_mbps):.1f} s</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Expected Retransmissions</div>
        <div class="metric-value accent-rose">{round(retx_val):,} <span style="font-size:1rem; font-weight:normal;">pkts</span></div>
        <div class="metric-sub">{wasted_mb:.2f} MB overhead ({metrics['total_packets']:,} total pkts)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    bottleneck_status = "Link Bottleneck (Cap)" if loss_fraction == 0.0 or th_val >= link_mbps else "Loss Bottleneck (Mathis)"
    accent_class = "accent-emerald" if loss_fraction == 0.0 else "accent-rose"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Governing Regime</div>
        <div class="metric-value {accent_class}" style="font-size:1.25rem; margin-top:0.35rem;">{bottleneck_status}</div>
        <div class="metric-sub">p = {loss_pct:.2f}%, RTT = {rtt_ms} ms</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- TABS -----------------
tab_graphs, tab_table, tab_math, tab_script, tab_realworld = st.tabs([
    "📈 Interactive Graphs",
    "📊 Comparison Table & Export",
    "🧮 Mathematical Model & Live Steps",
    "🎙️ Faculty Defense & Speaking Script",
    "🌐 Real-World TCP (Reno vs CUBIC vs BBR)"
])

# ----------------- TAB 1: GRAPHS -----------------
with tab_graphs:
    st.subheader("1. Throughput vs. Packet Loss Curve")
    st.markdown("""
    The curve drops **steeply at first** and then flattens out, mirroring the characteristic $\\frac{1}{\\sqrt{p}}$ Mathis decay. 
    Notice how even fractional losses (0.1% - 0.5%) collapse the throughput.
    """)
    
    # Generate curve
    df_curve = generate_loss_curve(mss_bytes, rtt_ms, link_mbps, points=200, max_loss=5.0)
    
    fig_curve = go.Figure()
    
    # Mathis curve
    fig_curve.add_trace(go.Scatter(
        x=df_curve["loss_pct"],
        y=df_curve["throughput_mbps"],
        mode='lines',
        name='Mathis Model Estimate',
        line=dict(color='#38bdf8', width=3),
        hovertemplate="Loss: <b>%{x:.2f}%</b><br>Throughput: <b>%{y:.2f} Mbps</b><extra></extra>"
    ))
    
    # Current Operating Point
    fig_curve.add_trace(go.Scatter(
        x=[loss_pct],
        y=[th_val],
        mode='markers',
        name='Current Setting',
        marker=dict(color='#ef4444', size=12, symbol='circle', line=dict(color='#ffffff', width=2)),
        hovertemplate="Current Operating Point<br>Loss: <b>%{x:.2f}%</b><br>Throughput: <b>%{y:.2f} Mbps</b><extra></extra>"
    ))
    
    # Physical link capacity line
    fig_curve.add_hline(
        y=link_mbps,
        line_dash="dot",
        line_color="#10b981",
        annotation_text=f"Physical Link Capacity ({link_mbps} Mbps)",
        annotation_position="bottom right"
    )
    
    # Vertical line at current loss
    fig_curve.add_vline(
        x=loss_pct,
        line_dash="dash",
        line_color="rgba(239, 68, 68, 0.6)",
        annotation_text=f"p = {loss_pct:.2f}%",
        annotation_position="top left"
    )
    
    fig_curve.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(15, 23, 42, 0.7)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        height=420,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis_title="Packet Loss Rate p (%)",
        yaxis_title="TCP Throughput (Mbps)",
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_curve, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("2. AIMD Congestion Window Simulation (Sawtooth Graph)")
    st.markdown("""
    Each discrete round represents one RTT. In congestion avoidance:
    - **Additive Increase (AI):** When all packets in the window are ACKed, $cwnd$ increases by **+1 packet**.
    - **Multiplicative Decrease (MD):** When at least one packet suffers loss ($P = 1 - (1-p)^{cwnd}$), $cwnd$ **halves**.
    """)
    
    df_sim = simulate_cwnd(loss_fraction=loss_fraction, rounds=sim_rounds, seed=sim_seed, initial_cwnd=initial_cwnd)
    
    # Filter loss points
    loss_points = df_sim[df_sim["loss_event"] == True]
    
    fig_cwnd = go.Figure()
    
    # CWND line
    fig_cwnd.add_trace(go.Scatter(
        x=df_sim["round"],
        y=df_sim["cwnd"],
        mode='lines',
        name='Congestion Window (cwnd)',
        line=dict(color='#818cf8', width=2.5),
        hovertemplate="RTT Round: <b>%{x}</b><br>cwnd: <b>%{y} packets</b><extra></extra>"
    ))
    
    # Loss drops
    fig_cwnd.add_trace(go.Scatter(
        x=loss_points["round"],
        y=loss_points["cwnd"],
        mode='markers',
        name='Packet Loss Event (Halving)',
        marker=dict(color='#f43f5e', size=9, symbol='x', line=dict(width=2)),
        hovertemplate="Loss Detected in Round <b>%{x}</b><br>cwnd reduced to: <b>%{y}</b><extra></extra>"
    ))
    
    # Mean CWND line
    avg_cwnd = df_sim["cwnd"].mean()
    fig_cwnd.add_hline(
        y=avg_cwnd,
        line_dash="dash",
        line_color="#fbbf24",
        annotation_text=f"Average cwnd = {avg_cwnd:.1f} pkts",
        annotation_position="bottom right"
    )
    
    fig_cwnd.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(15, 23, 42, 0.7)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        height=400,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis_title="Time in RTT Rounds",
        yaxis_title="Congestion Window (packets)",
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_cwnd, use_container_width=True)
    
    # CWND Stats
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    c_s1.metric("Max Window Reached", f"{df_sim['cwnd'].max()} pkts")
    c_s2.metric("Min Window", f"{df_sim['cwnd'].min()} pkts")
    c_s3.metric("Average Window", f"{avg_cwnd:.1f} pkts")
    c_s4.metric("Total Loss Events", f"{len(loss_points)} drops")


# ----------------- TAB 2: COMPARISON TABLE -----------------
with tab_table:
    st.subheader("Benchmark Comparison Across Loss Rates")
    st.markdown(f"""
    This table evaluates performance for the current environment:
    **MSS = {mss_bytes} B, RTT = {rtt_ms} ms, Link = {link_mbps} Mbps, File Size = {file_size_mb} MB**.
    """)
    
    df_table = generate_comparison_table(mss_bytes, rtt_ms, link_mbps, file_size_mb)
    
    # Display table
    st.dataframe(
        df_table[["Packet Loss (%)", "Throughput (Mbps)", "Link Utilization", "Transfer Time", "Expected Retransmissions", "Wasted Data (MB)"]],
        use_container_width=True,
        hide_index=True
    )
    
    # Faculty highlight alert
    st.markdown("""
    > [!IMPORTANT]
    > **Key point to demonstrate to faculty:** Look at the jump from **0% to just 0.1% loss**. 
    > A minuscule 0.1% loss drops throughput from **100 Mbps to ~4.51 Mbps** (a ~95% performance penalty), 
    > causing file transfer time to balloon from 8 seconds to nearly 3 minutes!
    """)
    
    # CSV download
    csv_data = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Comparison Table as CSV",
        data=csv_data,
        file_name=f"tcp_loss_comparison_rtt{rtt_ms}ms_link{link_mbps}mbps.csv",
        mime="text/csv",
    )


# ----------------- TAB 3: MATHEMATICAL MODEL -----------------
with tab_math:
    st.subheader("The Mathis Analytical Model (1997)")
    st.markdown(r"""
    In 1997, Matthew Mathis, Jeffrey Semke, Jamshid Mahdavi, and Teunis Ott published their landmark paper:  
    *“The Macroscopic Behavior of the TCP Congestion Avoiding Algorithm” (ACM SIGCOMM CCR)*.
    
    They proved that when TCP Reno operates in steady-state congestion avoidance with random packet loss rate $p$, 
    the upper-bound throughput is given by:
    """)
    
    st.latex(r"\text{Throughput} \approx \frac{C \times \text{MSS} \times 8}{\text{RTT} \times \sqrt{p}}")
    
    st.markdown(r"""
    Where:
    - **$\text{MSS} \times 8$**: Converts payload bytes into bits.
    - **$\text{RTT}$**: Round-Trip Time in seconds. Dividing by RTT converts bits to rate per second.
    - **$\sqrt{p}$**: The packet loss penalty. Throughput scales inversely with $\sqrt{p}$, not $p$.
    - **$C = \sqrt{1.5} \approx 1.22$**: The geometric constant derived from the area under the AIMD sawtooth cycles.
    - **Physical Cap**: The throughput can never exceed the physical wire speed: $\min(\text{Mathis}, \text{Link})$.
    """)
    
    st.markdown("### 🔍 Live Step-by-Step Calculation for Your Current Inputs")
    
    if loss_fraction == 0:
        st.info("At 0.0% loss, $\\sqrt{p} = 0$, which makes the division undefined. In zero-loss networks, TCP throughput is bounded solely by link bandwidth or receiver flow control. Estimated = Physical Link Cap.")
    else:
        # Step breakdown
        mss_bits = mss_bytes * 8
        numerator = 1.22 * mss_bits
        rtt_sec = rtt_ms / 1000.0
        sqrt_p = math.sqrt(loss_fraction)
        denominator = rtt_sec * sqrt_p
        raw_bps = numerator / denominator
        raw_mbps = raw_bps / 1_000_000.0
        
        st.markdown(rf"""
        1. **Numerator (Bits per sawtooth cycle):**  
           $$1.22 \times \text{{MSS}} \times 8 = 1.22 \times {mss_bytes} \times 8 = {numerator:,.1f} \text{{ bits}}$$
           
        2. **Denominator (Loss-scaled RTT):**  
           $$\text{{RTT}}_{{\text{{sec}}}} \times \sqrt{{p}} = {rtt_sec:.3f} \text{{ s}} \times \sqrt{{{loss_fraction:.4f}}} = {rtt_sec:.3f} \times {sqrt_p:.4f} = {denominator:.6f} \text{{ s}}$$
           
        3. **Mathis Estimated Speed:**  
           $$\frac{{{numerator:,.1f}}}{{{denominator:.6f}}} = {raw_bps:,.0f} \text{{ bps}} \approx {raw_mbps:.3f} \text{{ Mbps}}$$
           
        4. **Apply Physical Link Bound:**  
           $$\text{{Throughput}} = \min({raw_mbps:.3f}, {link_mbps}) = \mathbf{{{th_val:.2f} \text{{ Mbps}}}}$$
        """)

    st.markdown("### 🎲 Expected Retransmissions Probability")
    st.markdown(r"""
    Under independent packet loss with Bernoulli probability $p$:
    - The number of transmission attempts needed before a packet successfully arrives follows a geometric distribution with mean:
      $$\mathbb{E}[\text{Attempts}] = \frac{1}{1 - p}$$
    - The expected number of **failed attempts (retransmissions)** per packet is:
      $$\mathbb{E}[\text{Retransmissions per packet}] = \frac{1}{1 - p} - 1 = \frac{p}{1 - p}$$
    - Total retransmissions for $N$ packets:
      $$R = N \times \frac{p}{1 - p}$$
    """)


# ----------------- TAB 4: FACULTY DEFENSE & VIVA PREP -----------------
with tab_script:
    st.subheader("🎓 2-Minute Presentation Script & Faculty Defense Guide")
    
    st.markdown("#### 🎙️ Speaking Script (Memorize or Read During Demo)")
    
    script_text = (
        '"Respected faculty, TCP guarantees reliable delivery over unreliable networks. When a packet '
        'is lost in transit, TCP must retransmit that packet, but more importantly, it interprets the loss '
        'as a signal of network congestion and aggressively throttles its transmission rate. '
        'My project studies and simulates this exact penalty.\n\n'
        'I implemented an interactive simulator in Python using the landmark Mathis Analytical Model. '
        'The formula states that TCP throughput is inversely proportional to RTT multiplied by the square root '
        'of packet loss (1 / (RTT * sqrt(p))). In our simulator, the user controls packet loss, RTT, MSS, link bandwidth, '
        'and file size.\n\n'
        'In addition to calculating throughput and transfer time, the project simulates the AIMD congestion window '
        'dynamics—where cwnd increases by 1 packet per round and cuts in half on any loss event, producing the classic '
        'sawtooth pattern.\n\n'
        'The most crucial takeaway from our findings is that even a minuscule packet loss of 0.1% drops a 100 Mbps '
        'connection down to just 4.5 Mbps. Finally, we note that this is an analytical steady-state model for TCP Reno; '
        'modern algorithms like CUBIC or BBR handle loss and high-delay networks differently."'
    )
    
    st.markdown(f"""
    <div class="script-box">
        {script_text.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("📚 The Five Core Definitions (Say These Simply)")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        st.markdown(r"""
        - **TCP (Transmission Control Protocol):** A connection-oriented, reliable transport protocol that detects dropped packets and retransmits them.
        - **Packet Loss ($p$):** The fraction of transmitted packets dropped by routers or noisy channels ($1\% = 1 \text{ in } 100$).
        - **RTT (Round Trip Time):** The total elapsed time for a data packet to travel from sender to receiver plus the ACK to return.
        """)
    with q_col2:
        st.markdown(r"""
        - **MSS (Maximum Segment Size):** The maximum amount of TCP data payload (excluding IP/TCP headers) in a single packet (standard: 1460 bytes).
        - **cwnd (Congestion Window):** The sender-side limit on how many unacknowledged packets TCP may send into the network simultaneously.
        """)

    st.markdown("---")
    
    st.subheader("❓ Likely Faculty Viva Questions & Model Answers")
    
    with st.expander("Q1: Why is throughput proportional to 1/√p instead of 1/p?"):
        st.markdown(r"""
        **Answer:**  
        Because of the **geometry of the AIMD sawtooth**.  
        In TCP Reno, the window grows linearly by 1 MSS every RTT until a loss occurs. The number of packets delivered between two loss events is approximately $1/p$.  
        Since the window forms a triangle of height $w_{\max}$ and base $w_{\max}/2$, the number of packets sent in a cycle is proportional to $w_{\max}^2$.  
        Equating $w_{\max}^2 \approx 1/p$ gives $w_{\max} \approx 1/\sqrt{p}$.  
        Dividing by RTT gives throughput $\propto \frac{1}{\text{RTT} \cdot \sqrt{p}}$.
        """)
        
    with st.expander("Q2: Why cap the throughput at physical link bandwidth?"):
        st.markdown(r"""
        **Answer:**  
        The Mathis formula is an asymptotic analytical estimate assuming the network buffer is infinite and the link is unconstrained.  
        However, in reality, a flow can **never transmit faster than the physical link** or bottleneck interface (e.g., a 100 Mbps cable cannot deliver 150 Mbps).  
        Therefore: $\text{Throughput} = \min(\text{Mathis Estimate}, \text{Link Bandwidth})$.
        """)

    with st.expander("Q3: Why does 0% loss return the link bandwidth?"):
        st.markdown(r"""
        **Answer:**  
        At $p = 0$, the Mathis equation divides by $\sqrt{0}$, which is undefined (approaching infinity).  
        When there is zero packet loss, TCP is not loss-constrained; it is bounded solely by either the receiver's advertised flow-control window (rwnd) or the physical link capacity.
        """)

    with st.expander("Q4: Why does TCP halve its window upon loss (Multiplicative Decrease)?"):
        st.markdown(r"""
        **Answer:**  
        According to Chiu & Jain's vector analysis of congestion avoidance, **Additive Increase / Multiplicative Decrease (AIMD)** is mathematically guaranteed to converge to **both efficiency and fairness** when independent users share a bottleneck.  
        Halving the window rapidly empties congested router buffers (preventing congestion collapse), while slowly incrementing by 1 gently probes for available capacity.
        """)

    with st.expander("Q5: What are the key limitations of this model?"):
        st.markdown(r"""
        **Answer (State these proactively to impress the examiner!):**  
        1. **Analytical model, not physical emulator:** Assumes long-running, steady-state flows without slow start or three-way handshakes.
        2. **Independent random loss assumption:** Assumes Bernoulli loss; real network losses often occur in bursts due to full router drop-tail buffers.
        3. **TCP Reno specific:** Modern operating systems default to TCP CUBIC (Linux/Android/macOS) or TCP BBR (Google), which do not follow $1/\sqrt{p}$.
        """)


# ----------------- TAB 5: REAL-WORLD TCP CONTEXT -----------------
with tab_realworld:
    st.subheader("Beyond Reno: How Modern TCP Protocols Handle Loss")
    st.markdown("""
    While the Mathis model perfectly describes classical **TCP Reno**, modern high-speed networks exposed major weaknesses in Reno:
    on a 10 Gbps transatlantic link (100ms RTT), Reno would require a loss rate less than $10^{-8}$ (1 in 100 million packets) to fill the pipe, 
    and recovering after a single packet loss would take over **an hour**!
    """)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="metric-label" style="color:#38bdf8;">TCP Reno (1988)</div>
            <div style="font-size:0.95rem; font-weight:bold; margin-bottom:0.5rem; color:#f8fafc;">Standard AIMD</div>
            <ul style="font-size:0.85rem; color:#cbd5e1; padding-left:1.2rem;">
                <li>Linear window increase (+1 packet / RTT)</li>
                <li>Multiplicative decrease (halves cwnd on loss)</li>
                <li>Suffers terrible performance on high Bandwidth-Delay Product (BDP) links</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(r"""
        <div class="metric-card" style="text-align:left;">
            <div class="metric-label" style="color:#a855f7;">TCP CUBIC (Default in Linux/macOS)</div>
            <div style="font-size:0.95rem; font-weight:bold; margin-bottom:0.5rem; color:#f8fafc;">Cubic Window Function</div>
            <ul style="font-size:0.85rem; color:#cbd5e1; padding-left:1.2rem;">
                <li>Replaces linear growth with a cubic polynomial function of elapsed time since last loss</li>
                <li>Rapidly climbs back to $W_{\max}$, slows down near inflection, then probes aggressively</li>
                <li>RTT-independent window growth ensures fairness across long and short links</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c3:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="metric-label" style="color:#10b981;">BBR (Google, 2016)</div>
            <div style="font-size:0.95rem; font-weight:bold; margin-bottom:0.5rem; color:#f8fafc;">Bottleneck Bandwidth & RTT</div>
            <ul style="font-size:0.85rem; color:#cbd5e1; padding-left:1.2rem;">
                <li>Does <strong>not</strong> interpret packet loss as congestion!</li>
                <li>Actively measures bottleneck delivery rate and min RTT</li>
                <li>Maximizes throughput while keeping queues empty, solving <em>bufferbloat</em></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Protocol Comparison Matrix")
    
    df_proto = pd.DataFrame([
        {
            "Protocol": "TCP Reno",
            "Congestion Metric": "Packet Loss",
            "Growth Function": "Linear (+1 per RTT)",
            "Reaction to Loss": "Halves cwnd (MD)",
            "High BDP Link Performance": "Extremely Poor"
        },
        {
            "Protocol": "TCP CUBIC",
            "Congestion Metric": "Packet Loss",
            "Growth Function": "Cubic Polynomial: W(t) = C(t-K)³ + Wmax",
            "Reaction to Loss": "Reduces cwnd by 30% (β = 0.7)",
            "High BDP Link Performance": "Excellent"
        },
        {
            "Protocol": "Google BBR",
            "Congestion Metric": "Bottleneck Bandwidth & Min RTT",
            "Growth Function": "Rate Pacing Model",
            "Reaction to Loss": "Ignores random non-congestive loss",
            "High BDP Link Performance": "State of the Art"
        }
    ])
    st.dataframe(df_proto, use_container_width=True, hide_index=True)
