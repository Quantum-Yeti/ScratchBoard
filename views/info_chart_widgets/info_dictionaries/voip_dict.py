voip_signals = [
    {
        "name": "Jitter (ms)",
        "range": "< 30",
        "symptoms": "Choppy audio, clicks, or delays",
        "explanation": "Variation in packet arrival times can cause voice degradation.",
        "steps": "Check network congestion, enable QoS, avoid Wi-Fi interference."
    },
    {
        "name": "Packet Loss (%)",
        "range": "< 1%",
        "symptoms": "Dropped audio, call drops",
        "explanation": "Lost packets reduce call quality and can interrupt calls.",
        "steps": "Inspect network, prefer wired connection, configure router QoS."
    },
    {
        "name": "Latency / Ping (ms)",
        "range": "< 150",
        "symptoms": "Delayed conversation, echo",
        "explanation": "Time it takes for voice packets to travel from sender to receiver.",
        "steps": "Check WAN link, VPN, or routing issues."
    },
    {
        "name": "MOS (Mean Opinion Score)",
        "range": "4.0–5.0",
        "symptoms": "Poor audio quality, user complaints",
        "explanation": "User-perceived call quality score (1 = bad, 5 = excellent).",
        "steps": "Optimize network, check codecs, upgrade hardware if needed."
    },
    {
        "name": "SIP Registration",
        "range": "Registered",
        "symptoms": "Cannot make/receive calls",
        "explanation": "Status of SIP registration with VoIP server.",
        "steps": "Restart device, verify credentials, check firewall rules."
    },
    {
        "name": "Codec Mismatch",
        "range": "Supported codecs",
        "symptoms": "One-way audio, no audio",
        "explanation": "Device is using a codec unsupported by PBX or server.",
        "steps": "Configure correct codecs on PBX and endpoints."
    },
    {
        "name": "Echo / Noise",
        "range": "Minimal",
        "symptoms": "Feedback, static",
        "explanation": "Can be acoustic or network-based echo.",
        "steps": "Check headset, reduce network latency, enable echo cancellation."
    },
    {
        "name": "Bandwidth Usage",
        "range": "≥ 100 kbps per call",
        "symptoms": "Audio degradation, dropped calls",
        "explanation": "Insufficient bandwidth affects call quality.",
        "steps": "Increase bandwidth, prioritize voice traffic (QoS)."
    }
]