# Contract verification

From the repository root:

```sh
python3 -m pip install -r scripts/requirements-contract.txt
python3 scripts/check_contract.py
```

This checks OpenAPI validity, documented endpoints against the product manifest, supported task selectors, input limits and exact CSV columns when declared. Existing offline transport tests are also run when present. It never submits a paid API request.

For legacy CheckNumber/NumberChecker task catalogs, opt in to a read-only, anonymous live drift check:

```sh
python3 scripts/check_contract.py --live
```

This compares catalog IDs, availability, upload bounds and minimum billable quantities. Network failure is reported as a failure, not silently treated as a pass. Other API families do not expose this catalog contract; the checker reports that live comparison is unavailable for them.

## Enable GitHub Actions

The template `.github/api-contract-workflow.yml.example` is **inactive**. After an authorized maintainer has workflow-write access, copy it to `.github/workflows/api-contract.yml` and commit that file. The template runs on pushes and pull requests, and offers a manual live-catalog check. No API key or repository write permission is required by its jobs.

The template is kept inactive because the current publishing credential cannot write GitHub Actions workflow files. Local validation remains usable immediately.
