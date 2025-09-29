from crewai_tools import DirectorySearchTool

def build_rag_tool(knowledge_dir: str = "knowledge"):
    # IMPORTANT: This tool expects the argument "search_query" when invoked by agents.
    return DirectorySearchTool(
        directory=knowledge_dir,
        recursive=True,
        max_results=6,
    )