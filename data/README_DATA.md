# DIEMS College Admission Enquiry Chatbot

## 1. Project Overview

The DIEMS College Admission Enquiry Chatbot is an NLP-based chatbot developed to assist students in getting admission-related information about Deogiri Institute of Engineering and Management Studies (DIEMS).

The chatbot uses Natural Language Processing (NLP), sentence embeddings, semantic search, and a structured knowledge base to understand user queries and retrieve relevant information.

It provides direct answers to questions related to college information, undergraduate programmes, M.Tech programmes, admission eligibility, fees, required documents, hostel facilities, and contact details.

The application is developed using Python and Streamlit, providing an interactive and user-friendly interface.

## 2. Objectives

- Provide quick responses to students' admission-related queries.
- Reduce the effort required to search through college documents.
- Understand natural-language questions using NLP techniques.
- Retrieve relevant information using semantic and keyword-based search.
- Provide accurate answers based on verified DIEMS information.
- Make admission information easily accessible through a chatbot interface.

## 3. Key Features

- **Natural Language Understanding:** Understands questions written in everyday language.
- **Semantic Search:** Finds relevant information using sentence embeddings.
- **Knowledge-Based Responses:** Retrieves information from structured college records.
- **Direct Answers:** Provides concise and relevant responses.
- **Multiple Information Categories:** Covers admissions, courses, fees, eligibility, documents, facilities, and contacts.
- **Interactive Interface:** Provides a user-friendly chatbot interface using Streamlit.
- **Fallback Responses:** Handles questions when reliable information is unavailable.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Streamlit | User interface |
| Sentence Transformers | Text embeddings |
| FAISS | Similarity search (optional) |
| NumPy | Vector operations and similarity search |
| JSONL | Knowledge-base storage |
| PyPDF | PDF text extraction |
| Pandas | Data processing |
| Requests | API communication |

## 5. Project Structure

```text
diems_admission_chatbot/
│
├── backend/
│   ├── config.py
│   └── services/
│       ├── ingest.py
│       ├── retriever.py
│       └── llm_service.py
│
├── data/
│   ├── knowledge_base.jsonl
│   └── documents/
│
├── templates/
│   └── faq_template.csv
│
├── index/
│
├── streamlit_app.py
├── build_index.py
├── requirements.txt
└── README.md
```

*Note: The project structure may vary depending on the files included in the implementation.*

## 6. Knowledge-Base Data

The case-study report describes FAQ, UG, M.Tech, 2026–27 category-wise fees, eligibility, document checklists, contacts, and selected facilities.

The report text supplied for implementation does not contain the actual official values or lists. Therefore, no college facts have been fabricated here.

### Add Verified Records

1. Copy `templates/faq_template.csv` to `faq.csv` and replace every `ENTER...` value with information checked against the current official DIEMS source.

2. Add records to `data/knowledge_base.jsonl`, with one JSON object per line.

Example:

```json
{"id":"faq_001","text":"Question: ... Answer: ...","metadata":{"category":"College information","source":"official brochure.pdf","page":1,"reviewed_on":"2026-11-16"}}
```

3. Add official PDF documents to `data/documents/`.

4. Text-based PDFs are extracted using PyPDF. Scanned or image-only PDFs require OCR before processing. OCR is not included in this version.

5. CSV/XLSX files in `data/` should have a `text` column, or `question` and `answer` columns. Include `category` and source columns wherever possible.

6. Rebuild the index after any data change:

```powershell
python build_index.py
```

### Important Notes

- Use only verified information from official DIEMS sources.
- Maintain the academic year, fee category, exact figures, and source page information.
- Do not upload personal applicant documents.
- Do not fabricate admission details or fee information.

## 7. Installation and Setup

### Step 1: Download the Project

Download or clone the project and extract it to your computer.

### Step 2: Open the Project Folder

Open the project folder in VS Code.

Open the terminal and execute:

```powershell
cd "D:\Engg Study Material\NLP\diems_admission_chatbot"
```

### Step 3: Create a Virtual Environment

If the virtual environment does not already exist:

```powershell
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Required Dependencies

```powershell
python -m pip install -r requirements.txt
```

## 8. Building the Knowledge Index

The chatbot uses sentence embeddings to convert knowledge-base records into numerical vectors.

These vectors are used to retrieve information relevant to the user's question.

To build the knowledge index, execute:

```powershell
python build_index.py
```

The generated index is stored in the index directory.

**Important:** Rebuild the index whenever the knowledge-base data is updated.

## 9. Running the Application

After activating the virtual environment, execute:

```powershell
python -m streamlit run streamlit_app.py
```

The application opens in the default web browser.

Users can enter their questions in the chatbot interface and receive relevant answers.

## 10. How the Chatbot Works

The chatbot follows a Retrieval-Augmented Generation (RAG)-style workflow when an LLM service is configured. Without an LLM service, it provides retrieval-based answers.

### Working Process

1. The user enters a question through the Streamlit interface.
2. The question is processed by the backend.
3. Sentence Transformers convert the question into an embedding.
4. The retriever searches the knowledge base using semantic similarity and keyword matching.
5. Relevant records are selected based on their retrieval scores.
6. The answer service prepares a concise response using the retrieved information.
7. The chatbot displays the response to the user.

### System Workflow

```text
        User
          |
          v
   Enter Question
          |
          v
   Streamlit Interface
          |
          v
   Question Processing
          |
          v
   Sentence Embeddings
          |
          v
   Semantic + Keyword Search
          |
          v
   Knowledge Base Retrieval
          |
          v
   Answer Generation
          |
          v
   Display Response
```

## 11. Example Queries

Users can ask questions such as:

- What is the B.Tech admission process at DIEMS?
- Which programmes are offered at DIEMS?
- What are the eligibility criteria for admission?
- What documents are required for B.Tech admission?
- What fee information is available?
- What hostel facilities are available?
- How can I contact the admission office?
- Is DIEMS an autonomous institute?

## 12. Stopping the Application

To stop the running Streamlit application, press:

```powershell
Ctrl + C
```

## 13. Future Enhancements

- Multilingual chatbot support.
- Voice-based question and answer functionality.
- Integration with updated official admission notices.
- Improved semantic retrieval and query understanding.
- Support for additional college documents.
- Enhanced conversation management.

## 14. Limitations

- The accuracy of responses depends on the quality and completeness of the knowledge base.
- Outdated information may produce outdated answers.
- Scanned PDFs require OCR processing.
- The chatbot cannot confirm real-time admission status, hostel availability, or current fee payments unless connected to an appropriate live data source.
- Unavailable information is handled using a fallback response.

## 15. Conclusion

The DIEMS College Admission Enquiry Chatbot provides an interactive solution for answering students' admission-related questions.

By combining NLP, sentence embeddings, semantic retrieval, and a Streamlit interface, the system helps users access relevant college information quickly and conveniently.

The project demonstrates how NLP-based conversational systems can simplify information retrieval and improve the accessibility of educational information.

## 16. Author

**Project:** DIEMS College Admission Enquiry Chatbot

**Domain:** Natural Language Processing (NLP)

**Programming Language:** Python

**Interface:** Streamlit