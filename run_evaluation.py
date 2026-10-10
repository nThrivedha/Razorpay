"""
SentinelUPI — Evaluation & False-Positive Cost Analysis
--------------------------------------------------------
Executes model evaluation on held-out test set and prints detailed metrics:
- Precision, Recall, F1-Score, ROC-AUC
- False Positive Rate (FPR)
- Explicit False-Positive Cost & Friction Analysis
"""

import json
from dataset_evaluator import DatasetEvaluator

def execute_evaluation():
    evaluator = DatasetEvaluator()
    res = evaluator.run_heldout_evaluation()

    metrics = res["metrics"]
    conf = res["confusion_matrix"]
    fp_cost = res["false_positive_cost_analysis"]

    print("==========================================================================")
    print("           SENTINELUPI — HELD-OUT EVALUATION & COST REPORT                ")
    print("==========================================================================")
    print(f" Timestamp:                      {res['timestamp']}")
    print(f" Total Evaluation Samples:       {res['heldout_dataset_summary']['total_samples']}")
    print(f"   • Normal Baseline Samples:    {res['heldout_dataset_summary']['normal_samples']}")
    print(f"   • Injected Scam Samples:      {res['heldout_dataset_summary']['injected_scam_samples']}")
    print("--------------------------------------------------------------------------")
    print(" [1] CONFUSION MATRIX & ACCURACY")
    print(f"   • True Positives (TP):        {conf['true_positives']} (Scams correctly intercepted)")
    print(f"   • False Positives (FP):       {conf['false_positives']} (Normal transactions flagged)")
    print(f"   • True Negatives (TN):        {conf['true_negatives']} (Normal transactions approved)")
    print(f"   • False Negatives (FN):       {conf['false_negatives']} (Micro-coercion scams missed)")
    print("--------------------------------------------------------------------------")
    print(" [2] PERFORMANCE METRICS")
    print(f"   • Precision:                  {metrics['precision_percent']}%")
    print(f"   • Recall:                     {metrics['recall_percent']}%")
    print(f"   • F1-Score:                   {metrics['f1_score_percent']}%")
    print(f"   • False Positive Rate (FPR):  {metrics['false_positive_rate_percent']}%")
    print(f"   • ROC-AUC Score:              {metrics['roc_auc']}")
    print(f"   • Avg Inference Latency:      {metrics['avg_inference_latency_ms']} ms")
    print("--------------------------------------------------------------------------")
    print(" [3] EXPLICIT FALSE-POSITIVE COST & USER FRICTION ANALYSIS")
    print(f"   • FPR Stat:                   {fp_cost['fpr_stat']}")
    print(f"   • Practical Production Impact:{fp_cost['impact_summary']}")
    print(f"   • User Friction Mitigation:   {fp_cost['user_friction_mitigation']}")
    print("==========================================================================")

if __name__ == "__main__":
    execute_evaluation()
