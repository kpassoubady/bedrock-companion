# Bedrock Companion

Hands-on lab companion for the "Building Production-Ready Agents with Amazon Bedrock AgentCore" course.

## Repository Structure

```
day1/
├── concepts/          # Post-class reference docs (read after course completion)
│   ├── 01-welcome-architecture-overview.md
│   ├── 02-core-execution.md
│   ├── 03-securing-agent-identity.md
│   ├── 04-state-visibility-memory-observability.md
│   └── 06-best-practices-wrap-up.md
└── labs/
    ├── 01-first-bedrock-request/       # Introductory lab (20 min)
    │   ├── README.md
    │   ├── start/       # TODO stubs for students
    │   └── solution/    # Complete working examples
    └── 05-operating-the-environment/   # Breakout lab (45 min)
        ├── README.md
        ├── start/
        └── solution/
```

## Concept Docs

The `day1/concepts/` directory contains dense reference documents for each session block. These are designed for post-course review — students can read them after class to reinforce learning. Each document covers:

- **01 — Architecture Overview:** Five focus capabilities, component comparison, practical implications
- **02 — Core Execution:** Runtime session isolation, Gateway protocol translation, architectural principles
- **03 — Identity:** Three-identity separation model, Agent Identity Directory, OWASP ASI03 mitigation
- **04 — Memory & Observability:** Memory types and strategies, trace span hierarchy, OWASP ASI06/ASI09
- **06 — Best Practices:** Cost management, runaway execution prevention, EDDOps, five production practices

## Labs

- `day1/labs/01-first-bedrock-request/` sends a first inference request through Amazon Bedrock's OpenAI-compatible Chat Completions API.
- `day1/labs/05-operating-the-environment/` deploys and inspects a governed agent on AgentCore Runtime.

Each lab directory contains its own setup and completion instructions.

## Related Repositories

- [bedrock-setup](https://github.com/kpassoubady/bedrock-setup) — Pre-class environment verification and installation steps.
