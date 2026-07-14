import json
import re
import requests
import config

def calculate_judge_metrics(question: str, context: str, actual_answer: str, expected_answer: str) -> dict[str, float]:
    """
    Invokes an isolated out-of-band Judge LLM role calculation 
    to output deterministic evaluation metadata scores.
    """
    judge_instruction = f"""You are an objective AI Quality Systems Auditing Engine.
Evaluate this automated RAG transaction cleanly across three metrics.

Context elements pulled by retriever:
\"\"\"
{context}
\"\"\"

User target query item:
"{question}"

Expected baseline reference truth:
"{expected_answer}"

Actual engine production output:
"{actual_answer}"

You must score the run on exactly these fields (values strictly bound between 0.0 and 1.0):
1. precision_at_k: Ratio of retrieved text pieces in the provided Context that directly contain data relevant to resolving the question.
2. faithfulness: Grounding verification score. Are ALL facts listed inside the Actual output directly stated inside the Context document text block? If any sentence relies on outside model training data or extrapolates details, score this 0.0.
3. answer_relevance: Does the Actual output answer precisely match the core questions posed by the user, ignoring string layout format changes?

Return your calculation response strictly matching this clean JSON structural format without markdown text wrappers:
{{
    "precision_at_k": 0.0,
    "faithfulness": 0.0,
    "answer_relevance": 0.0
}}
"""
    payload = {
        "model": config.JUDGE_MODEL,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": judge_instruction}]
    }
    
    fallback_metrics = {"precision_at_k": 0.0, "faithfulness": 0.0, "answer_relevance": 0.0}
    
    try:
        response = requests.post(config.API_URL, json=payload, headers=config.headers, timeout=30)
        response.raise_for_status()
        raw_content = response.json()["choices"][0]["message"]["content"].strip()
        
        # Strip markdown markers if the model generates them
        cleaned_json_string = re.sub(r"^```json|```$", "", raw_content, flags=re.IGNORECASE).strip()
        return json.loads(cleaned_json_string)
    except Exception as e:
        print(f"Evaluation scoring calculation skipped due to parser parsing/network exception: {e}")
        return fallback_metrics