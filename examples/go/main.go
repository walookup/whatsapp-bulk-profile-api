package main

import (
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

// 提交一个 ws_profile_batch 任务，然后查询一次状态。真实集成请把查询放进循环，间隔不短于 30 秒。
func main() {
	key := os.Getenv("WALOOKUP_API_KEY")
	if key == "" {
		panic("Set WALOOKUP_API_KEY")
	}
	var buf bytes.Buffer
	mw := multipart.NewWriter(&buf)
	_ = mw.WriteField("product", "ws_profile_batch")
	_ = mw.WriteField("country", "US")
	f, err := os.Open("numbers.txt")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	part, _ := mw.CreateFormFile("file", "numbers.txt")
	if _, err := io.Copy(part, f); err != nil {
		panic(err)
	}
	mw.Close()

	req, _ := http.NewRequest("POST", "https://walookup.com/api/v1/bulk-tasks", &buf)
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
