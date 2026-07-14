import requests
import config

def execute_rag_pipeline(question: str, collection) -> tuple[str, str]:
    """
    Executes a decoupled text context lookup loop from vector spaces 
    and bridges it into an isolated model request envelope.
    """
    # 1. Vector Search Query Execution
    results = collection.query(query_texts=[question], n_results=3)
    
    # 2. Defensive Edge Case Boundary Validation Gate Check
    if not results or not results.get("documents") or not results["documents"][0]:
        return "I do not possess context data elements to resolve this query.", ""
        
    context = "\n\n".join(results["documents"][0])
    
    # 3. Grounded Context Prompt Construction
    system_prompt = (
        "Answer the question using ONLY the context below. "
        "If the answer isn't in the context, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
    )
    
    payload = {
        "model": config.MODEL,
        "temperature": config.EVAL_TEMP,
        "messages": [{"role": "user", "content": system_prompt}]
    }
    
    # 4. Outbound Wire I/O Protocol Transaction Execution
    try:
        response = requests.post(config.API_URL, json=payload, headers=config.headers, timeout=30)
        response.raise_for_status()
        ai_output = response.json()["choices"][0]["message"]["content"]
        return ai_output, context
    except Exception as e:
        print(f"Network Wire / Model Query Latency Error encountered: {e}")
        return "Pipeline generation exception failure occurred.", context