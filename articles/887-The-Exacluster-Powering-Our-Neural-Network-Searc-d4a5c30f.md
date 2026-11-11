---
title: 'The Exacluster: Powering Our Neural Network Search Engine'
company: Exa
tag: 工程相关
date: 2025-05-15
url: https://exa.ai/blog/meet-the-exacluster
account: 
origin: harvest2-202607
---
Exa is a modern AI search engine with SERP API, website crawler tools, and deep research API. Power your app with web search AI and web crawling API.![](https://px.ads.linkedin.com/collect/?pid=9254756&fmt=gif)

[Introducing Exa Connect](https://exa.ai/connect)[Introducing Exa Connect: Access leading data providers.](https://exa.ai/connect)[Learn more](https://exa.ai/connect)

Products

[Search](/products/search)[Contents](https://exa.ai/docs/reference/contents-api-guide)[Deep](/products/deep)[Agent](/products/agent)[Monitors](https://exa.ai/docs/reference/monitors-api-guide)[Exa Connect](/connect)

Resources

[CareersWe're hiring](/careers)[Customers](/customers)[Partners](/partners)[Demos](/demos)[Contact us](/contact)[Research](/research)[Brand](/brand)

[Pricing](/pricing)

[Blog](/blog)

[Docs](https://exa.ai/docs)

[About](/about)

[Contact sales](/contact/sales)[Sign up](https://dashboard.exa.ai)

# Meet the Exacluster: the cluster training our next-gen search models

![Meet the Exacluster: the cluster training our next-gen search models](https://exa.imgix.net/h200_cluster.jpg)

[![Carlos Marques](https://exa.imgix.net/carlos-profile.webp)](https://www.linkedin.com/in/carlosmarquessilva/)

[Carlos Marques](https://www.linkedin.com/in/carlosmarquessilva/)

Technical Staff·May 15, 2025

---

### We Needed a Bigger Hammer

Exa recently purchased a 5 million dollar GPU cluster to train retrieval models over the web.

This cluster is a beast:

* 144 H200s
* 3,456 CPUs
* 270 TB NVMe SSD
* 20 TB GPU RAM
* 36 TB CPU RAM
* 100 KW operating power

It arrived at our datacenter in crates of bare-metal GPUs. And now it's running nearly 24/7, powering all concurrent workflows of our ML team.

As I write this, we're simultaneously embedding billions of pages, training a reranker, uploading checkpoints to a cache with S3 backups, all using a batch job framework that ensures reliability and reproducibility.

In this post, we'll explain in detail how we turned 18 hunks of bare metal into the streamlined infrastructure that powers our ML research.

### Two clusters

Since the beginning of Exa in 2021, we've believed that neural approaches to web retrieval will win over traditional approaches (this is now almost certainly correct). That's why we spent half our 2021 seed money on our first GPU cluster — 10 nodes with 8xA100 GPUs each.

By late 2024, we had 100x larger inference requirements and 5x more ML engineers running lots of training experiments in parallel. We needed more compute.

So we stood up a second, larger 18-node fleet — the Exacluster 😉

#### Cluster 1: 80 A100s

* 80xNVIDIA A100-80 GB (8 per node)
* 10xSupermicro AS-4124GO-NART+
* 6.4 TB HBM
* 960 EPYC threads (96 per node)
* 10 TB DDR4 system RAM
* ~80 TB Gen-4 NVMe
* Dual 100 GbE and NVLink v3 interconnect

![a100 gpu cluster](https://exa.imgix.net/a100_cluster.jpg)

#### Cluster 2: 144 H200s

![h200 gpu cluster](https://exa.imgix.net/h200_cluster.jpg)

* 144xNVIDIA H200-141 GB (8 per node)
* 18xLenovo ThinkSystem SR680a V3
* 20 TB HBM3
* 3,456 Xeon threads (192 per node)
* 36 TB DDR5-5600 system RAM
* 270 TB Gen-4 NVMe (12.8 TB per node)
* Mellanox ConnectX-7 + BlueField-3 DPUs

#### Quick‑Look Scorecard

|  | Old Cluster (A100) | Exa Cluster (H200) | Combined |
| --- | --- | --- | --- |
| Nodes | 10 | 18 | 28 |
| GPUs | 80 | 144 | 224 |
| Total GPU RAM | 6.4 TB | 20 TB | 26.4 TB |
| CPU Cores | 960 | 3,456 | 4,416 |
| System RAM | 10 TB | 36 TB | 46 TB |
| Local NVMe | 80 TB | 270 TB | 350 TB |
| FP16 PFLOPs\* | ~25 | ~143 | ~168 |

\*ball-park, aggregated theoretical flops without sparsity

What this means is that a run that used to take a week to complete can now finish in ~1 day. No longer compute-bound! (as much)

---

### The Wiring - How We Drive 224 GPUs Like One

Here's the five-layer stack that turns these bare servers into a compute beast we can control.

#### 1. Pulumi — Infrastructure as Code… that is actually code

Managing 28 bare-metal nodes, high-speed networks, and core services requires a repeatable process—not ad-hoc scripts. Pulumi provides that consistency.

* **Python over YAML** — configuration is written in Python, so engineers can use familiar control flow—loops, functions, tests—and quickly extend the setup.
* **Type safety** — Pulumi's typed API, validated with `mypy`, flags incorrect parameters before any provisioning begins.
* **Rich ecosystem** — Kubernetes, AWS, GCP, on-prem IPMI: one repo handles metal and cloud burst.

Pulumi's plan → apply workflow produces a clear diff of intended actions for every change, letting us review and confirm before it reaches production. If an update causes issues, the environment can be rolled back to its previous state with the same command.

Using Pulumi keeps the system consistent, auditable, and straightforward to evolve as hardware and software requirements grow.

#### 2. Ansible (+ Kubespray) — Automating the Bare-Metal Build

Pulumi orchestrates the full setup including a set of Ansible playbooks—most of which come directly from Kubespray, a maintained collection of Ansible roles for Kubernetes clusters. This turns each powered‑on server into a ready Kubernetes node.

#### What the playbooks do

* **System prep** — set the BIOS options, write the storage layout, install the OS, install base packages, load required kernel modules.
* **Kubernetes install** — use Kubespray roles to deploy the control‑plane or worker components, set kubelet and containerd options, and apply the chosen CNI (Calico).
* **Final join** — label the nodes, verify health, and return control to Pulumi so higher‑level services can be created.

Running Ansible/Kubespray under Pulumi gives us a single, repeatable path from bare metal to a consistent Kubernetes fleet, with all changes tracked and reproducible.

#### 3. NVIDIA GPU & Network Operators — The Full-Stack Advantage

NVIDIA's Kubernetes operators give us a clean, uniform way to manage every accelerator and NIC in the fleet—no manual SSH sessions, no node-specific scripts.

**GPU Operator**

* Installs and keeps current the driver, CUDA toolkit, and container runtime components.
* Exposes a device‑plugin DaemonSet so a pod can simply request `nvidia.com/gpu: 1.`
* Handles MIG partitioning and publishes DCGM metrics to Prometheus.

**Network Operator**

* Deploys OFED and sets up GPUDirect RDMA and RoCE on the ConnectX‑7 NICs and BlueField‑3 DPUs.
* Exposes a device‑plugin DaemonSet so a pod can simply request a specific network `"rdma/rdma_network": "1000"`
* Aligns driver versions with the GPU Operator to avoid incompatibilities.

Because everything is containerized, each node runs exactly the same stack and survives reboots or upgrades without drift. A new CUDA release becomes a version bump: nodes are cordoned and drained one at a time, upgraded and tested, then put back into service before the rollout advances.

This seamless hardware-to-software integration is a key reason NVIDIA dominates the datacenter AI market. Their operators close the gap between "I have GPUs" and "my workloads are running."

#### 4. Alluxio — Turning 350 TB of NVMe into a Single, High-Throughput Cache

Each new node ships with high-end Gen 4 NVMe; across 28 servers that's ~350 TB of low-latency storage connected by 400 Gb/s ethernet links. We use Alluxio to fuse those drives into one distributed cache while keeping S3 as the authoritative store.

**Write path**

* Data is written to the local NVMe tier.
* Depending on the policy, Alluxio either (a) flushes the blocks to S3 immediately (sync) or (b) uploads them in the background (async), so we don't get bottlenecked by our upload speed.

**Read path**

* Alluxio first looks for the object in its distributed NVMe cache.
* If the block is present, it serves it at local-disk speed; if not, the data is fetched from S3, cached, and then streamed to the job.

**Transparent interface**

* Buckets are pre-mounted and exposed through an S3-compatible endpoint.
* Existing code keeps its S3 URLs; no refactor needed.

**Cost control**

* Hot data stays on-prem, cutting on egress bills.
* We can evict the cache at any time—S3 remains the single source of truth.

The result is a unified, high-bandwidth data layer that lets GPUs stream training data at aggregate local‑disk speeds while preserving the durability and simplicity of S3.

#### 5. Flyte — The Brain That Schedules the Forge

When we listed what the scheduling layer had to deliver, the list was long:

* Code first, no YAML string configuration mess
* Ability to run locally for fast iteration speeds
* Multi-node training that understands PyTorch DDP
* Large batch jobs that can overflow to cloud GPUs on demand
* "One-click" developer pods for debugging
* S3 as the durable store
* In-task checkpointing and resume
* Reproducible environments and dependency pinning
* Dataset and artifact lineage
* Priority queues and fair-share policies

We evaluated several frameworks—Kubeflow, Airflow, Prefect, Dagster, etc—but Flyte was the only one that covered the full list without extensive custom work.

| Requirement | How Flyte addresses it |
| --- | --- |
| Code-first | A Python decorator turns a function into a task; DAGs compose naturally in code, no special DSL needed. |
| Versioned, reproducible runs | Each registration hashes the Docker image, requirements, and source code; every run is traceable and re-runnable. |
| Task caching & checkpointing | Built-in task cache and partial-run resume; failed jobs can restart from the last saved state. |
| Distributed training | Native plugins for PyTorchJob and MPIJob schedule multi-node GPU pods with topology-aware placement. |
| Large Batch Jobs | Using the Ray plugin + KubeRay we scale data jobs to hundreds of nodes, then shut down cleanly. |
| Cloud burst | A single project can target on-prem or cloud execution queues; scaling to thousands of spot GPUs is a configuration flag, not a rewrite. |
| Dataset lineage | Automatic tracking links inputs, outputs, and the exact code version that produced them. |
| Priority queues & quotas | Easily configurable Kubernetes priority classes and resource quotas; urgent inference fine-tunes preempt batch preprocessing. |
| Developer workflows | Flyte tasks are ordinary Python functions—run them locally, set breakpoints, and write unit tests exactly as you would for any other Python code. |

Flyte orchestrates node affinity, GPU topology, log routing to Loki, metrics to Prometheus, and artifact storage on S3 (with Alluxio caching) while honoring queue priorities. Engineers focus on writing code; the platform handles placement, scaling, and bookkeeping.

---

### Putting It All Together

Pulumi provisions everything → Ansible/Kubespray lays kube-roots → NVIDIA operators light up the accelerators → Alluxio feeds them at warp speed → Flyte keeps the assembly line humming.

The payoff?

* Launch a 7B parameter pre-train on 16 nodes with a single command.
* Queue 30 hyper-parameter sweeps in parallel—no manual GPU juggling.
* Spin up a 100-node AWS batch job as easily as running the workflow on your laptop; same code, just a different execution queue.
* Rebuild the entire cluster—from bare metal to 224 GPUs ready—in under one hour.

That's why we named this infrastructure Hephaestus, after the Greek god of blacksmithing. Hephaestus is the roaring forge where we shape our ML models.

If you're an engineer/researcher burning with ideas for semantic search models that need serious compute, Hephaestus is waiting. [https://exa.ai/careers](/careers)

![tmux for 18 nodes](https://exa.imgix.net/tmux_cluster.jpeg)

---

#### Cheers,

#### [Carlos Marques](https://www.linkedin.com/in/carlosmarquessilva/)

SEE MORE

[![SOTA Search Over Academic Publications](/images/blog/publications-benchmark.png)

#### SOTA Search Over Academic Publications

The Exa Team

July 23, 2026](/blog/publications-search)[![Introducing Exa Agent](/images/blog/exa-agent-card.jpg)

#### Introducing Exa Agent

The Exa Team

June 16, 2026](/blog/exa-agent)[![Exa raises $250M Series C to build the search engine for AIs](https://exa.imgix.net/team1.avif?w=800&q=60&auto=format%2Ccompress&fit=max)

#### Exa raises $250M Series C to build the search engine for AIs

Will Bryk

May 20, 2026](/blog/announcing-series-c)