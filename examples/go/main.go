package main

import (
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

// Submit once. Query the returned task ID separately, no more often than every 30 seconds.
func main() {
	key := os.Getenv("WALOOKUP_API_KEY")
	if key == "" {
		panic("Set WALOOKUP_API_KEY")
	}
	baseURL := os.Getenv("API_BASE_URL")
	if baseURL == "" {
		baseURL = "https://walookup.com"
	}
	var buf bytes.Buffer
	mw := multipart.NewWriter(&buf)
	_ = mw.WriteField("service_type", "ws_avatar_batch")
	_ = mw.WriteField("country", "US")
	f, err := os.Open("examples/numbers.txt")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	part, _ := mw.CreateFormFile("file", "numbers.txt")
	if _, err := io.Copy(part, f); err != nil {
		panic(err)
	}
	mw.Close()

	req, _ := http.NewRequest("POST", baseURL+"/api/v1/bulk-tasks", &buf)
	req.Header.Set("X-API-Key", key)
	req.Header.Set("Content-Type", mw.FormDataContentType())
	r, e := http.DefaultClient.Do(req)
	if e != nil {
		panic(e)
	}
	defer r.Body.Close()
	b, _ := io.ReadAll(r.Body)
	if r.StatusCode >= 300 {
		panic(string(b))
	}
	fmt.Println(string(b))
}
