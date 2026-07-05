# Submission Checklist — Phase 8 QA

Generated: 2026-07-05 12:25 UTC

## Assignment requirements — Must pass

| Criterion | Status |
|-----------|--------|
| Public GitHub repo with all required artifacts | pending push |
| Notebook runs top-to-bottom after data download | PASS |
| NSL-KDD LR reproduced (±0.02) or deviation explained | PASS |
| ≥2 models with full metric suite (MCC, FAR); have 5 | PASS |
| Report evaluates ≥5 claims; have 7 | PASS |
| README contains required links and instructions | PASS |
| Submitted before July 10, 2026 23:59 | PASS (deadline not reached) |

## Assignment requirements — Should pass

| Criterion | Status |
|-----------|--------|
| AE+LR reproduced | PASS (author baseline MATCH) |
| SMOTE with/without comparison | PASS |
| Per-attack-type error analysis (R2L, U2R) | PASS |
| Feature redundancy formally analyzed | PASS |

## Grading rubric coverage

| Component | Primary artifact |
|-----------|------------------|
| Problem understanding & source selection (10) | Report §1, README |
| Summary quality (15) | Report §1 |
| Critical evaluation of claims (20) | Report §2, docs/critical_evaluation.md |
| Feature engineering analysis (10) | Report §3, Notebook §3 |
| Exploratory data analysis (15) | Notebook §2, Report §5 figures |
| Model training & comparison (15) | Notebook §4, Report §5 |
| Evaluation & error analysis (10) | Notebook §5–6, Report §5 |
| Code quality & software engineering (5) | src/, notebook structure |

## Manual steps (student)

1. Confirm public repo URL: https://github.com/JCS1029/Intrusion-Detection-NSL-KDD-
2. Email repo URL to examiner per `haifaUEX.pdf` course instructions.
3. Confirm repo is public and tag v1.0-submission is present.

## QA run excerpt

```
# QA Run Log — 2026-07-05T12:19:48.109273+00:00
OK: .venv-qa already has required packages (skipping reinstall)
OK: KDDTrain+.txt rows=125973
OK: KDDTest+.txt rows=22544
OK: artifact notebook
OK: artifact report_pdf
OK: artifact experiment_metrics
OK: artifact baseline_reproduction
OK: artifact critical_evaluation
OK: artifact reproducibility_notes
OK: artifact readme
OK: artifact requirements
OK: artifact src_modules
$ C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\.venv-qa\Scripts\python.exe -m ipykernel install --user --name ds-cyber-qa --display-name Python (ds-cyber-qa)
Installed kernelspec ds-cyber-qa in C:\Users\lovel\AppData\Roaming\jupyter\kernels\ds-cyber-qa
exit_code=0
$ C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\.venv-qa\Scripts\jupyter-nbconvert.exe --to notebook --execute C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\notebooks\ids_nsl_kdd_analysis.ipynb --output _qa_executed.ipynb --ExecutePreprocessor.timeout=1200 --ExecutePreprocessor.kernel_name=ds-cyber-qa
[NbConvertApp] Converting notebook C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\notebooks\ids_nsl_kdd_analysis.ipynb to notebook
C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\.venv-qa\Lib\site-packages\zmq\_future.py:718: RuntimeWarning: Proactor event loop does not implement add_reader family of methods required for zmq. Registering an additional selector thread for add_reader support via tornado. Use `asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())` to avoid this warning.
  self._get_loop()
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1783254160.928363   13576 port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1783254170.647057   13576 port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
I0000 00:00:1783254176.979860   13576 cpu_feature_guard.cc:227] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: SSE3 SSE4.1 SSE4.2 AVX, in other operations, rebuild TensorFlow with the appropriate compiler flags.
E0000 00:00:1783254177.630883   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_15}}
E0000 00:00:1783254222.405046   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_14}}
E0000 00:00:1783254230.571413   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_14}}
E0000 00:00:1783254269.751602   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_15}}
E0000 00:00:1783254317.212683   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_14}}
E0000 00:00:1783254328.433251   13576 node_def_util.cc:682] NodeDef mentions attribute use_unbounded_threadpool which is not in the op definition: Op<name=MapDataset; signature=input_dataset:variant, other_arguments: -> handle:variant; attr=f:func; attr=Targuments:list(type),min=0; attr=output_types:list(type),min=1; attr=output_shapes:list(shape),min=1; attr=use_inter_op_parallelism:bool,default=true; attr=preserve_cardinality:bool,default=false; attr=force_synchronous:bool,default=false; attr=metadata:string,default=""> This may be expected if your graph generating binary is newer  than this binary. Unknown attributes will be ignored. NodeDef: {{node ParallelMapDatasetV2/_14}}
[NbConvertApp] Writing 1450774 bytes to C:\Users\lovel\Desktop\data science in cyber\Intrusion-Detection-NSL-KDD-\notebooks\_qa_executed.ipynb
exit_code=0
```