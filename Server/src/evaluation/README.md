# Evaluation Module

This module provides tools to evaluate the performance, safety, and quality of the Medical Diagnostic System.

## Structure

- `metrics.py`: Defines the qualitative criteria (e.g., Fairness, Explainability).
- `evaluator.py`: Contains the `ComprehensiveEvaluator` class which uses Google Gemini to grade responses.
- `runner.py`: The main script to run the evaluation.
- `test_dataset.json`: A set of test cases used for evaluation.

## How to Run

1. **Generate Dataset**:
   first, generate the large comprehensive dataset:
   ```bash
   python generate_dataset.py
   ```

2. **Run Evaluation**:
   Run the runner script from the root `Server` directory or directly from `src/evaluation`.
   
   To run with the small dataset:
   ```bash
   python runner.py --dataset test_dataset.json --output report_small.md
   ```
   
   To run with the large generated dataset:
   ```bash
   python runner.py --dataset large_test_dataset.json --output report_full.md
   ```

## Key Improvements

- **Multi-turn Support**: The `runner.py` now supports multi-turn conversations. If the "input" in the dataset is a list `["Hello", "I have fever"]`, it will simulate a conversation maintaining context.
- **Robust Evaluator**: Powered by `gemini-1.5-flash` for faster and more reliable grading.
- **Large Dataset**: `generate_dataset.py` can create 50+ diverse test cases including Edge Cases, Safety, and Medical Complex scenarios.


## Understanding the "Query" Logic in Evaluation

The user specifically requested an explanation of the "query" aspect. In the context of this system evaluation:

### 1. User Input as Query
When `runner.py` executes a test case, it takes the `input` string from the JSON dataset. This input acts as the **Initial Query** to the Agent System.

### 2. Internal Query Transformation
Inside the Agent (specifically the `document_retriever`), the user's natural language input (e.g., "I have a headache") is often transformed into a **Search Query**.
- **Translation**: It may be translated to English (e.g., "Headache symptoms causes").
- **Keyword Extraction**: It may extract key medical terms.
- **Vector Search**: This query is used to semantic search the `FAQKnowledgeBase` or Checkups database.

### 3. Evaluation of Query Handling
The `ComprehensiveEvaluator` (Gemini) implicitly judges how well this query was handled by looking at the **Response**:
- **Relevance**: Did the system find relevant info? (Implies good query transformation).
- **Explainability**: Did the system explain *why* it thinks it's a specific disease? (Did it cite the retrieved documents?).

### 4. "Query" in the Dataset
In `test_dataset.json`, the `input` field is the query we are testing. We include different types of queries:
- **Direct Symptom Queries**: "I have fever".
- **Harmful Queries**: "Make poison" (To test safety filters).
- **Ambiguous Queries**: "I feel bad" (To test if the system asks for clarification).
