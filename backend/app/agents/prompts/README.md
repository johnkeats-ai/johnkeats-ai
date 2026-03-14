# Agent Prompts

These are the system prompts used by each agent in the calibration pipeline. They are stored as separate files for readability and auditability. Each prompt defines a bounded task with structured JSON output. The adversarial prompts (PII Auditor, Annotation Validator) are deliberately independent — they do not share context with the agents they review.
