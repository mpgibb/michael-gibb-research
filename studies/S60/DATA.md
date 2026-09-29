# tau-bench source and available evidence

Publisher: Sierra Research, [original tau-bench repository](https://github.com/sierra-research/tau-bench), commit `59a200c6d575d595120f1cb70fea53cef0632f6b`. Citation: Yao et al. (2024), [tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045). [MIT license](https://github.com/sierra-research/tau-bench/blob/59a200c6d575d595120f1cb70fea53cef0632f6b/LICENSE), Copyright (c) 2024 Sierra.

The original repository contains retail and airline simulated task environments, action schemas, reference final-state/output evaluation and historical trajectories. Its current README warns that task versions are outdated and points to a successor. This study explicitly preserves the original benchmark version and does not claim successor performance.

The four historical JSON files and their exact SHA-256 values are in config.json. The publisher-labeled gpt-4o files contain four repeats for 115 retail and 50 airline tasks. The sonnet-35-new files contain eight repeats for the same task counts. Raw records contain model/user conversations and simulated customer details; no raw transcript is redistributed here.

Historical files provide task/trial identifiers, rewards, reward details, user-simulator cost and tool/message trajectories. They do not establish complete API cost, measured wall-clock latency, exact dated model snapshots or equivalent user-simulator configurations. Missing metadata remains null. Reanalysis is attributed to the publisher's recorded runs, not represented as newly executed agent trials.

New controlled trials require configured model snapshots and a bounded execution budget. Credentials are read from environment variables and are never part of research artifacts.
