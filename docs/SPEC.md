# CoreFlow — Product Spec (v1)

## 1. Overview

CoreFlow is an open-source platform built by **Apollume Labs** that runs real-time computer vision on multiple camera streams. Users register cameras and “drop in” models (served by Triton), then CoreFlow launches DeepStream pipelines that decode, batch, infer, track, and output both annotated streams and detection events.

CoreFlow uses:

* **NVIDIA DeepStream** for video ingest + GPU decode + batching + tracking + OSD
* **NVIDIA Triton Inference Server** for model serving
* **TensorRT** for optimized inference engines (preferred runtime)

---

## 2. Goals

### v1 goals

* Register RTSP cameras
* Register Triton models (TensorRT/ONNX) from a model repository
* Create/start/stop pipelines (camera group + model + settings)
* Output:

  * RTSP preview stream (annotated)
  * JSON detection events (WebSocket + REST latest)
  * basic metrics (FPS/latency/dropped frames)

### Non-goals (v1)

* Training or dataset tooling
* Kubernetes multi-node scheduler (single host first)
* Advanced user management (basic local token optional)
* Complex analytics rules engine (basic thresholds only)

---

## 3. Target Users

* Developers building real-time CV systems
* Teams running multi-camera inference in industrial environments (safety, inspection, surveillance)
* Researchers who want a stable, reproducible inference stack

---

## 4. Key Concepts

### Camera

A video source (RTSP in v1). Stored as a resource and can be assigned to pipelines.

### Model

A Triton-served detector model. CoreFlow supports detectors that output bounding boxes (v1).

### Pipeline

A running DeepStream pipeline instance defined by:

* one or more cameras
* a single model
* runtime settings (batch size, threshold, tracker, output port)

---

## 5. Functional Requirements

### 5.1 Cameras

**Create camera**

* Input: `name`, `rtsp_url`, optional `tags`, `enabled=true`
* Validate RTSP connectivity (probe)
* Store in DB

**List cameras**

* Filter by `enabled`, search by name/tag

**Update camera**

* Enable/disable
* Update RTSP URL (re-probe)

**Delete camera**

* Not allowed if camera is used by a running pipeline (must stop first)

---

### 5.2 Models (Triton Model Registry)

**Register model**

* Input:

  * `name` (display name)
  * `triton_model_name`
  * `triton_model_version` (default `1`)
  * `labels_file` (optional)
  * `task=detector`
  * `input_shape` (e.g. 640x640) + format
  * `parser_type` (bbox parser family, v1: YOLO-style)
* Validation:

  * Triton model exists in model repo
  * Triton is reachable

**List models**

* Show status (available / missing / error)

**Delete model**

* Not allowed if in use by running pipeline

---

### 5.3 Pipelines

**Create pipeline**

* Input:

  * `name`
  * `camera_ids[]` (1..N)
  * `model_id`
  * settings:

    * `batch_size` (default = number of cameras)
    * `infer_interval` (default 0)
    * `threshold` (default 0.5)
    * `tracker_enabled` (default true)
    * `output_rtsp_port` (auto assign if not provided)
    * `width,height` (mux output resolution; default 1280x720)
* Output:

  * pipeline resource with state `CREATED`

**Start pipeline**

* Generates DeepStream config (from templates)
* Launches DeepStream runtime container/process
* State transition: `CREATED/STOPPED -> STARTING -> RUNNING` or `ERROR`

**Stop pipeline**

* Gracefully stops runtime container/process
* Transition: `RUNNING -> STOPPING -> STOPPED`

**Restart pipeline**

* Stop then start (same config)

**Pipeline state**

* `CREATED`, `STARTING`, `RUNNING`, `STOPPING`, `STOPPED`, `ERROR`

---

## 6. Outputs

### 6.1 Annotated Preview (RTSP out)

Each pipeline exposes an RTSP output endpoint:

* `rtsp://<host>:<output_rtsp_port>/live`

v1 requirement:

* It must work for at least 1–4 RTSP inputs on a single GPU host.

---

### 6.2 Detection Events (JSON)

CoreFlow produces normalized detection events.

**Event schema**

```json
{
  "pipeline_id": "pipe-01",
  "camera_id": "cam-01",
  "ts": 1730000000,
  "frame_id": 12345,
  "detections": [
    {"xyxy":[10,20,200,240], "score":0.92, "class":"person", "track_id": 7}
  ]
}
```

**Delivery**

* WebSocket: `/ws/pipelines/{pipeline_id}/events`
* REST: `GET /pipelines/{pipeline_id}/detections/latest`

v1: store latest per camera in memory (optional DB later).

---

### 6.3 Metrics

Per pipeline:

* `fps_per_camera`
* `avg_inference_latency_ms` (approx)
* `frames_dropped`
* `pipeline_uptime_seconds`
* `last_error`

Expose:

* `GET /pipelines/{id}/metrics`
* Prometheus endpoint: `GET /metrics`

---

## 7. System Architecture

### 7.1 Control Plane (Backend)

* FastAPI service
* Responsibilities:

  * resource CRUD (cameras/models/pipelines)
  * config generation
  * runtime orchestration (start/stop)
  * event aggregation + WS broadcast
  * metrics collection

### 7.2 Data Plane (DeepStream Runtime)

* DeepStream container executes GStreamer pipeline:

  * `uridecodebin/nvurisrcbin` → `nvv4l2decoder` → `nvstreammux`
  * inference via **nvinferserver (Triton)**
  * tracker (NvDCF default)
  * OSD overlay
  * sink: RTSP out
  * metadata: forwarded to backend

### 7.3 Triton Inference Server

* Serves models from `model_repo`
* Model types:

  * TensorRT engine (`model.plan`)
  * ONNX (`model.onnx`) optional

---

## 8. Configuration Generation

Backend generates:

* DeepStream app config for each pipeline
* `nvinferserver` config pointing to:

  * Triton host/port
  * `triton_model_name` + version
  * preprocessing + postprocessing settings

Templates live in:

* `infra/deepstream/templates/`

Generated configs live in:

* `runtime/deepstream_runner/pipelines/{pipeline_id}/`

---

## 9. API (v1)

### Cameras

* `POST /cameras`
* `GET /cameras`
* `PATCH /cameras/{id}`
* `DELETE /cameras/{id}`

### Models

* `POST /models`
* `GET /models`
* `DELETE /models/{id}`

### Pipelines

* `POST /pipelines`
* `GET /pipelines`
* `POST /pipelines/{id}/start`
* `POST /pipelines/{id}/stop`
* `GET /pipelines/{id}/metrics`
* `GET /pipelines/{id}/detections/latest`
* `WS /ws/pipelines/{id}/events`

---

## 10. Deployment (v1)

* Docker Compose:

  * `backend`
  * `triton`
  * `deepstream-runtime` (spawned per pipeline or reused with dynamic configs)

GPU requirement:

* NVIDIA GPU with drivers + container toolkit.

---

## 11. Milestones

### M0 — Repo skeleton (day 1)

* Compose boots backend + triton
* Health endpoints working

### M1 — One pipeline (days 2–5)

* Register camera + model
* Start pipeline → RTSP out works

### M2 — Events + metrics (days 5–8)

* Metadata forwarding → WS/REST
* Basic metrics

### M3 — Minimal UI (days 8–12)

* Pipeline dashboard + start/stop
* Show RTSP out URL

---

## 12. “Where to put it” (files)

Create:

* `docs/SPEC.md` (this file)
* `docs/ARCHITECTURE.md` (next file we’ll write)
