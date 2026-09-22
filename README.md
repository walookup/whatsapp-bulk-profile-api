# WhatsApp Bulk Profile Check — `ws_profile_batch` | WA Lookup

WhatsApp bulk profile check returns the profile fields for each number: avatar URL and category, estimated age band, gender, and skin tone. It suits segmenting large lists into audiences. The result contains only the profile fields listed above — never chat history or message content.

This is the official WA Lookup example repository for **one** bulk product, `ws_profile_batch`. It is an asynchronous task: upload a file, get a task id immediately, poll the task, and download the result file when it finishes.

- **Product page:** https://walookup.com/products/ws_profile_batch
- **API documentation:** https://walookup.com/api-docs
- **API base URL:** `https://walookup.com`
- **Authentication:** `X-API-Key`
- **Get an API key:** https://walookup.com/register

## What is it usually used for?

- Audience segmentation
- Targeted list splits
- Avatar asset collection
- First-pass account authenticity

## What does the result file contain?

| Column | Example | Meaning |
|---|---|---|
| `number` | `17253100591` | The submitted number. |
| `activated` | `yes` | Whether the number is registered on WhatsApp. |
| `avatar` | `<image url>` | Avatar URL. |
| `category` | `individual portrait` | Avatar category, e.g. individual portrait. |
| `gender` | `male` | Gender estimated from the avatar. |
| `age` | `25` | Age band estimated from the avatar. |
| `skin_color` | `south_asian` | Skin tone estimated from the avatar. |
| `hair_color` | `black` | Hair colour estimated from the avatar. |
| `isb` | `2` | Business account flag. |

The result is a **point-in-time signal**, not a verdict, and not identity data. It describes what the provider reported at the moment the task ran.

## How do I submit a task?

Upload a `.txt` or `.csv` with **one phone number per line**, 1,000–100,000 valid entries. A number list must come from a **single country**, given as `country` — the upstream uses it to expand bare national numbers.

```bash
curl -X POST 'https://walookup.com/api/v1/bulk-tasks' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -F 'product=ws_profile_batch' \
  -F 'country=US' \
  -F 'file=@numbers.txt'
```

The response returns the task id and `status=processing`, along with the server-side quote taken before processing starts.

## How do I poll a task and download the result?

```bash
curl -fsS 'https://walookup.com/api/v1/bulk-tasks/TASK_ID' -H 'X-API-Key: YOUR_API_KEY'
```

`status` is `processing`, `success` or `failed` — there is no progress percentage to poll for. **Do not poll more often than once every 30 seconds.** When the task succeeds the response carries the result-file download link.

## Bulk task or realtime check?

`POST /api/v1/bulk-tasks` (this repository) takes a file of 1,000–100,000 entries and answers later — that is the shape for list cleaning, campaign preparation and enrichment runs. A **realtime** check (`POST /api/v1/check`, or `POST /api/v1/batch-check` for up to 100 identifiers) answers inside the same HTTP response, for a signup form or a live lookup. The two are separate endpoints and are not interchangeable; see the other repositories under [walookup](https://github.com/walookup).

## What about billing?

The whole file is reserved on submit. When the task finishes you are charged only for the entries that were actually checked and the remainder is returned. A failed task is refunded in full.

## What are the limits and error codes?

| Limit | Value |
|---|---|
| Entries per task | 1,000–100,000 |
| File formats | `.txt`, `.csv`, one entry per line |
| Products per task | 1 (`ws_profile_batch`) |
| Country | required, exactly one per task |
| Poll interval | no more than once per 30 seconds |

`40000`/`40001` are request or file errors; `40100` is an invalid key; `40200` is insufficient balance; `42900` is rate limited — honour `Retry-After`; `50300` is temporary maintenance. `GET /api/v1/balance` returns the current balance in `data.balance_micros`.

Keep the key on a trusted server and read it from `WALOOKUP_API_KEY`. Never commit it or expose it in production browser code.

## Runnable examples in seven languages

| Language | Example |
|---|---|
| Python | [`examples/python`](examples/python) |
| Node.js | [`examples/nodejs`](examples/nodejs) |
| Go | [`examples/go`](examples/go) |
| Java | [`examples/java`](examples/java) |
| C# | [`examples/csharp`](examples/csharp) |
| PHP | [`examples/php`](examples/php) |
| Shell / curl | [`examples/shell`](examples/shell) |

## Official resources and responsible use

- **This product:** https://walookup.com/products/ws_profile_batch
- **All products:** https://walookup.com/products
- **Documentation:** https://walookup.com/api-docs
- **Registration:** https://walookup.com/register
- **Pricing:** https://walookup.com/pricing
- **OpenAPI contract:** [`openapi.yaml`](openapi.yaml)
- **License:** [MIT](LICENSE) for the sample code

Submit only data you are authorized to process, and comply with applicable privacy laws and platform terms. Report the signal you received as a signal; do not relabel it downstream as a conclusion it does not support.

---

*Last reviewed: 2026-09-22 · Maintained by WA Lookup. Canonical documentation: https://walookup.com/api-docs*
