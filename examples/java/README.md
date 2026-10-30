# java example

JDK 11 or newer (source-file launcher).

Run **from the repository root**:

```bash
export WALOOKUP_API_KEY="YOUR_API_KEY"
java examples/java/BulkTask.java TASK_ID
```

Query one existing task; it does not submit a new task.

Replace TASK_ID with the ID of a task you already submitted. The bundled `examples/numbers.txt` only illustrates the input format and does not meet the production minimum. Go reads that path directly; replace it with an authorized file before use. See the [main README](../../README.md) for `ws_avatar_batch` limits and billing. Never submit fixture identifiers to production.

The request uses `service_type=ws_avatar_batch`. For phone tasks, send `country` before `file`; email and username tasks do not require it. `API_BASE_URL` can select a trusted local mock endpoint.
