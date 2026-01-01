requirements = [
            {
                "activity": "Web Browsing / Social Media",
                "min": "1–5 Mbps",
                "rec": "10+ Mbps",
                "latency": "< 100 ms",
                "notes": "Very low bandwidth; responsive browsing benefits from lower latency."
            },
            {
                "activity": "Email & Cloud Docs",
                "min": "1 Mbps",
                "rec": "5–10 Mbps",
                "latency": "< 100 ms",
                "notes": "Small uploads/downloads; stable connection matters more than speed."
            },
            {
                "activity": "Video Calls (Zoom/Meet) – 1:1",
                "min": "2 Mbps",
                "rec": "3–5 Mbps",
                "latency": "< 80 ms",
                "notes": "HD video requires upload + download stability."
            },
            {
                "activity": "Video Conference (Group Call)",
                "min": "3–4 Mbps",
                "rec": "5–8 Mbps",
                "latency": "< 60 ms",
                "notes": "More users = more bandwidth; jitter can cause glitches."
            },
            {
                "activity": "Online Gaming",
                "min": "3 Mbps",
                "rec": "10–25 Mbps",
                "latency": "< 30 ms",
                "notes": "Speed not important; **latency and jitter** are critical."
            },
            {
                "activity": "Cloud Gaming (GeForce NOW, Xbox)",
                "min": "15 Mbps",
                "rec": "35–50 Mbps",
                "latency": "< 40 ms",
                "notes": "Needs stable downstream + upstream + low jitter."
            },
            {
                "activity": "Streaming SD Video",
                "min": "3 Mbps",
                "rec": "5+ Mbps",
                "latency": "N/A",
                "notes": "Low requirement; most connections exceed this."
            },
            {
                "activity": "Streaming HD 1080p",
                "min": "5 Mbps",
                "rec": "10–15 Mbps",
                "latency": "N/A",
                "notes": "Higher bitrates for live TV streams."
            },
            {
                "activity": "Streaming 4K",
                "min": "25 Mbps",
                "rec": "50+ Mbps",
                "latency": "N/A",
                "notes": "Some services require 15–25 Mbps minimum."
            },
            {
                "activity": "Streaming 8K",
                "min": "80 Mbps",
                "rec": "100–200 Mbps",
                "latency": "N/A",
                "notes": "Few services use 8K; extremely high bitrates."
            },
            {
                "activity": "Smart Home Devices",
                "min": "1 Mbps per device",
                "rec": "2 Mbps per device",
                "latency": "< 150 ms",
                "notes": "Cameras require more: 2–6 Mbps upload each."
            },
            {
                "activity": "Large File Downloads",
                "min": "10 Mbps",
                "rec": "100–500 Mbps",
                "latency": "N/A",
                "notes": "Speed dramatically affects completion time."
            },
            {
                "activity": "Cloud Backups / Uploads",
                "min": "5 Mbps",
                "rec": "20–50 Mbps upload",
                "latency": "N/A",
                "notes": "Upload speed is the bottleneck."
            },
            {
                "activity": "Multi-User Home (4–6 people)",
                "min": "50–100 Mbps",
                "rec": "300–600 Mbps",
                "latency": "< 50 ms",
                "notes": "Video streaming + gaming + smart devices."
            },
            {
                "activity": "Heavy Use Home (8+ people)",
                "min": "200 Mbps",
                "rec": "600 Mbps – 1 Gbps",
                "latency": "< 40 ms",
                "notes": "4K streams, work-from-home, gaming, cloud storage."
            },
        ]