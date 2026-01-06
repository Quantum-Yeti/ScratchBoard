signals = [
    {
        "name": "Optical Power (Rx) – Downstream",
        "range": "-27 dBm to -8 dBm",
        "symptoms": "Too low: slow speeds, intermittent drops, no signal\nToo high: laser saturation, ONT resets",
        "explanation": "Received optical power from the OLT to the ONT. Low power could result from fiber attenuation, dirty connectors, or excessive cable length. High power indicates laser saturation or equipment malfunction.",
        "steps": "Clean fiber connectors, ensure there are no bends or kinks in the fiber, and inspect the fiber drop. Request a fiber light-level test from the ISP if the issue persists."
    },
    {
        "name": "Optical Power (Tx) – Upstream",
        "range": "+0.5 dBm to +5 dBm",
        "symptoms": "Too low: ONT cannot reach the OLT\nToo high: potential laser malfunction or hardware failure",
        "explanation": "Transmitted optical power from the ONT to the OLT. Low power can indicate connector contamination or laser failure, while high power suggests potential issues with the ONT laser.",
        "steps": "Clean fiber connectors, ensure no sharp bends in the fiber, and restart the ONT. Check ONT logs for any laser warning messages."
    },
    {
        "name": "Optical Signal-to-Noise Ratio (OSNR)",
        "range": "≥ 20 dB (GPON) / ≥ 28 dB (XGS-PON)",
        "symptoms": "Low OSNR leads to unstable speeds, packet loss, or ONT re-registration",
        "explanation": "OSNR measures the clarity of the optical signal. Low OSNR values typically indicate issues with the fiber backbone, poor splicing, or degrading optical amplifiers.",
        "steps": "Report to ISP for troubleshooting. Check for fiber cuts, water intrusion, or aging OLT optics."
    },
    {
        "name": "Laser Bias Current",
        "range": "Vendor-specific",
        "symptoms": "Rising bias current indicates aging laser, potentially leading to failure",
        "explanation": "The laser bias current powers the ONT’s laser. Over time, a gradual increase in this value can signal degradation of the laser's functionality.",
        "steps": "Monitor the trend of bias current. Replace the ONT if the bias current approaches the upper limit specified by the vendor."
    },
    {
        "name": "Loss of Optical Signal (LOS)",
        "range": "None expected",
        "symptoms": "No internet; ONT LOS indicator blinking; no connection established",
        "explanation": "The ONT is not receiving any optical signal from the OLT, often due to disconnected or damaged fiber.",
        "steps": "Clean connectors and reseat the SC/APC connector. Inspect the fiber drop for damage or bends, and contact the ISP if the issue persists."
    },
    {
        "name": "Loss of Frame (LOF)",
        "range": "None expected",
        "symptoms": "Internet drops despite normal light levels",
        "explanation": "The ONT is receiving light but cannot decode the PON frames, typically due to upstream noise or issues on the OLT side.",
        "steps": "Restart the ONT and request the ISP to check the PON card or splitter leg for issues."
    },
    {
        "name": "Loss of GEM Channel (LOM)",
        "range": "None expected",
        "symptoms": "ONT connects but no data is transmitted",
        "explanation": "GEM (GPON Encapsulation Method) channel assignment issues, often due to provisioning misconfigurations between the ONT and OLT.",
        "steps": "ISP intervention is required to re-provision the ONT profile. Verify serial number matching between the ONT and OLT."
    },
    {
        "name": "PON Technology",
        "range": "GPON, XGS-PON, 10G-EPON",
        "symptoms": "Speed issues if ONT and OLT are mismatched or if the splitter is oversubscribed",
        "explanation": "The ONT connects to a shared PON, and the available bandwidth is limited by the number of users and splitter capacity.",
        "steps": "Verify that the ONT supports the subscribed speed, and check the PON capacity with your ISP."
    },
    {
        "name": "Splitter Loss",
        "range": "1:32 ≈ 17 dB loss, 1:16 ≈ 13 dB loss",
        "symptoms": "Degraded downstream optical power, limited upstream range",
        "explanation": "Splitters divide the fiber into multiple paths, introducing signal loss proportional to the split ratio. High split ratios cause more attenuation.",
        "steps": "Splitter loss upgrades need to be requested from the ISP, as customers cannot modify splitter configuration."
    },
    {
        "name": "Fiber Connector / Splice Quality",
        "range": "0.1–0.3 dB per splice",
        "symptoms": "Gradual speed degradation, increased error rates over time",
        "explanation": "Poor splice quality or dirty connectors lead to signal reflection and increased attenuation, degrading the optical signal.",
        "steps": "Clean SC/APC fiber connectors, inspect for dust, and request an OTDR (Optical Time Domain Reflectometer) test to check splice losses."
    },
]
