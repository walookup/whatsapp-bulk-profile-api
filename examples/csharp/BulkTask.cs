using System;
using System.Net.Http;
using System.Threading.Tasks;

// 查询一个已提交的 ws_avatar_batch 任务。提交用 multipart，见 README 的 curl 示例。
class BulkTask
{
    static async Task Main(string[] args)
    {
        var apiKey = Environment.GetEnvironmentVariable("WALOOKUP_API_KEY")
            ?? throw new Exception("Set WALOOKUP_API_KEY");
        var baseUrl = Environment.GetEnvironmentVariable("API_BASE_URL") ?? "https://walookup.com";
        var taskId = args.Length > 0 ? args[0] : Environment.GetEnvironmentVariable("TASK_ID")
            ?? throw new Exception("Pass a task id");
        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("X-API-Key", apiKey);
        var response = await client.GetAsync($"{baseUrl}/api/v1/bulk-tasks/{taskId}");
        var body = await response.Content.ReadAsStringAsync();
        response.EnsureSuccessStatusCode();
        Console.WriteLine(body);
    }
}
