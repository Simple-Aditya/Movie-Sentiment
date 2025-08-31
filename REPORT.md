# Mini-Report: LLM-Based Sentiment Marker (Movie Reviews)

## Prompt Design Choices

- **System Prompt:**  
  The prompt instructs Gemini to classify each review as Positive, Negative, or Neutral, and return a compact JSON object with:
  - `label`: sentiment class
  - `confidence`: float (0–1)
  - `explanation`: 1–2 sentence rationale
  - `evidence_phrases`: list of supporting phrases

- **Few-shot Examples:**  
  Included in the prompt for better consistency:
  ```
  Example output:
  {
    "label": "Positive",
    "confidence": 0.95,
    "explanation": "The review praises the acting and story.",
    "evidence_phrases": ["amazing acting", "great story"]
  }
  ```

## Failure Cases & Mitigation

- **Non-JSON Output:**  
  Sometimes Gemini returns extra text or malformed JSON.  
  *Mitigation:* Added robust parsing logic to extract JSON from the response.

- **Ambiguous Reviews:**  
  Neutral or mixed reviews sometimes misclassified.  
  *Mitigation:* Prompt explicitly asks for "Neutral" if sentiment is unclear.

- **Low Confidence:**  
  For very short or vague reviews, confidence may be low.  
  *Mitigation:* Confidence is always shown, and explanation is grounded in review text.

## Notes

- Model: `gemini-2.5-flash-lite` via Google Generative AI API
- Temperature: 0.1 for evaluation (deterministic)