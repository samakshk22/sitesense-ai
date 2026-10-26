# SiteSense AI — Multimodal Construction Intelligence Platform

A single-project capstone prototype built with Streamlit. SiteSense AI brings together visual PPE/site-hazard screening, concrete-crack triage, an editable early-stage cost estimator, and a weather-aware safety checklist.

## Features

- **PPE & site hazards:** upload a site photo and ask Gemini to describe visible PPE and potential hazards, with recommended controls and limitations.
- **Concrete crack triage:** upload a concrete photo for cautious visual observations and follow-up actions. It does not determine structural integrity.
- **Planning & valuation:** estimate a concept-stage INR budget from area, building type, editable rate, location factor, and contingency; view a cost breakdown and indicative milestone sequence.
- **Weather advisory:** enter forecast conditions and receive threshold-based precautions. This is a rule-based checklist, not a live forecast.
- **Privacy-conscious prototype:** no database and no server-side project storage. Without an API key, image analysis produces a clearly labeled simulated preview; it never pretends to analyze the image.
- **Export:** download AI screening reports as JSON.

## Requirements

- Python 3.10 or newer
- Optional Google Gemini API key for live image analysis

## Run locally on Windows

1. Open this folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages and start the app:

   ```powershell
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

4. The app opens in your browser. You can use the planning and weather tools without an API key. Set `GEMINI_API_KEY` in your environment before starting Streamlit to enable live image analysis. The app reads keys from server-side configuration and does not display them in the UI.

## Deploy to Streamlit Community Cloud

1. Push this repository to a **public GitHub repository**.
2. In Streamlit Community Cloud, create an app from the repository, select branch `main`, and set the main file path to `app.py`.
3. Deploy. The dependency list is in `requirements.txt`.
4. To enable Gemini on the hosted app, add `GEMINI_API_KEY = "your-key"` under the app's Streamlit Cloud **Secrets** settings. Never commit the key to GitHub.
5. Copy the deployed HTTPS URL and submit it together with the GitHub repository URL in the Skill Wallet portal.

## AI and data handling

The live image-analysis buttons send the selected image and task prompt to Google's Gemini API using the key supplied through the environment or Streamlit secrets. Do not upload images unless you are authorized to share them and have reviewed the provider's current data terms. The app does not intentionally save the image or AI report to a database; session state is used only to display the latest report while the app session is active. API usage may incur charges according to your Google account and model terms.

## Important limitations

This is a capstone decision-support prototype, not a certified PPE compliance tool, legal safety determination, structural engineering assessment, live weather service, or professional quantity survey. AI can miss hazards or produce incorrect details. Have competent site personnel verify observations, follow local regulations and approved safety plans, and obtain qualified engineering/cost advice before taking action. The estimator's default rates and schedule are illustrative assumptions; replace them with current local quotations and project scope.

## Project structure

```text
app.py          Streamlit user interface and application logic
requirements.txt Python package dependencies
README.md       Setup, deployment, and limitations
.gitignore      Ignores local environments and secrets
```
