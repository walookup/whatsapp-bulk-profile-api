import { readFile } from "node:fs/promises";

const apiKey = process.env.WALOOKUP_API_KEY;
if (!apiKey) throw new Error("Set WALOOKUP_API_KEY");

const baseUrl = process.env.API_BASE_URL || "https://walookup.com";
const product = process.env.PRODUCT || "ws_profile_batch";
const country = process.env.COUNTRY || "US";
const path = process.env.FILE || "numbers.txt";

const form = new FormData();
form.set("product", product);
form.set("country", country);
form.set("file", new Blob([await readFile(path)]), "numbers.txt");

const created = await fetch(`${baseUrl}/api/v1/bulk-tasks`, {
  method: "POST",
  headers: { "X-API-Key": apiKey },
  body: form,
});
if (!created.ok) throw new Error(await created.text());
const taskId = (await created.json()).data.id;
console.log("submitted", taskId);

// 轮询间隔不得短于 30 秒，这是服务端的契约而不是建议。
for (;;) {
  await new Promise((r) => setTimeout(r, 30_000));
  const status = await fetch(`${baseUrl}/api/v1/bulk-tasks/${taskId}`, { headers: { "X-API-Key": apiKey } });
  if (!status.ok) throw new Error(await status.text());
  const data = (await status.json()).data;
  console.log(data.status);
  if (data.status !== "processing") {
    console.log(data);
    break;
  }
}
