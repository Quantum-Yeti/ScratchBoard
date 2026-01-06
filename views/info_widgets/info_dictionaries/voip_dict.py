voip_signals = [
    {
        "name": "Jitter (ms)",
        "range": "< 30 ms",
        "symptoms": "Choppy audio, clicks, or delays in conversation",
        "explanation": "Variation in packet arrival times, causing audio distortion and delays.",
        "steps": "Check for network congestion, enable Quality of Service (QoS), and reduce Wi-Fi interference."
    },
    {
        "name": "Packet Loss (%)",
        "range": "< 1%",
        "symptoms": "Dropped audio, call disconnects, distorted sound",
        "explanation": "Packet loss reduces call quality and can cause interruptions in the call.",
        "steps": "Inspect the network for issues, use a wired connection, and configure router QoS to prioritize voice traffic."
    },
    {
        "name": "Latency / Ping (ms)",
        "range": "< 150 ms",
        "symptoms": "Delayed conversation, noticeable echo, poor call quality",
        "explanation": "The time it takes for voice packets to travel from sender to receiver. Higher latency causes delays in communication.",
        "steps": "Check WAN link, inspect VPN settings, and resolve routing issues."
    },
    {
        "name": "MOS (Mean Opinion Score)",
        "range": "4.0–5.0",
        "symptoms": "Poor audio quality, user complaints, distorted speech",
        "explanation": "A score representing user-perceived call quality, where 1 is bad and 5 is excellent.",
        "steps": "Optimize the network, check codec settings, and upgrade hardware if necessary."
    },
    {
        "name": "SIP Registration",
        "range": "Registered",
        "symptoms": "Unable to make or receive calls, registration failure",
        "explanation": "Indicates the status of the SIP registration with the VoIP server.",
        "steps": "Restart the device, verify SIP credentials, check firewall settings for port blocking."
    },
    {
        "name": "Codec Mismatch",
        "range": "Supported codecs configured",
        "symptoms": "One-way audio, no audio, call drops",
        "explanation": "Occurs when the device is using a codec not supported by the PBX or VoIP server.",
        "steps": "Ensure the correct codecs are configured on both the PBX and the endpoints (devices)."
    },
    {
        "name": "Echo / Noise",
        "range": "Minimal or absent",
        "symptoms": "Echo, feedback, static noise during calls",
        "explanation": "Echo can be caused by acoustic feedback or network-related issues.",
        "steps": "Check the headset or microphone settings, reduce network latency, and enable echo cancellation features."
    },
    {
        "name": "Bandwidth Usage",
        "range": "≥ 100 kbps per call",
        "symptoms": "Audio degradation, dropped calls, delays in conversation",
        "explanation": "Inadequate bandwidth causes poor audio quality and may drop calls.",
        "steps": "Increase available bandwidth, prioritize voice traffic using QoS settings on the network."
    }
]
