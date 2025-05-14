# main.py
import os
from dotenv import load_dotenv
from datetime import datetime

# Load OpenAI API Key
load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# ---- Agent Node Functions ----

def researcher(state):
    topic = state.get("topic", "Agentic AI Capabilities for Financial Services")
    response = llm.invoke(f"Research and provide detailed points on: {topic}")
    return {**state, "research": response.content}

def summarizer(state):
    research_content = state.get("research", "")
    response = llm.invoke(f"Summarize the following for an executive audience:\n{research_content}")
    return {**state, "summary": response.content}

def validator(state):
    summary = state.get("summary", "")
    response = llm.invoke(
        f"Validate this summary for clarity and quality:\n{summary}\nRespond with 'PASS' or 'FAIL' and suggested edits if any."
    )
    return {**state, "validation": response.content}

# ---- LangGraph Workflow ----

workflow = StateGraph(dict)
workflow.add_node("researcher", researcher)
workflow.add_node("summarizer", summarizer)
workflow.add_node("validator", validator)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "summarizer")
workflow.add_edge("summarizer", "validator")
workflow.add_edge("validator", END)

app = workflow.compile()

# ---- Run Graph ----

result = app.invoke({"topic": "What are the Top Leadership Competencies required in today's Corporate World"})

print("\n--- Final Output ---")
print("✅ Research:\n", result["research"])
print("\n📝 Summary:\n", result["summary"])
print("\n🔍 Validation:\n", result["validation"])

# ---- Save Markdown ----

today = datetime.today().strftime('%Y-%m-%d')
filename = f"{today}-gen-ai-leading-competencies.md"
filepath = os.path.join("_posts", filename)

markdown = f"""---
title: "Benefits of Agentic AI capabilities in Financial Services"
date: {today}
layout: post
---

## Summary
{result['summary']}

## Research
{result['research']}

## Validator Comments
{result['validation']}
"""

with open(filepath, "w") as f:
    f.write(markdown)

print(f"\n✅ Markdown file saved to: {filepath}")