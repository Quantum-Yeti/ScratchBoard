docsis_signals = [
    {
        "name": "Downstream Power (dBmV)",
        "range": "-8 to +10",
        "symptoms": "Too low: intermittent downstream lock, instability\nToo high: signal distortion, retrains, poor quality",
        "explanation": "Represents the power level of the downstream channels at the modem. Power levels outside the optimal range can indicate issues with coaxial cables, splitters, or amplifiers.",
        "steps": "Check the coaxial connections, ensure splitters are functioning properly, and inspect taps or amplifiers for faults."
    },
    {
        "name": "Downstream SNR (dB)",
        "range": ">= 35 dB",
        "symptoms": "Low SNR leads to sync loss, frequent packet errors, or poor throughput",
        "explanation": "The Signal-to-Noise Ratio (SNR) represents the quality of the downstream signal. Low SNR indicates either weak signal strength or noise interference on the line.",
        "steps": "Inspect the cable connectors, avoid long coaxial runs, replace any damaged cables, and check for noise sources in the network."
    },
    {
        "name": "Upstream Power (dBmV)",
        "range": "+35 to +50 dBmV",
        "symptoms": "Too low: the modem cannot reach the CMTS (Cable Modem Termination System)\nToo high: potential line faults or amplifier overdrive",
        "explanation": "Represents the power level of the signal transmitted from the modem to the CMTS. Out-of-range values can cause connectivity issues or signal quality problems.",
        "steps": "Inspect the coaxial cable, check for damaged splitters, and verify the functionality of amplifiers or line splitters."
    },
    {
        "name": "Upstream SNR (dB)",
        "range": ">= 30 dB",
        "symptoms": "Low upstream SNR causes T3/T4 timeouts, ranging failures, and poor upload performance",
        "explanation": "The upstream SNR shows the quality of the upstream signal received by the CMTS. Low values can indicate interference or weak signal transmission from the modem.",
        "steps": "Check for loose connectors, damaged cables, or sources of interference such as poor-quality splitters or amplifiers."
    },
    {
        "name": "CMTS Receive Power (dBmV)",
        "range": "-2 to +2 dBmV (ideal)",
        "symptoms": "Too low: modem signal not properly reaching CMTS\nToo high: potential distortion at the CMTS, signal degradation",
        "explanation": "Represents the power level the CMTS receives from the modem. Inadequate or excessive power can lead to communication issues.",
        "steps": "Inspect coaxial cables, check for excessive signal attenuation, and adjust upstream amplifiers if applicable."
    },
    {
        "name": "CMTS SNR (dB)",
        "range": ">= 30 dB",
        "symptoms": "Low CMTS SNR results in intermittent upstream loss, high packet errors, and connectivity problems",
        "explanation": "This represents how clean the upstream signal is when received at the CMTS. Low values typically point to network interference or weak signal quality.",
        "steps": "Inspect for ingress (external signal interference), damaged coax, and poor-quality connectors."
    },
    {
        "name": "Network Utilization",
        "range": "< 80% recommended",
        "symptoms": "High utilization can lead to congestion, increased latency, and decreased throughput",
        "explanation": "Network utilization represents the load on the upstream and downstream channels. Utilization above 80% may cause performance degradation.",
        "steps": "Check for upstream network congestion, investigate potential ISP throttling, or look for provisioning issues that may be affecting bandwidth."
    },
    {
        "name": "Correctable Codewords (Downstream)",
        "range": "Low to moderate",
        "symptoms": "High values suggest noisy channels or signal instability",
        "explanation": "Correctable codewords indicate errors that have been fixed by Forward Error Correction (FEC). A high number of correctables suggests interference or poor signal quality.",
        "steps": "Inspect coaxial cables and connectors, reduce interference sources, check splitters for functionality, and monitor trends over time."
    },
    {
        "name": "Uncorrectable Codewords (Downstream)",
        "range": "Very low, ideally zero",
        "symptoms": "High numbers result in packet loss, service degradation, and unreliable connectivity",
        "explanation": "Uncorrectable codewords represent errors that cannot be fixed by FEC. A high number of uncorrectables indicates severe signal impairment or noise on the line.",
        "steps": "Replace damaged cables, inspect connectors, and reduce any noise or interference sources in the network."
    },
    {
        "name": "Upstream Correctable Codewords",
        "range": "Low to moderate",
        "symptoms": "Increasing numbers point to upstream noise or interference",
        "explanation": "Indicates correctable errors on the upstream signal transmitted by the modem. A rising count suggests poor signal quality or interference.",
        "steps": "Tighten connectors, check the upstream cable for damage, and eliminate potential ingress or noise sources."
    },
    {
        "name": "Upstream Uncorrectable Codewords",
        "range": "Near zero",
        "symptoms": "High values indicate upstream packet loss, T3/T4 timeouts, and severe connection issues",
        "explanation": "Uncorrectable upstream errors indicate critical issues with the upstream signal, often caused by ingress or return path problems.",
        "steps": "Inspect the upstream path, replace faulty connectors, and remove noise sources in the upstream signal chain."
    },
    {
        "name": "T3 Timeout",
        "range": "N/A",
        "symptoms": "Intermittent loss of upstream communication",
        "explanation": "A T3 timeout occurs when the modem fails to receive a response from the CMTS in a timely manner. Often due to network noise or physical issues with the coaxial line.",
        "steps": "Check coaxial cables, splitters, and any potential sources of noise. Look for issues within the cable plant or line network."
    },
    {
        "name": "T4 Timeout",
        "range": "N/A",
        "symptoms": "Complete loss of upstream communication",
        "explanation": "A T4 timeout occurs when the modem fails to synchronize with the upstream channel. Often a sign of a severe service outage or excessive noise.",
        "steps": "Inspect upstream connectivity, check coaxial cables, and consider a technician visit for further diagnostics."
    },
    {
        "name": "DHCP / IP Issues",
        "range": "Modem obtains IP address",
        "symptoms": "Modem cannot acquire an IP address from the DHCP server, resulting in no internet access",
        "explanation": "Indicates a provisioning issue, or that the modem cannot communicate with the CMTS to obtain a valid IP address.",
        "steps": "Restart the modem, check the coaxial cable, verify that the CMTS is reachable, and ensure no issues with the ISP's DHCP server."
    },
    {
        "name": "MER (Modulation Error Ratio)",
        "range": "≥ 35 dB (DOCSIS 3.0), ≥ 30 dB (DOCSIS 3.1)",
        "symptoms": "Low MER leads to errors, poor signal quality, and frequent retrains",
        "explanation": "MER measures the quality of modulation on the downstream channels. A low MER value indicates issues with the signal integrity, leading to possible retransmissions and packet loss.",
        "steps": "Check cabling, connectors, and sources of interference (e.g., electrical devices or other cables nearby)."
    },
    {
        "name": "Channel Bonding / Frequency",
        "range": "Varies by ISP",
        "symptoms": "Channels drop, fail to bond, or experience poor synchronization",
        "explanation": "This refers to the stability and bonding of multiple channels on both upstream and downstream. Bonding issues can affect overall speed and signal integrity.",
        "steps": "Inspect coaxial cables, check splitters for proper function, and consult with the ISP for any known channel issues or outages."
    },
]
