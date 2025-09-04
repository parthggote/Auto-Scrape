# ACORD Student Challenge 2025: Insurance Form Analysis Pipeline

## 1. Overview

This project is an automated pipeline designed to tackle the ACORD Student Challenge 2025. It analyzes pet insurance (and related) application and claim forms from multiple global regions. The system scrapes forms from insurer websites, parses the documents (PDF, HTML), uses AI to extract and standardize fields, groups them into logical categories, merges them into a unified schema, and exports the final schema in JSON, XML, and Excel formats.

## 2. Architecture

The pipeline follows a modular, sequential process:

```
[Input: config/urls.json]
           |
           v
+--------------------+
|   1. Scraper       |  (Downloads raw HTML/PDF forms)
+--------------------+
           |
           v
+--------------------+
|   2. Parser        |  (Extracts text content from raw forms)
+--------------------+
           |
           v
+--------------------+
|   3. Extractor (AI)|  (Identifies and extracts form fields from text)
+--------------------+
           |
           v
+--------------------+
|   4. Grouper (AI)  |  (Categorizes extracted fields)
+--------------------+
           |
           v
+--------------------+
|  5. Schema Builder |  (Consolidates all forms into a master schema)
+--------------------+
           |
           v
+--------------------+
|   6. Exporter      |  (Saves the master schema in multiple formats)
+--------------------+
           |
           v
[Output: /outputs/final/{schema.json, schema.xml, schema.xlsx}]
```

## 3. Folder Structure

- `config/`: Contains configuration files, primarily `urls.json` for input URLs.
- `data/`: Stores intermediate data.
  - `raw/`: Raw downloaded PDF and HTML files.
  - `parsed/`: Plain text extracted from the raw files.
- `outputs/`: Contains the final and intermediate outputs of the pipeline.
  - `extracted/`: JSON files with fields extracted from each form.
  - `grouped/`: JSON files with fields grouped into categories for each form.
  - `final/`: The final, consolidated master schema in JSON, XML, and Excel formats.
- `src/`: All Python source code for the pipeline modules.
- `run_pipeline.py`: The main executable script to run the entire workflow.
- `requirements.txt`: A list of all Python dependencies for the project.

## 4. Modules

The core logic is encapsulated in the `src/` directory:

- `scraper.py`: Handles downloading of web content (HTML) and files (PDF).
- `parser.py`: Responsible for parsing different document types (PDF, HTML) to extract raw text.
- `llm_client.py`: An abstraction layer for communicating with AI models (like OpenAI or Ollama).
- `extractor.py`: Uses the LLM client to identify and extract structured data fields from the parsed text.
- `grouper.py`: Uses the LLM client to organize the extracted fields into logical groups.
- `schema_builder.py`: Merges the grouped data from all sources into a single, unified master schema.
- `exporter.py`: Converts the final JSON schema into other formats like XML and Excel.
- `utils.py`: Contains helper functions, such as logging configuration, used across modules.

## 5. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    If using a commercial LLM API, create a `.env` file and add your API key:
    ```
    OPENAI_API_KEY="your_api_key_here"
    ```

## 6. Usage

To run the full data processing pipeline, execute the main script with the path to your URL configuration file:

```bash
python run_pipeline.py config/urls.json
```

The script will process all URLs specified in `urls.json`, and the final, consolidated schemas will be saved in the `/outputs/final/` directory.
