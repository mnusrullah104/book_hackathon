<!-- SYNC IMPACT REPORT:
     Version change: 1.0.0 → 1.1.0
     Modified principles: [PRINCIPLE_1_NAME] → Spec-first development, [PRINCIPLE_2_NAME] → Technical accuracy and reproducibility, [PRINCIPLE_3_NAME] → Clarity for developers, [PRINCIPLE_4_NAME] → AI-native architecture, [PRINCIPLE_5_NAME] → End-to-end transparency
     Added sections: None
     Removed sections: None
     Templates requiring updates: .specify/templates/plan-template.md ⚠ pending, .specify/templates/spec-template.md ⚠ pending, .specify/templates/tasks-template.md ⚠ pending
     Follow-up TODOs: None
-->

# AI-Native Book with Embedded RAG Chatbot Constitution

## Core Principles

### Spec-first development (NON-NEGOTIABLE)
Every feature and implementation must begin with a formal specification; No code is written without a corresponding spec that defines goals, interfaces, and acceptance criteria; All development follows the Spec-Kit Plus methodology with traceable requirements.

### Technical accuracy and reproducibility
All code examples, configurations, and procedures must be technically accurate and fully reproducible; All implementations must work as documented with clear setup instructions; Free-tier compatible architecture required for accessibility.

### Clarity for developers and AI engineers
Documentation must be clear and accessible to both traditional developers and AI engineers; Code examples must be production-quality with appropriate explanations; Chapter progression must follow logical learning paths with practical applications.

### AI-native architecture (agents, RAG, vector DBs)
All system architecture must embrace AI-native patterns including agents, Retrieval-Augmented Generation (RAG), and vector databases; Systems must leverage modern AI infrastructure patterns with appropriate tooling; Architecture decisions must consider AI integration requirements from inception.

### End-to-end transparency
All processes must be transparent and traceable from specification to deployment; Build and deployment steps must be fully documented with reproducible environment variables; All system behaviors must be observable and auditable.

### Modular, non-filler content
Content must be modular and focused without unnecessary filler material; Each section must contribute meaningfully to the overall learning objectives; Production-quality code examples only, no placeholder or dummy implementations.

## Book Standards

Format: Markdown/MDX via Docusaurus for clear documentation structure; Clear chapter progression with integrated code examples and diagrams; Developer-focused explanations that bridge conceptual understanding with practical implementation.

## RAG System Requirements

Backend: FastAPI for reliable API services; AI: OpenAI Agents / ChatKit SDKs for intelligent interactions; Data: Neon Serverless Postgres + Qdrant Cloud (Free Tier) for scalable vector storage; Responses must be retrieval-grounded with no hallucinations, supporting both whole-book and user-selected text queries.

## Deployment Standards

GitHub Pages for public accessibility; Documented environment variables and build steps for reproducible setup; All deployment processes must be transparent and repeatable by readers.

## Governance

Constitution supersedes all other development practices; All implementations must comply with specified architectural constraints; Amendments require formal documentation and approval process; All code reviews must verify compliance with these principles.

**Version**: 1.1.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-12-18
