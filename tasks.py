# tasks.py
from crewai import Task
from typing import List
from memory import ShortTermMemory

def build_tasks(coordinator, strategist, compliance, risk, writer, user_prompt: str, short_mem: ShortTermMemory) -> List[Task]:
    """
    Builds the task graph for the fintech partnership recommender.
    NOTE: Input types & return shape unchanged. It should run as before.
    """
    # 0) Partnership ideation (dynamic, sector-aware, knowledge-grounded)
    t0 = Task(
        description=(
            f"User request/context: {user_prompt}\n"
            "Goal: Propose the strongest partnership concept aligned to the user's need.\n"
            "Step 1 — Infer sector & theme:\n"
            "- Parse the user request to infer a primary sector from {telco, retail, gig platforms, travel, education, healthcare}. "
            "If unclear, quickly shortlist two plausible sectors and pick one based on expected business impact and compliance feasibility.\n"
            "Step 2 — Ground with knowledge files (local RAG context):\n"
            "- Prefer retrieving snippets from knowledge/*.md files you have: "
            "[compliance_snippets.md, risk_pointers.md, sector_play_hints.md, partnership_archetypes.md, revenue_models.md, "
            "customer_journeys.md, technology_enablers.md, competitive_landscape.md].\n"
            "Step 3 — External RAG search (2–4 short snippets):\n"
            "- IMPORTANT: The RAG tool requires the argument named search_query. Call it like "
            "{\"search_query\": \"<sector keyword(s)> <product/partnership keyword(s)> <value keywords>\"}.\n"
            "- Example queries (adapt dynamically to the chosen sector):\n"
            "  • {\"search_query\": \"telco co-branded wallet loyalty cross-sell\"}\n"
            "  • {\"search_query\": \"retail scan and pay QR cashback tiers uptake\"}\n"
            "  • {\"search_query\": \"gig platform instant payout savings pots tax helper adoption\"}\n"
            "  • {\"search_query\": \"travel fx multi-currency card delay insurance lounge access\"}\n"
            "  • {\"search_query\": \"education campus id pay pocket money controls consent\"}\n"
            "  • {\"search_query\": \"healthcare pay in 4 clinics preventative rewards financing\"}\n"
            "Step 4 — Craft the concept:\n"
            "- Describe (a) Value proposition, (b) Incentive mechanics (loyalty/cashback/tiers), "
            "(c) GTM steps in <6 weeks (week-by-week milestones), (d) Basic KPIs (activation, txn freq, AOV, retention). "
            "Where relevant, incorporate elements from partnership_archetypes.md, revenue_models.md, and customer_journeys.md.\n"
            "Output — Keep concise, crisp, and grounded. Store a short final idea summary into short-term memory key 'idea'."
        ),
        expected_output="A concise 120-160 word partnership concept.",
        agent=strategist,
        output_json=None,
        callback=lambda out: short_mem.set('idea', str(out))
    )

    # 1) Compliance scan with RAG
    t1 = Task(
        description=(
            "Use the 'idea' from short-term memory as context.\n"
            "Retrieve the most relevant policy/compliance snippets (3–6) by combining:\n"
            "  • Local knowledge files: compliance_snippets.md, technology_enablers.md, customer_journeys.md (for consent points).\n"
            "  • External RAG search where needed.\n"
            f"Use web search to asses the compliance hints for {user_prompt}\n"
            "IMPORTANT: The RAG tool requires the argument named search_query. Call it like "
            "{\"search_query\": \"kyc aml pci dss privacy consent data residency vendor risk audit\"}.\n"
            "Checklist — Summarize pass/gap/unknown for: KYC/AML, PCI-DSS scope (tokenization, PAN handling avoidance), "
            "Privacy/Consent (explicit consent, purpose limitation, retention, portability), Data residency/localization, "
            "Vendor/SLA/Right-to-audit, and Logging/monitoring.\n"
            "Cite the file names used when applicable and store the result into 'compliance_summary'."
        ),
        expected_output="A short bullet list <=120 words with any cited file names.",
        agent=compliance,
        output_json=None,
        callback=lambda out: short_mem.set('compliance_summary', str(out))
    )

    # 2) Risk analysis
    t2 = Task(
        description=(
            "Inputs: 'idea' + 'compliance_summary' + original user request.\n"
            "Optionally query the RAG tool again for fresh angles using: "
            f"Use web search to asses relevancy of RAG tool search results and {user_prompt}\n"
            "{\"search_query\": \"fintech operational fraud security scalability regulatory partner market\"}.\n"
            "Use local knowledge from risk_pointers.md and competitive_landscape.md to structure risks by category: "
            "Operational, Fraud, Security, Scalability/Costs, Regulatory/Licensing, Vendor/Partner, and Market/Adoption.\n"
            "For each category, list the top 1–2 concrete risks and provide 1–2 actionable mitigations "
            "(e.g., rate limits, device fingerprinting, key rotation, SLAs, audits, A/B risk gates, rollout canarying). "
            "Store the result into 'risk_summary'."
        ),
        expected_output="Bullet points grouped by category, <=150 words.",
        agent=risk,
        output_json=None,
        callback=lambda out: short_mem.set('risk_summary', str(out))
    )

    # 3) Writer composes final report
    t3 = Task(
        description=(
            "Compose a concise Markdown report using 'idea', 'compliance_summary', and 'risk_summary'. "
            "Sections:\n"
            "1) Proposed Partnership Idea — one clear paragraph.\n"
            "2) Rationale & Value — reference sector dynamics (from sector_play_hints.md & competitive_landscape.md) and a 1-liner revenue model.\n"
            "3) Compliance Snapshot — summarize the pass/gap/unknown checklist (cite local file names if used).\n"
            "4) Risks & Mitigations — grouped bullets, prioritized.\n"
            "5) Next Steps (actionable) — 6-week GTM milestones (week 1–6), include an initial KPI target table (activation %, txn freq, AOV, CAC payback).\n"
            "Keep total under ~450 words. Add a short 'What we used' footer (web, RAG + short-term memory + knowledge/*.md)."
            "Finally add references list for web search results that are used.\n"
        ),
        expected_output="A single Markdown string.",
        agent=writer,
        output_json=None,
    )

    # 4) Coordinator QA
    t4 = Task(
        description=(
           "QA the Writer's draft for clarity, grounding, and consistency with the knowledge base. "
           "Checks: (a) Idea matches user intent, (b) Compliance snapshot aligns with compliance_snippets.md, "
           "(c) Risks reflect risk_pointers.md breadth, (d) KPIs are reasonable for early-stage pilots, "
           "(e) Tone is concise and partner-ready. If fine, finalize; else apply up to 3 small edits and return improved Markdown."
        ),
        expected_output="Final Markdown string.",
        agent=coordinator,
        output_json=None,
    )

    return [t0, t1, t2, t3, t4]
