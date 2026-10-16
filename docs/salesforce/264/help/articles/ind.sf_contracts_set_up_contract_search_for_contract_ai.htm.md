---
article_id: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
title: Configure Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_contract_search_for_contract_ai.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
fetched_at: 2026-10-13
---

# Configure Contract Search

If you need fast, reliable answers buried in thousands of contract documents, configure contract search. Ask a question in natural language and get the most relevant search results and AI-generated summaries.

IMPORTANT Starting Winter ’26, Salesforce recommends setting up Contract Search by deploying the Contract Document data kit. See Set Up Contract Search By Using Prebuilt Data Kit. Manual setup steps apply only to customers who configured Contract Search in Summer ’25.
Why Use Contract Search?
Go from hours of manual scanning to context-aware answers.
Surface critical obligations before they become compliance issues.
Every answer is grounded in the original clause with a clear rationale.
Permissions follow data governance rules.
Contract Search and Its Components
COMPONENT	PURPOSE
Data Cloud	Stores vector embeddings and metadata that power semantic search
Fileforce Ingestion	Pulls new contract PDFs, splits them into segments, and triggers indexing
Vector Indexing	Converts each segment into a dense vector that captures meaning
Data Governance	Applies field-level security, sharing rules, and audit trails
Agentforce Employee Agent (AEA)	Provides chat-style Q&A and multiturn conversations
Key Terminology
TERM	WHAT IT MEANS	WHY IT MATTERS
Embedding	A numeric vector that represents the semantics of a text snippet	Enables similarity search for meaning, not just keywords.
Vector Index	A database of embeddings plus metadata	Lets Contract Search find the closest semantic matches quickly.
Retrieval-Augmented Generation (RAG)	LLM technique that combines search results with prompts	Produces answers that are both context-aware and concise.
How Contract Search Works
Ingest & Encode
Contracts are split into segments (clauses, tables, paragraphs).
Each segment becomes an embedding and is stored in Data Cloud.
Ask a Question
Your question is also embedded.
The system compares it against millions of stored embeddings to find the closest matches.
Rank & Retrieve
Matches are sorted by similarity score and returned with clause text and document location.
Summarize with RAG
Top snippets feed a Large Language Model via domain-specific prompt templates.
The LLM returns a concise answer plus citations so you can verify the source.
What You Can Do
Query in plain English:"When does the master service agreement renew?"
See why it matched: Each result shows the clause plus a short snippet.
Get to the source: Download the contract document.
Chat with your contracts: Use AEA for follow-up questions without losing context.
Common Use Cases
TEAM	TYPICAL QUESTION	BENEFIT
Legal	"List all indemnity clauses with unlimited liability."	Accelerate risk reviews across thousands of agreements
Sales	"What are the renewal dates and price-increase caps for account X?"	Negotiate confidently with real-time contract intel
Procurement	"Show termination-for-convenience language in vendor contracts."	Identify supplier risks early
Security and Governance Highlights
Permission-aware results: Users only see clauses they’re allowed to view.
Audit trails: Every search and retrieval is logged for compliance.
Data residency: Embeddings stay inside your Data Cloud tenant.
Set Up Contract Search By Using Prebuilt Data Kit
Use a home or companion org architecture for centralized search, and deploy all required components in a single click with the prebuilt Contract Document data kit.
Manually Configure Contract Search
Set up Contract Search manually to get fast, reliable answers across thousands of contracts. Use natural language to ask questions and receive relevant results along with AI-generated summaries.
Contract Search Limitations
Review the functional and configuration limitations that impact how contract search indexes, retrieves, and processes contract data.
Agentforce for Contract Search
Use Agentforce to power AI-driven contract search. The Contract Document Overview topic lets contract managers and legal analysts summarize documents or ask questions about specific clauses. Customize the topic and prompt templates to match your business needs.
Search, Summarize, and Interact with Contracts Using AI
Use Contract Search with AI to query and analyze contract documents using natural language. You can view matching contracts, ask questions, summarize content, and preview or download contract documents.
Billing Considerations for Contract Search
Use of the Summarize Contract Document and Query Contract Document actions impacts credit consumption. These actions rely on Data Cloud for document indexing and querying, and invoke generative AI through Agentforce to deliver summaries and answers.
