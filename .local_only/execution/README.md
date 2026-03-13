# Execution Scripts

Execution scripts are deterministic Python scripts that perform specific actions like API calls, data processing, or file operations.

## Principles
- **Deterministic**: Given the same input, they should behave predictably.
- **Atomic**: Each script should do one thing well.
- **Documented**: Include comments on how to run and what inputs are expected.
- **Environment Driven**: Use `.env` for secrets and configuration.
