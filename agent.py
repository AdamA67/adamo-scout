import anthropic
import json
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

def load_skill(skill_name):
    path = f"skills/{skill_name}/SKILL.md"
    with open(path,"r") as f:
        return f.read()

def run_skill(skill_name,user_message,context=None):
    system_prompt = load_skill(skill_name)

    if context:
        full_message = f"{context}\n\n{user_message}"
    else:
        full_message = user_message
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": full_message}
        ]
    )
    
    raw = response.content[0].text
    raw = raw.strip()
    print(f"RAW RESPONSE FROM {skill_name}:")
    print(repr(raw))
    print("---")
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)

def run_pipeline(job_brief):
    results={}

    # Step 1 - Analyst
    print("Running Analyst...")
    analyst_output = run_skill(
        "analyst",
        f"Here is the job brief:\n\n{job_brief}"

    )
    results["analyst"]=analyst_output

    # Step 2 - Researcher
    print("Running Researcher...")
    researcher_output = run_skill(
        "researcher",
        "Enrich this candidate profile with market intelligence",
        context=f"Analyst output:\n{json.dumps(analyst_output, indent=2)}"
    )
    results["researcher"] = researcher_output

    # Step 3 - Strategist
    print("Running Strategist...")
    strategist_output = run_skill(
        "strategist",
        "Build the search strategy based on this data.",
        context=f"Analyst output:\n{json.dumps(analyst_output, indent=2)}\n\nResearcher output:\n{json.dumps(researcher_output, indent=2)}"
    )
    results["strategist"] = strategist_output

    # Step 4 - Writer
    print("Running Writer...")
    writer_output = run_skill(
        "writer",
        "Write the outreach messages for this candidate profile.",
        context=f"Analyst output:\n{json.dumps(analyst_output, indent=2)}\n\nResearcher output:\n{json.dumps(researcher_output, indent=2)}\n\nStrategist output:\n{json.dumps(strategist_output, indent=2)}"
    )
    results["writer"] = writer_output

    # Step 5 - Scorer
    print("Running Scorer...")
    scorer_output = run_skill(
        "scorer",
        "Evaluate this search and provide the executive summary.",
        context = f"Analyst output:\n{json.dumps(analyst_output, indent=2)}\n\nResearcher output:\n{json.dumps(researcher_output, indent=2)}\n\nStrategist output:\n{json.dumps(strategist_output, indent=2)}\n\nWriter output:\n{json.dumps(strategist_ouput,indent=2)}"
    )
    results["scorer"]=scorer_output
    return results

