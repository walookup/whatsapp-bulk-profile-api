import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

// 查询一个已提交的 ws_avatar_batch 任务。提交用 multipart，见 README 的 curl 示例。
public class BulkTask {
    public static void main(String[] args) throws Exception {
        String apiKey = System.getenv("WALOOKUP_API_KEY");
        if (apiKey == null) throw new IllegalStateException("Set WALOOKUP_API_KEY");
        String baseUrl = System.getenv().getOrDefault("API_BASE_URL", "https://walookup.com");
        String taskId = args.length > 0 ? args[0] : System.getenv("TASK_ID");
        if (taskId == null) throw new IllegalStateException("Pass a task id");
        HttpRequest request = HttpRequest.newBuilder(URI.create(baseUrl + "/api/v1/bulk-tasks/" + taskId))
            .header("X-API-Key", apiKey)
            .GET()
            .build();
        HttpResponse<String> response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 300) throw new IllegalStateException(response.body());
        System.out.println(response.body());
    }
}
