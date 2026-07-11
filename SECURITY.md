# Security

Meridian reads `EXA_API_KEY` from the environment or `.env`. It is never hardcoded, logged, committed, or included in API responses.

Local SQLite cache, history, quota, and collection files are the only persisted user data. Set `MERIDIAN_HOME` to control where they are stored.

Report vulnerabilities privately through GitHub Security Advisories once the repository is published.
