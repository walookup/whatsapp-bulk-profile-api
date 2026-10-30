# shell example

Bash, curl and Python 3 (JSON parsing).

Run **from the repository root**:

```bash
export WALOOKUP_API_KEY="YOUR_API_KEY"
bash examples/shell/bulk_task.sh
```

Submit once, then poll the same ID at least 30 seconds apart. Prints result metadata and its download URL; does not download the archive automatically.

For Python, Node.js, PHP and Shell, set `FILE=/path/to/your/list.txt` to choose an authorized input file. The bundled `examples/numbers.txt` only illustrates the input format and does not meet the production minimum. Go reads that path directly; replace it with an authorized file before use. See the [main README](../../README.md) for `ws_avatar_batch` limits and billing. Never submit fixture identifiers to production.

The request uses `service_type=ws_avatar_batch`. For phone tasks, send `country` before `file`; email and username tasks do not require it. `API_BASE_URL` can select a trusted local mock endpoint.
