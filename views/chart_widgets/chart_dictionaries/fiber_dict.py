signals = [
            {
                "name": "Optical Power (Rx) – Downstream",
                "range": "-27 dBm to -8 dBm",
                "symptoms": "Too low → slow speeds, drops, no light signal\nToo high → laser saturation, ONT resets",
                "explanation": "Received light level from OLT to ONT. Fiber attenuation, dirty connectors, or long distances reduce power.",
                "steps": "Clean fiber connectors; check for bends/kinks; inspect the drop fiber; request fiber light-level test by ISP."
            },
            {
                "name": "Optical Power (Tx) – Upstream",
                "range": "+0.5 dBm to +5 dBm",
                "symptoms": "Too low → ONT cannot reach OLT\nToo high → laser malfunction or hardware issue",
                "explanation": "Upstream light transmitted from ONT to OLT. Problems usually mean connector contamination or ONT laser failure.",
                "steps": "Clean connectors, ensure no sharp bends; restart ONT; check if ONT laser warnings appear in logs."
            },
            {
                "name": "Optical Signal-to-Noise Ratio (OSNR)",
                "range": "≥ 20 dB (GPON) / ≥ 28 dB (XGS-PON)",
                "symptoms": "Low OSNR → unstable speeds, packet loss, or ONT re-registration",
                "explanation": "OSNR measures light clarity. Low OSNR usually indicates backbone fiber issues, bad splices, or optical amplifier degradation.",
                "steps": "Report to ISP; check for fiber cuts, water intrusion, or failing OLT optics."
            },
            {
                "name": "Laser Bias Current",
                "range": "Vendor-specific",
                "symptoms": "Rising current → aging laser, eventual transmit failure",
                "explanation": "Represents drive current powering ONT laser. Increase over time = laser degradation.",
                "steps": "Monitor trends; replace ONT if bias current nears upper limit."
            },
            {
                "name": "Loss of Optical Signal (LOS)",
                "range": "None expected",
                "symptoms": "No internet; ONT LOS light blinking; cannot establish link",
                "explanation": "ONT cannot see light from OLT. Usually fiber unplugged, broken, or blocked.",
                "steps": "Clean connectors, reseat SC/APC connector; inspect drop fiber; check for bends; contact ISP if persists."
            },
            {
                "name": "Loss of Frame (LOF)",
                "range": "None expected",
                "symptoms": "Internet drops but light levels appear normal",
                "explanation": "ONT receives light but cannot decode PON frames. Usually upstream noise or OLT-side issues.",
                "steps": "Restart ONT; request ISP to check PON card or splitter leg."
            },
            {
                "name": "Loss of GEM Channel (LOM)",
                "range": "None expected",
                "symptoms": "ONT connects but no data passes",
                "explanation": "GEM channel assignment issues between ONT and OLT, often provisioning misconfigurations.",
                "steps": "ISP must re-provision ONT profile; verify serial number match."
            },
            {
                "name": "PON Technology",
                "range": "GPON, XGS-PON, 10G-EPON",
                "symptoms": "Speed issues if ONT/OLT mismatch or oversubscribed splitter",
                "explanation": "ONT connects to shared PON with splitters limiting available bandwidth.",
                "steps": "Verify ONT supports subscribed speed; confirm PON capacity with ISP."
            },
            {
                "name": "Splitter Loss",
                "range": "1:32 ≈ 17 dB loss, 1:16 ≈ 13 dB loss",
                "symptoms": "Low downstream optical power; degraded upstream range",
                "explanation": "Splitters divide fiber into multiple customers, introducing attenuation proportional to split ratio.",
                "steps": "Upgrades require ISP; customer cannot fix splitter loss."
            },
            {
                "name": "Fiber Connector / Splice Quality",
                "range": "0.1–0.3 dB per splice",
                "symptoms": "Gradual speed reduction, increased error rates",
                "explanation": "Poor splices or dirty connectors introduce reflection and attenuation.",
                "steps": "Clean SC/APC ends; inspect for dust; request OTDR test for splice loss."
            },
        ]