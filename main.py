# main.py
import json
import os
import time
from datetime import datetime
import config
from src.vector_store import get_chroma_client, get_collection, seed_database_if_empty
from src.rag_engine import execute_rag_pipeline
from src.evaluator import calculate_judge_metrics

def load_golden_eval_set(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_historical_drift_analysis(current_metrics: dict, history_file: str = "score_history.json"):
    """
    Appends the execution metrics record into the system timeline log 
    and checks if performance has regressed against the historical baseline trendline.
    """
    history_records = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encodings="utf-8") as f:
                history_records = json.load(f)
        except Exception:
            history_records = []
            
    # Calculate previous baseline running average values
    if history_records:
        historical_averages = {
            "precision_at_k": sum(r["metrics"]["precision_at_k"] for r in history_records) / len(history_records),
            "faithfulness": sum(r["metrics"]["faithfulness"] for r in history_records) / len(history_records),
            "answer_relevance": sum(r["metrics"]["answer_relevance"] for r in history_records) / len(history_records)
        }
        
        print("\n--- LONG-TERM ARCHITECTURAL DRIFT ASSESSMENT ---")
        drift_detected = False
        for metric, current_val in current_metrics.items():
            hist_avg = historical_averages[metric]
            delta = hist_avg - current_val
            print(f"• {metric.upper()}: Current run score [{current_val:.2f}] vs Historical Moving Baseline [{hist_avg:.2f}]")
            
            # Drift is visible over time as a trendline decrease
            if hist_avg > 0 and (delta / hist_avg) > config.DRIFT_ALERT_THRESHOLD:
                print(f"Warning Alert: Silent Performance Degradation Detected on metric component: '{metric}'!")
                drift_detected = True
                
        if not drift_detected:
            print("All pipeline validation variables remain within normal baseline tolerances.")
    else:
        print("\n First system baseline execution registered. Establishing green-zone historical trends marker...")

    # Record history state row onto persistent tape storage
    new_record = {
        "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": current_metrics
    }
    history_records.append(new_record)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_records,f, indent=4,)

def main():
    pdf_target_path = "data/Practice.pdf"
    eval_set_path = "data/eval_set.json"
    
    # 1. Enforce validation database seeding initialization steps
    seed_database_if_empty(pdf_target_path)
    
    # 2. Bind application resource handles
    chroma_client = get_chroma_client()
    collection = get_collection(chroma_client)
    
    # 3. Fetch immutable Golden Dataset list records
    dataset = load_golden_eval_set(eval_set_path)
    print(f"Loaded validation batch test metrics dataset. Total items count: {len(dataset)}")
    
    total_run_scores = {"precision_at_k": 0.0, "faithfulness": 0.0, "answer_relevance": 0.0}
    
    # 4. Process loop items sequentially one-by-one to avoid rate-limit exception errors
    for idx, item in enumerate(dataset, start=1):
        print(f"\n[Processing question {idx}/{len(dataset)}]")
        question = item["question"]
        expected = item["expected_answer"]
        
        # Call decoupled core retrieval/generation pipeline path
        actual, context = execute_rag_pipeline(question, collection)
        
        # Calculate isolated Judge evaluation matrices parameters
        scores = calculate_judge_metrics(question, context, actual, expected)
        print(f"   Scores -> Precision@k: {scores['precision_at_k']}, Faithfulness: {scores['faithfulness']}, Relevance: {scores['answer_relevance']}")
        
        # Aggregate incremental parameters
        for key in total_run_scores:
            total_run_scores[key] += scores[key]
            
        # Throttling delay to completely insulate the client from API utilization usage limits
        time.sleep(2)
        
    # 5. Compute mean performance metrics values for this complete batch execution
    batch_size = len(dataset)
    aggregated_run_averages = {k: v / batch_size for k, v in total_run_scores.items()}
    
    print("\n--- RUN COMPLETE AVERAGE SUMMARY SCORES ---")
    print(json.dumps(aggregated_run_averages, indent=4))
    
    # 6. Execute historical aggregation check analysis layer matching observer design pattern
    run_historical_drift_analysis(aggregated_run_averages)

if __name__ == "__main__":
    main()