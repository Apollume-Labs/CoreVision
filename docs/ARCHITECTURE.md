# CoreVision — System Architecture

## 1. Architecture Overview

**CoreVision** follows a **control-plane / data-plane** architecture designed for real-time, multi-camera computer vision workloads.

* **Control Plane**: manages configuration, lifecycle, orchestration, and observability.
* **Data Plane**: executes GPU-accelerated video pipelines.
* **Inference Plane**: serves models via a dedicated inference server.

This separation ensures:

* scalability
* fault isolation
* clean responsibility boundaries
* production stability

---

## 2. High-Level Architecture

```
                ┌──────────────────────────┐
                │        Frontend          │
                │  (Dashboard / UI)        │
                └───────────▲─────────────┘
                            │ REST / WS
                            │
┌───────────────────────────┴───────────────────────────┐
│                    Control Plane                       │
│                                                        │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐ │
│  │ Camera Mgmt  │   │ Model Mgmt   │   │ Pipeline   │ │
│  │              │   │ (Triton)     │   │ Orchestr. │ │
│  └──────┬───────┘   └──────┬───────┘   └──────┬─────┘ │
│         │                  │                  │       │
│         │           ┌──────▼──────┐           │       │
│         │           │ Config Gen  │◄──────────┘       │
│         │           └──────┬──────┘                   │
│         │                  │                          │
│  ┌──────▼─────────┐   ┌────▼──────────┐               │
│  │ Event Aggreg.  │   │ Metrics / Obs │               │
│  └────────────────┘   └────────────────┘               │
└───────────────────────────┬───────────────────────────┘
                            │
                            │ start / stop / config
                            │
┌───────────────────────────▼───────────────────────────┐
│                     Data Plane                         │
│                                                        │
│     ┌──────────────────────────────────────────┐     │
│     │           DeepStream Runtime              │     │
│     │                                          │     │
│     │  RTSP → Decode → Mux → Infer → Track     │     │
│     │                         │                │     │
│     │                         ▼                │     │
│     │                Triton Inference          │     │
│     │                                          │     │
│     │  OSD → RTSP Out  |  Metadata → Backend   │     │
│     └──────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Control Plane (Backend)

**Technology**

* FastAPI
* Python
* REST + WebSocket APIs
* Docker

**Responsibilities**

* Camera registry (RTSP sources)
* Model registry (Triton models)
* Pipeline lifecycle management
* DeepStream configuration generation
* Event aggregation and distribution
* Metrics exposure

**Key Principle**

> The control plane **never runs inference**.

---

### 3.2 Data Plane (DeepStream Runtime)

**Technology**

* NVIDIA DeepStream SDK
* GStreamer
* GPU-accelerated decode and processing

**Responsibilities**

* Ingest RTSP streams
* Decode video on GPU
* Batch multiple streams (`nvstreammux`)
* Send frames to inference
* Track objects
* Draw overlays
* Output annotated streams
* Emit structured metadata events

**Design Choice**

* Pipelines are **config-driven**, not hardcoded.
* Backend generates configs dynamically.

---

### 3.3 Inference Plane (Triton)

**Technology**

* NVIDIA Triton Inference Server
* TensorRT (preferred)
* ONNX (optional)

**Responsibilities**

* Serve models from a model repository
* Handle batching and concurrency
* Provide versioned models
* Expose gRPC / HTTP inference endpoints

**Why Triton**

* Decouples models from pipelines
* Enables hot-swapping models
* Production-proven at scale

---

## 4. DeepStream Pipeline Architecture

Each CoreVision pipeline follows this structure:

```
RTSP Source
   ↓
GPU Decode (nvv4l2decoder)
   ↓
Stream Mux (nvstreammux)
   ↓
Inference (nvinferserver → Triton)
   ↓
Object Tracker (NvDCF)
   ↓
OSD (bounding boxes, labels)
   ↓
RTSP Sink (preview output)
```

### Metadata Flow

* Inference + tracker metadata is extracted
* Converted to normalized JSON
* Forwarded to backend (HTTP / WS)

---

## 5. Configuration Flow

1. User creates pipeline via API
2. Backend validates:

   * cameras
   * model availability in Triton
3. Backend generates:

   * DeepStream app config
   * `nvinferserver` config
4. Runtime loads config and starts pipeline
5. Backend monitors pipeline state

All generated configs are stored per pipeline for traceability.

---

## 6. Model Integration Architecture

### Model Repository Structure (Triton)

```
model_repo/
  my_detector/
    1/
      model.plan
    config.pbtxt
```

### CoreVision Expectations

* Detector outputs bounding boxes
* Class IDs mapped via labels file
* Pre/post-processing defined in config

CoreVision does **not** assume YOLO internally — only bounding-box semantics.

---

## 7. Event Architecture

### Detection Event Contract

```json
{
  "pipeline_id": "pipe-01",
  "camera_id": "cam-01",
  "ts": 1730000000,
  "detections": [
    {
      "xyxy": [x1, y1, x2, y2],
      "score": 0.92,
      "class": "person",
      "track_id": 7
    }
  ]
}
```

### Delivery

* WebSocket (real-time)
* REST (latest snapshot)
* Optional file sink (JSONL)

---

## 8. Metrics & Observability

### Collected Metrics

* FPS per camera
* Approx inference latency
* Frame drop count
* Pipeline uptime
* Error state

### Exposure

* REST endpoints
* Prometheus `/metrics`

---

## 9. Scaling Strategy

### v1 (Single Node)

* Multiple cameras per GPU
* One Triton instance
* Multiple DeepStream pipelines

### Future

* Multi-GPU awareness
* Model-to-GPU affinity
* Multi-node orchestration (Kubernetes)

---

## 10. Design Decisions & Rationale

### Why DeepStream?

* GPU decode
* Multi-camera batching
* Production stability
* Zero-copy paths

### Why Triton?

* Model decoupling
* Versioning
* Batch scheduling
* Industry standard

### Why Backend-Controlled Pipelines?

* Dynamic reconfiguration
* Safe lifecycle management
* Auditable system state

---

## 11. What CoreVision Is NOT

* Not a training platform
* Not a notebook framework
* Not a Python OpenCV loop
* Not a monolithic inference service

**CoreVision is a real-time video inference platform.**

---

## 12. Next Documents

* `SPEC.md` — system requirements
* `ROADMAP.md` — milestones and future features
* `MODEL_ONBOARDING.md` — how users add models
* `DEPLOYMENT.md` — production deployment guide
