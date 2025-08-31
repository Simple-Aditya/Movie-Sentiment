# Movie Sentiment App

This repository contains a Streamlit web app with Google Gemini-powered sentiment analysis logic for movie reviews.

## Files

- `app.py`: Streamlit app for interactive sentiment analysis and batch processing.
- `prompt.py`: Contains the system prompt used for LLM calls.

## Features
- **Single review analysis**: Paste a review and get sentiment (Positive/Negative/Neutral), confidence, explanation, and evidence phrases.
- **Batch analysis**: Upload a `.txt` or `.csv` file of reviews for batch sentiment marking.
- **Download results**: Export results as JSON.
- **Visual summary**: View sentiment distribution and confidence scatter plot for batch analysis only.

## Setup
1. **Clone the repo**
2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Set your Gemini API key** (line 7: var: API_KEY):
   Edit `app.py` for local testing.
4. **Run the app**:
   ```sh
   streamlit run app.py
   ```

## Usage
- Paste a review or upload a file.
- Click "Analyze".
- View results, download JSON, or see visual summary.

## Prompt Design
- The system prompt instructs Gemini to classify reviews and return a compact JSON object with label, confidence, explanation, and evidence phrases.
- Few-shot examples can be added in `prompt.py` for improved accuracy.
- In order to make the prompt the following structure is followed that has proved to be work:
    `persona -> goal -> rules -> flow of logic -> case handeling -> output format -> few shot examples`

## Notes
- API key should never be committed to the repo.
- Results may vary due to LLM subjectivity.
- For batch mode, CSV should have reviews in the first column.