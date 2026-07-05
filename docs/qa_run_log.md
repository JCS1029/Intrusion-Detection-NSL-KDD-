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
Wrote docs\submission_checklist.md

Overall QA: PASS
