from __future__ import annotations

import json
import os
from datetime import date
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from google.genai import types


APP_TITLE = "SiteSense AI"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #f5f7f8; }
    [data-testid="stSidebar"] { background: #10251e; }
    [data-testid="stSidebar"] * { color: #f3f8f4 !important; }
    [data-testid="stSidebar"] input { color: #14251f !important; }
    .hero { padding: 1.65rem 1.8rem; border-radius: 18px; color: white;
      background: linear-gradient(115deg,#123d2e 0%,#17634a 58%,#25825e 100%);
      margin: 0 0 1.25rem 0; box-shadow: 0 12px 28px rgba(24,75,55,.15); }
    .hero h1 { font-family: 'Manrope',sans-serif; font-size: 2rem; margin: 0 0 .35rem 0; color:white; }
    .hero p { margin:0; color:#d8eee3; font-size:1rem; }
    .eyebrow { color:#bdebd2; font-size:.72rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase; }
    .panel { background:#fff; border:1px solid #e6ece8; padding:1.1rem 1.25rem; border-radius:14px; }
    .small-note { color:#64746c; font-size:.86rem; }
    div[data-testid="stMetric"] { background:white; border:1px solid #e6ece8; padding:14px 16px; border-radius:14px; }
    .stButton button { border-radius:9px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse model output, tolerating a surrounding Markdown code fence."""
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("\n", 1)[-1]
        if candidate.endswith("```"):
            candidate = candidate[:-3]
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The AI response did not contain a JSON object.")
    result = json.loads(candidate[start : end + 1])
    if not isinstance(result, dict):
        raise ValueError("The AI response was not a JSON object.")
    return result


def ask_gemini(
    api_key: str,
    prompt: str,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> dict[str, Any]:
    """Send one text or image-and-text request to Gemini and return JSON."""
    client = genai.Client(api_key=api_key)
    contents: list[Any] = [prompt]
    if image_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    if not response.text:
        raise ValueError("The AI returned an empty response. Try again with a clearer input.")
    return parse_json_response(response.text)


def show_json_download(result: dict[str, Any], filename: str) -> None:
    st.download_button(
        "Download result (JSON)",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
        key=f"download_{filename}",
    )


def render_list(value: Any, empty_message: str = "No items returned.") -> None:
    if not isinstance(value, list) or not value:
        st.caption(empty_message)
        return
    for item in value:
        if isinstance(item, dict):
            title = item.get("title") or item.get("hazard") or item.get("item") or "Finding"
            detail = item.get("details") or item.get("description") or item.get("recommendation") or ""
            priority = item.get("priority") or item.get("severity")
            suffix = f" · {priority}" if priority else ""
            st.markdown(f"- **{title}{suffix}** — {detail}" if detail else f"- **{title}{suffix}**")
        else:
            st.markdown(f"- {item}")


def render_ai_result(title: str, result: dict[str, Any], filename: str) -> None:
    if result.get("_demo"):
        st.info("SIMULATED DEMO — this is illustrative content, not a result from your uploaded image or an AI model.")
    elif result.get("_error"):
        st.error(result["_error"])
        return
    st.subheader(title)
    summary = result.get("summary")
    if summary:
        st.write(summary)
    score = result.get("score")
    if isinstance(score, (int, float)):
        st.metric("AI-reported score", f"{score:.0f}/100")
    for key, label in (
        ("hazards", "Potential hazards"),
        ("findings", "Observations"),
        ("controls", "Recommended controls"),
        ("actions", "Recommended actions"),
        ("limitations", "Limitations and items to verify"),
    ):
        if result.get(key) is not None:
            st.markdown(f"**{label}**")
            render_list(result[key])
    st.caption("AI output is an initial screening aid. A competent site professional must verify all observations and decisions.")
    show_json_download(result, filename)


with st.sidebar:
    st.markdown("## 🏗️ SiteSense AI")
    st.caption("Construction intelligence workspace")
    st.divider()
    st.markdown("**AI connection**")
    try:
        cloud_api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        cloud_api_key = ""
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or cloud_api_key
    if api_key:
        st.success("Gemini configured · live analysis available")
    else:
        st.info("Demo mode · add GEMINI_API_KEY in Streamlit app Settings → Secrets")
    st.divider()
    st.markdown("**Project context**")
    project_name = st.text_input("Project name", "Northstar Commercial Build")
    project_location = st.text_input("Site location", "Pune, Maharashtra")
    st.caption("The API key is read from server-side secrets and is never displayed in the app.")
    st.divider()
    st.caption("Capstone 1 · Multimodal Construction Intelligence Platform")

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">Multimodal construction intelligence · {date.today().strftime('%d %b %Y')}</div>
      <h1>Build safer. Plan smarter.</h1>
      <p>{project_name} &nbsp;·&nbsp; {project_location} &nbsp;·&nbsp; AI-assisted site decision support</p>
    </div>
    """,
    unsafe_allow_html=True,
)

overview_tab, inspection_tab, planning_tab, weather_tab = st.tabs(
    ["Overview", "🦺 Safety & crack inspection", "📐 Planning & valuation", "🌦️ Weather advisory"]
)

with overview_tab:
    st.subheader("Project command center")
    st.write("Bring site-photo screening, early crack triage, cost planning, and weather-aware precautions into one workspace.")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Inspection modules", "2", "PPE + concrete cracks")
    metric_cols[1].metric("Planning tools", "2", "Cost + milestones")
    metric_cols[2].metric("AI mode", "Live" if api_key else "Demo", "Gemini vision" if api_key else "No model calls")
    metric_cols[3].metric("Data storage", "None", "No external database")

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Workflow")
        st.markdown(
            "1. **Inspect:** upload a site photo and request a PPE or crack-screening report.\n"
            "2. **Plan:** estimate an early-stage project budget and indicative work sequence.\n"
            "3. **Prepare:** check conditions against configurable weather safety thresholds.\n"
            "4. **Export:** download individual AI reports as JSON for review and record keeping."
        )
        st.warning("This capstone is a decision-support prototype, not a certified safety inspection, structural assessment, or quantity survey.")
    with right:
        st.markdown("### Project snapshot")
        st.markdown(
            f"**Project**  \n{project_name}  \n\n**Location**  \n{project_location}  \n\n**AI provider**  \n{'Gemini (' + MODEL_NAME + ')' if api_key else 'Not connected — demo mode'}"
        )
        st.markdown('<div class="small-note">Images are sent to Google Gemini only when you choose to run a live analysis. Review the provider’s data terms before uploading sensitive site images.</div>', unsafe_allow_html=True)

with inspection_tab:
    st.subheader("Image-based site screening")
    st.write("Select a screening task, provide a clear site image, and review the AI response as an initial checklist.")
    mode = st.radio("Screening task", ["PPE & site hazards", "Concrete crack triage"], horizontal=True)
    uploaded = st.file_uploader(
        "Upload a site image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Use a clear, authorized photo. Avoid uploading identifiable personal or confidential material.",
        key="inspection_image",
    )
    if uploaded:
        st.image(uploaded, caption=f"Image ready · {uploaded.name}", use_container_width=True)

    if mode == "PPE & site hazards":
        inspection_prompt = """You are an assistant for preliminary construction-site safety screening. Inspect the provided image only. Do not identify people. Do not claim certainty when details are obscured, and do not infer facts outside the image. Return a JSON object with exactly these keys: summary (string), score (integer 0-100 or null; describe it as a visual screening score, not a compliance certification), hazards (array of objects with title, details, priority), controls (array of strings), limitations (array of strings). Note visible PPE only when clearly observable; distinguish 'not visible' from 'not worn'. Recommend a competent-person verification. Do not claim the site is safe."""
        demo_payload = {
            "_demo": True,
            "summary": "Illustrative preview only. Connect Gemini and analyze an authorized site photo to generate image-specific observations.",
            "score": None,
            "hazards": [{"title": "Example only", "details": "No image analysis has been performed in demo mode.", "priority": "Verify on site"}],
            "controls": ["Confirm task-specific PPE requirements with the site safety plan.", "Have a competent person inspect the work area before work begins."],
            "limitations": ["This simulated preview is not based on your uploaded image."],
        }
    else:
        inspection_prompt = """You are an assistant for preliminary visual concrete-crack triage, not a structural engineer. Inspect the provided image only. Do not diagnose structural safety or estimate hidden crack depth. Return a JSON object with exactly these keys: summary (string), score (integer 0-100 or null; call it an image clarity/triage score, not a structural rating), findings (array of objects with title, details, priority), actions (array of strings), limitations (array of strings). Describe visible crack characteristics cautiously; state when a scale or context is missing. Recommend documenting width, length, location, date, and changes, and escalation to a qualified structural engineer for concerning or changing cracks."""
        demo_payload = {
            "_demo": True,
            "summary": "Illustrative preview only. Connect Gemini and analyze an authorized concrete photo to generate image-specific observations.",
            "score": None,
            "findings": [{"title": "Example only", "details": "No image analysis has been performed in demo mode.", "priority": "Verify on site"}],
            "actions": ["Photograph the area with a scale reference and note its location and date.", "Escalate widening, recurring, or potentially structural cracks to a qualified engineer."],
            "limitations": ["This simulated preview is not based on your uploaded image. A photo cannot determine hidden damage."],
        }

    if st.button("Analyze site image", type="primary", disabled=uploaded is None, key="analyze_image"):
        if not api_key:
            st.session_state["latest_inspection"] = demo_payload
        else:
            try:
                st.session_state["latest_inspection"] = ask_gemini(
                    api_key, inspection_prompt, uploaded.getvalue(), uploaded.type or "image/jpeg"
                )
            except Exception as exc:
                st.session_state["latest_inspection"] = {"_error": f"Analysis failed: {exc}"}
    if not uploaded:
        st.info("Upload a JPG, PNG, or WebP image to enable the screening workflow.")
    if "latest_inspection" in st.session_state:
        render_ai_result(
            "Screening report",
            st.session_state["latest_inspection"],
            "sitesense_inspection.json",
        )

with planning_tab:
    st.subheader("Early-stage cost plan")
    st.caption("Indicative planning estimate in INR. Replace the default rates with current local quotations before making commitments.")
    inputs = st.columns(3)
    area_sqft = inputs[0].number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=25_000, step=500)
    building_type = inputs[1].selectbox("Building type", ["Residential", "Commercial", "Industrial"])
    city_tier = inputs[2].selectbox("Location cost factor", ["Tier 1 city", "Tier 2 city", "Other"], index=1)
    base_rates = {"Residential": 2100, "Commercial": 2900, "Industrial": 2400}
    city_factors = {"Tier 1 city": 1.12, "Tier 2 city": 1.0, "Other": 0.92}
    rate = st.number_input(
        "Base construction rate (₹ / sq ft)", min_value=500, max_value=20000,
        value=base_rates[building_type], step=50,
        help="An editable assumption for concept-stage comparison only.",
    )
    contingency = st.slider("Contingency allowance", min_value=0, max_value=30, value=10, step=1)
    project_base = area_sqft * rate * city_factors[city_tier]
    total_estimate = project_base * (1 + contingency / 100)
    component_data = pd.DataFrame(
        {
            "Cost component": ["Materials", "Labour", "Equipment & preliminaries", "Overheads & other", "Contingency"],
            "Share": [0.56, 0.24, 0.10, 0.10, contingency / 100],
        }
    )
    component_data["Estimate (₹) on base"] = component_data["Share"] * project_base
    component_data.loc[component_data["Cost component"] == "Contingency", "Estimate (₹) on base"] = project_base * contingency / 100
    c1, c2 = st.columns([0.85, 1.15], gap="large")
    with c1:
        st.metric("Indicative total", f"₹{total_estimate:,.0f}", f"₹{total_estimate / area_sqft:,.0f} / sq ft including contingency")
        st.metric("Base estimate", f"₹{project_base:,.0f}", f"{city_factors[city_tier]:.2f} location factor")
        st.dataframe(component_data[["Cost component", "Estimate (₹) on base"]], hide_index=True, use_container_width=True)
    with c2:
        fig = px.pie(component_data, values="Estimate (₹) on base", names="Cost component", hole=0.58,
                     color_discrete_sequence=["#17634a", "#42a879", "#f1b84b", "#9ab8aa"])
        fig.update_layout(margin=dict(t=12, b=12, l=12, r=12), legend_title_text="", height=330)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Indicative milestone sequence")
    milestones = pd.DataFrame(
        [
            {"Milestone": "Design & approvals", "Share of duration": "15%", "Indicative duration": "4–8 weeks"},
            {"Milestone": "Site preparation & foundations", "Share of duration": "20%", "Indicative duration": "6–10 weeks"},
            {"Milestone": "Structure", "Share of duration": "30%", "Indicative duration": "10–18 weeks"},
            {"Milestone": "Envelope & services", "Share of duration": "20%", "Indicative duration": "8–14 weeks"},
            {"Milestone": "Finishes, testing & handover", "Share of duration": "15%", "Indicative duration": "6–12 weeks"},
        ]
    )
    st.dataframe(milestones, hide_index=True, use_container_width=True)
    st.caption("Estimate excludes land, taxes, financing, and project-specific scope unless included in your local rate. Obtain a professional quantity survey and design before procurement.")

with weather_tab:
    st.subheader("Weather-aware site precautions")
    st.write(f"Enter a forecast snapshot for **{project_location}**. This rule-based checklist is not a live weather forecast.")
    weather_cols = st.columns(3)
    condition = weather_cols[0].selectbox("Condition", ["Clear", "Cloudy", "Rain", "Thunderstorm", "High wind", "Heat advisory"])
    temperature = weather_cols[1].number_input("Temperature (°C)", min_value=-10, max_value=60, value=31)
    wind_speed = weather_cols[2].number_input("Wind speed (km/h)", min_value=0, max_value=200, value=12)
    rainfall = st.number_input("Rainfall intensity (mm/hour)", min_value=0.0, max_value=300.0, value=0.0, step=1.0)

    alerts: list[tuple[str, str]] = []
    if wind_speed >= 40 or condition == "High wind":
        alerts.append(("High", "Pause crane lifts, work at height, and handling of large panels until the site-specific wind limit is checked."))
    if rainfall >= 25 or condition in {"Rain", "Thunderstorm"}:
        alerts.append(("High" if condition == "Thunderstorm" or rainfall >= 25 else "Moderate", "Inspect drainage and excavation stability; protect electrical systems and suspend exposed work when conditions are unsafe."))
    if temperature >= 40 or condition == "Heat advisory":
        alerts.append(("High", "Apply the heat-stress plan: water, shade, rest breaks, acclimatization, and monitoring for symptoms."))
    if not alerts:
        alerts.append(("Routine", "Continue routine monitoring, maintain housekeeping, and verify conditions against the site emergency and task-specific plans."))

    for level, advice in alerts:
        if level == "High":
            st.error(f"{level} priority · {advice}")
        elif level == "Moderate":
            st.warning(f"{level} priority · {advice}")
        else:
            st.success(f"{level} · {advice}")
    st.markdown("**Before work starts**")
    st.markdown("- Recheck the official local forecast and site instruments; conditions can change quickly.\n- Confirm the site-specific stop-work thresholds, emergency contacts, and responsible supervisor.\n- Keep a dated record of forecast inputs and any work restrictions communicated.")
    st.caption("Thresholds shown are generic screening prompts, not engineering limits. Follow local regulations, manufacturer guidance, and the approved site safety plan.")

st.divider()
st.caption("SiteSense AI · Capstone prototype · Outputs can be incomplete or incorrect; professional verification is required.")
