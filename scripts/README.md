# Contract verification

From the repository root:

```sh
python3 -m pip install -r scripts/requirements-contract.txt
python3 scripts/check_contract.py
```

This checks OpenAPI validity, documented endpoints against the product manifest, supported task selectors, input limits and exact CSV columns when declared. Existing offline transport tests are also run when present. It never submits a paid API request.

## Enable GitHub Actions

The template `.github/api-contract-workflow.yml.example` is **inactive**. After an authorized maintainer has workflow-write access, copy it to `.github/workflows/api-contract.yml` and commit that file. The template runs on pushes and pull requests. No API key or repository write permission is required by its jobs.

Local validation works without enabling the workflow.
