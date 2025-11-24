docsis_signals = [
    {
        "name": "Downstream Power (dBmV)",
        "range": "-8 to +10",
        "symptoms": "Too low: intermittent downstream lock\nToo high: distortion, retrains",
        "explanation": "Represents the power at the modem for downstream channels. Out-of-range values indicate coax, splitter, or amplifier issues.",
        "steps": "Check coax connections, splitters, inspect taps or amplifiers."
    },
    {
        "name": "Downstream SNR (dB)",
        "range": ">= 35",
        "symptoms": "Low SNR leads to sync loss or packet errors",
        "explanation": "Signal-to-noise ratio measures quality of downstream signal. Low SNR usually indicates noise on the line or weak signal.",
        "steps": "Check connectors, avoid long coax runs, replace damaged cables, check network noise sources."
    },
    {
        "name": "Upstream Power (dBmV)",
        "range": "+35 to +50",
        "symptoms": "Too low: cannot reach CMTS\nToo high: line faults or amplifier issues",
        "explanation": "Power transmitted from modem to CMTS. Out-of-range values affect connectivity.",
        "steps": "Inspect splitter, check line condition, adjust amplifier if available."
    },
    {
        "name": "Upstream SNR (dB)",
        "range": ">= 30 dB",
        "symptoms": "Low upstream SNR causes ranging failures and T3/T4 timeouts",
        "explanation": "Indicates how clean the upstream signal appears to the CMTS.",
        "steps": "Check for loose connectors, damaged coax, ingress noise sources, and splitters."
    },
    {
        "name": "CMTS Receive Power (dBmV)",
        "range": "-2 to +2 (ideal)",
        "symptoms": "Too low: modem signal not reaching CMTS\nToo high: distortion at CMTS",
        "explanation": "The power level the CMTS receives from the modem.",
        "steps": "Inspect coax, splitters, excessive attenuation, or upstream amplifiers."
    },
    {
        "name": "CMTS SNR (dB)",
        "range": ">= 30 dB",
        "symptoms": "Low CMTS SNR causes intermittent upstream loss and high errors",
        "explanation": "Shows how clean the modem’s upstream signal is when received at the CMTS.",
        "steps": "Check for ingress, damaged coax, loose connectors, upstream noise sources."
    },
    {
        "name": "Network Utilization",
        "range": "< 80% recommended",
        "symptoms": "High utilization causes congestion, latency, slow speeds",
        "explanation": "Represents load on upstream/downstream channels.",
        "steps": "Check upstream noise, ISP congestion, or provisioning problems."
    },
    {
        "name": "Correctable Codewords (Downstream)",
        "range": "Low to moderate",
        "symptoms": "High numbers indicate noisy channel",
        "explanation": "Errors corrected by FEC. Lots of correctables indicate noise.",
        "steps": "Inspect coax and connectors, reduce interference, check splitters, monitor trends."
    },
    {
        "name": "Uncorrectable Codewords (Downstream)",
        "range": "Very low",
        "symptoms": "High numbers cause packet loss and service degradation",
        "explanation": "Errors that FEC cannot fix. Indicates severe noise or signal impairment.",
        "steps": "Replace damaged cables and check connectors."
    },
    {
        "name": "Upstream Correctable Codewords",
        "range": "Low",
        "symptoms": "Rising numbers indicate upstream noise or ingress",
        "explanation": "Correctable errors on the modem’s upstream transmissions.",
        "steps": "Check coax, tighten connectors, eliminate noise sources."
    },
    {
        "name": "Upstream Uncorrectable Codewords",
        "range": "Near zero",
        "symptoms": "High values cause upstream packet loss and T3/T4 timeouts",
        "explanation": "Uncorrectable upstream errors indicate serious ingress or return path issues.",
        "steps": "Inspect upstream path, replace faulty connectors, remove noise sources."
    },
    {
        "name": "T3 Timeout",
        "range": "N/A",
        "symptoms": "Upstream lost intermittently",
        "explanation": "Modem is not hearing CMTS for upstream. Usually noise or line problem.",
        "steps": "Check coax, splitters, noise sources, or plant issues."
    },
    {
        "name": "T4 Timeout",
        "range": "N/A",
        "symptoms": "Modem loses upstream completely",
        "explanation": "Modem fails to range upstream. Often service outage or severe noise.",
        "steps": "Check upstream connectivity, inspect coax, requires a Technician."
    },
    {
        "name": "DHCP / IP Issues",
        "range": "Modem obtains IP",
        "symptoms": "Modem cannot get IP, no internet",
        "explanation": "Indicates provisioning or upstream communication problem.",
        "steps": "Restart modem, check cabling, verify CMTS reachable."
    },
    {
        "name": "MER (Modulation Error Ratio)",
        "range": "≥ 35 dB (DOCSIS 3.0), ≥ 30 dB (DOCSIS 3.1)",
        "symptoms": "Low → errors, poor signal quality",
        "explanation": "Measures modulation quality on downstream channels.",
        "steps": "Check cabling, connectors, and interference sources."
    },
    {
        "name": "Channel Bonding / Frequency",
        "range": "Varies by ISP",
        "symptoms": "Channels drop or fail to bond",
        "explanation": "Shows channel tuning and frequency stability.",
        "steps": "Inspect coax, splitters, or contact ISP for channel issues."
    },
]
