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
                "symptoms": "Too low: cannot reach CMTS\nToo high: possible line faults or amplifier issues",
                "explanation": "Power transmitted from modem to CMTS. Out-of-range can affect connectivity.",
                "steps": "Inspect splitter, check line condition, adjust amplifier if available."
            },
            {
                "name": "Correctable Codewords",
                "range": "Low to moderate",
                "symptoms": "High numbers indicate noisy channel",
                "explanation": "Errors that can be corrected by FEC. Too many means signal noise.",
                "steps": "Inspect coax and connectors, reduce interference, check splitters, monitor trends."
            },
            {
                "name": "Uncorrectable Codewords",
                "range": "Very low",
                "symptoms": "High numbers cause packet loss and service degradation",
                "explanation": "Errors that FEC cannot fix. Indicates serious line issues.",
                "steps": "Replace damaged cables and check connectors."
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
                "steps": "Check upstream connectivity, and inspect coax."
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