import google.generativeai as genai
import streamlit as st
import json
import pandas as pd
from sentiment_llm import system_prompt

API_KEY = "" # enter your API key here

if 'all_responses' not in st.session_state:
    st.session_state.all_responses = []
if 'has_processed_file' not in st.session_state:
    st.session_state.has_processed_file = False
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

def configure_gemini():
    if not API_KEY:
        st.error("API key not found. Please add it to Streamlit secrets or enter it in the sidebar.")
        return False
    try:
        genai.configure(api_key=API_KEY)
        return True
    except Exception as e:
        st.error(f"Failed to configure Gemini: {e}")
        return False

def call_gemini(prompt: str, model_name: str = "gemini-2.5-flash-lite") -> str:
    try:
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            top_p=0.2,
            top_k=40,
            max_output_tokens=512,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        st.error(f"Error calling Gemini: {e}")
        return None

def parse_json_response(response_text):
    if not response_text:
        return None
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None

def summarize_responses(responses: list):
    if not responses:
        st.warning("No responses to summarize.")
        return
    
    df = pd.DataFrame(responses)
    
    if "label" not in df.columns or "confidence" not in df.columns:
        st.error("Responses do not contain expected keys ('label', 'confidence').")
        st.write("Available columns:", df.columns.tolist())
        return
    
    st.subheader("Sentiment Distribution")
    label_counts = df["label"].value_counts()
    st.bar_chart(label_counts, use_container_width=True)
    
    st.subheader("Confidence vs Sentiment")
    df_viz = df.copy()
    label_map = {label: i for i, label in enumerate(df_viz["label"].unique())}
    df_viz["label_numeric"] = df_viz["label"].map(label_map)

    st.scatter_chart(df_viz, x="label_numeric", y="confidence", use_container_width=True, x_label="label", y_label="confidence")

    summary_prompt = f"Give a 20 word summary of sentiment analysis results: {label_counts.to_dict()}"
    summary = call_gemini(summary_prompt)
    if summary:
        st.subheader("Summary")
        st.write(summary)

configure_gemini()

st.title("Movie Review Sentiment Analysis with Gemini")

review = st.text_area("Enter a movie review for sentiment analysis:", value="" if 'review_text' not in st.session_state else st.session_state.review_text)
st.session_state.review_text = review

uploaded_file = st.file_uploader("Upload a file", type=["txt", "csv"])
if uploaded_file is not None and uploaded_file != st.session_state.last_uploaded_file:
    st.session_state.review_text = ""
    st.session_state.last_uploaded_file = uploaded_file

if uploaded_file:
    header_confirmation = st.checkbox("First row is header", value=False)

analyze = st.button("Analyze")
if review and analyze:
    with st.spinner("Analyzing sentiment..."):
        response = call_gemini(system_prompt + review)
        
        if response:
            st.subheader("Raw Response")
            st.write(response)
            
            parsed_result = parse_json_response(response)
            if parsed_result:
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(parsed_result, indent=2),
                    file_name="sentiment_analysis.json",
                    mime="application/json"
                )
            else:
                st.warning("Could not parse response as JSON. Check the raw response above.")

elif uploaded_file and analyze:
    reviews = []
    
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.warning("Uploaded CSV is empty.")
                st.stop()
            
            if header_confirmation:
                reviews = df.iloc[:, 0].dropna().astype(str).tolist()
            else:
                reviews = [df.columns[0]] + df.iloc[:, 0].dropna().astype(str).tolist()
        else:
            content = uploaded_file.read().decode("utf-8")
            if header_confirmation:
                reviews = content.splitlines()[1:]
            else:
                reviews = content.splitlines()
        
        if not reviews:
            st.warning("No reviews found in the uploaded file.")
            st.stop()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_responses = []
        for i, review_text in enumerate(reviews):
            if not review_text.strip(): 
                continue
                
            status_text.text(f"Processing review {i+1} of {len(reviews)}")
            progress_bar.progress((i + 1) / len(reviews))
            
            response = call_gemini(system_prompt + review_text)
            
            if response:
                parsed_result = parse_json_response(response)
                if parsed_result:
                    all_responses.append(parsed_result)
                else:
                    all_responses.append({
                        "label": "unknown",
                        "confidence": 0.0,
                        "reasoning": "Failed to parse response",
                        "raw_response": response
                    })
        
        progress_bar.empty()
        status_text.empty()
        
        if all_responses:
            st.session_state.all_responses = all_responses
            st.session_state.has_processed_file = True
            st.success(f"Processed {len(all_responses)} reviews")
    except Exception as e:
        st.error(f"Error processing file: {e}")

elif analyze and not review and not uploaded_file:
    st.warning("Please enter a movie review or upload a file for analysis.")

if st.session_state.has_processed_file and len(st.session_state.all_responses) > 0:
    col1, col2, col3 = st.columns(3)
    
    if 'show_responses_clicked' not in st.session_state:
        st.session_state.show_responses_clicked = False
    if 'show_summary_clicked' not in st.session_state:
        st.session_state.show_summary_clicked = False
    
    with col1:
        if st.button("Show All Responses", key="show_responses"):
            st.session_state.show_responses_clicked = True
            st.session_state.show_summary_clicked = False
    
    with col2:
        st.download_button(
            label="Download All Responses",
            data=json.dumps(st.session_state.all_responses, indent=2),
            file_name="sentiment_analysis_batch.json",
            mime="application/json"
        )
    
    with col3:
        if st.button("Visual Summary", key="visual_summary"):
            st.session_state.show_summary_clicked = True
            st.session_state.show_responses_clicked = False
    
    if st.session_state.show_responses_clicked:
        st.subheader("All Responses")
        st.json(st.session_state.all_responses)
    
    if st.session_state.show_summary_clicked:
        summarize_responses(st.session_state.all_responses)
