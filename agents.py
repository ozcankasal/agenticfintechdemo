from crewai import Agent
from typing import Tuple
from crewai_tools import SerperDevTool

def build_agents(rag_tool, llm_name: str) -> Tuple[Agent, Agent, Agent, Agent, Agent]:
    coordinator = Agent(
        role="Coordinator",
        goal="Plan minimal flow and finalize a clear, auditable outcome.",
        backstory="Fintech product lead; crisp, risk-aware decisions.",
        allow_delegation=True,
        verbose=True,
        llm=llm_name,
    )

    strategist = Agent(
        role="PartnershipStrategist",
        goal=("Design a concrete sector partnership idea that maximizes user growth and revenue "
              "with a crisp value proposition and activation plan."),
        backstory=("Practical B2B2C strategist. Prefer measurable KPIs, simple incentives, and "
                   "go-to-market steps that launch in < 6 weeks. "
                   "Explore relevant info from web"
                   "When you use the RAG tool, ALWAYS call it with the argument name 'search_query', "
                   "e.g. {\"search_query\": \"telco cobranded wallet cashbacks loyalty cross-sell\"}."),
        tools=[SerperDevTool(), rag_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm_name,
    )

    compliance = Agent(
        role="ComplianceOfficer",
        goal="Check the idea against KYC/AML/PCI/Privacy basics using RAG, summarize status.",
        backstory=("Experienced compliance specialist. Cite policy fragments succinctly. "
                    "Find relevant info from web"
                   "Always invoke the RAG tool with {'search_query': '<keywords>'}."),
        tools=[SerperDevTool(), rag_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm_name,
    )

    risk = Agent(
        role="RiskAnalyst",
        goal="Outline operational/fraud/security/scalability/regulatory risks with 1-2 mitigations each.",
        backstory=("Risk professional prioritizing concise mitigation plans. "
                   "Find risk factors from web"
                   "When invoking RAG, use {'search_query': '<keywords>'}."),
        tools=[SerperDevTool(), rag_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm_name,
    )

    writer = Agent(
        role="Writer",
        goal="Produce an executive-ready Markdown report with sections and checklists.",
        backstory="Clear, structured technical writer.",
        allow_delegation=False,
        verbose=True,
        llm=llm_name,
    )

    return coordinator, strategist, compliance, risk, writer