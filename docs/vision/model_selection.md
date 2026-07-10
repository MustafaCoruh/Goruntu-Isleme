# Person Detector Model Selection

## Selected model

**YOLOX-Nano ONNX** is selected for `models/person_detector.onnx`.

## Why this model was selected

| Criterion | Evaluation |
| --- | --- |
| YOLO-based small model | YOLOX-Nano is a compact YOLO-family detector with about 0.91M parameters and 1.08 GFLOPs at 416x416 input. |
| ONNX format | The YOLOX project publishes/export supports ONNX models for ONNX Runtime deployment. |
| CPU speed | The Nano variant is the smallest YOLOX model and is the best fit for the 5-10 FPS CPU target, subject to CPU generation, camera resolution, preprocessing, and postprocessing cost. |
| OpenVINO optimization | YOLOX documentation supports OpenVINO deployment; if OpenVINO conversion is required, export with opset 10 or convert the selected ONNX artifact with Model Optimizer. |
| Offline operation | The ONNX artifact can be copied into the operational environment and loaded locally without network access. |
| Person-only detection | The model is COCO-trained. Runtime filtering must keep only COCO class id `0` (`person`) and discard all other classes. |
| Portability | ONNX is runtime-agnostic and can be used with ONNX Runtime CPU, OpenCV DNN, or converted to OpenVINO IR. |
| Corporate licensing | YOLOX is distributed under Apache-2.0, which is generally suitable for commercial/corporate use when notices and license obligations are preserved. |

## Considered alternatives

| Alternative | Decision |
| --- | --- |
| Ultralytics YOLOv8n/YOLO11n ONNX | Rejected for this repository because the default open-source license is AGPL-3.0; commercial closed-source deployments generally need a separate commercial license review. |
| YOLOX-Tiny ONNX | Kept as a fallback if YOLOX-Nano accuracy is insufficient. It is still small, but has higher compute cost than Nano. |
| Larger YOLOX-S/M/L variants | Rejected for the current CPU-first 5-10 FPS target because compute and model size increase significantly. |

## Deployment notes

1. Keep the model file at:

   ```text
   models/person_detector.onnx
   ```

2. Preprocess frames to the model input size used by the artifact, expected to be `416x416` for YOLOX-Nano.
3. Run inference with ONNX Runtime CPU provider for baseline offline deployment.
4. Apply score thresholding and NMS in the application.
5. Filter final detections to COCO `person` only:

   ```python
   PERSON_CLASS_ID = 0
   detections = [d for d in detections if d.class_id == PERSON_CLASS_ID]
   ```

6. If CPU throughput is below target, convert the ONNX artifact to OpenVINO IR and benchmark OpenVINO CPU inference.

## Source references used for selection

- YOLOX official repository: `https://github.com/Megvii-BaseDetection/YOLOX`
- YOLOX ONNX Runtime documentation: `https://yolox.readthedocs.io/en/latest/demo/onnx_readme.html`
- YOLOX paper: `https://arxiv.org/abs/2107.08430`

## Artifact note

The intended artifact is the official/pre-converted YOLOX-Nano ONNX model. Network access from the execution environment returned HTTP 403 for GitHub/Hugging Face binary downloads during this change, so `models/person_detector.onnx` is committed as a documented artifact pointer rather than the full binary model. Replace it with the downloaded YOLOX-Nano ONNX binary before production packaging if binary artifacts are required in Git.
