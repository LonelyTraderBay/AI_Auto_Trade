# Local configuration fixtures

`base.yaml` and `environments/local.yaml` are JSON-compatible YAML documents.
JSON is a strict YAML 1.2 subset; using the subset keeps Phase 0 validation
deterministic without adding an unapproved YAML runtime dependency.

The effective precedence is:

```text
base -> environment
```

The local layer may not override risk, strategy, execution, venue or AI-owned
sections. These files contain no credential, secret, token, password or API key.
`sample-manifest.yaml` is a BACKTEST/SIMULATED/NONE fixture and does not authorize
deployment or external execution.

Validate from the repository root:

```bash
uv run ai-auto-trade config validate --manifest configs/sample-manifest.yaml
```
