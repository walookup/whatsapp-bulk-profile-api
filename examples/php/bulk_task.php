<?php
$key = getenv('WALOOKUP_API_KEY');
if (!$key) {
    throw new Exception('Set WALOOKUP_API_KEY');
}
$curl = curl_init('https://walookup.com/api/v1/bulk-tasks');
curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['X-API-Key: '.$key],
    CURLOPT_POSTFIELDS => [
        'product' => 'ws_profile_batch',
        'country' => 'US',
        'file' => new CURLFile('numbers.txt'),
    ],
]);
$response = curl_exec($curl);
$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);
if ($response === false || $status >= 300) {
    throw new Exception($response ?: curl_error($curl));
}
echo $response, PHP_EOL;
