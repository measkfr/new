import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import os

print("\n" + "="*70)
print("🤖 TELEGRAM CHAT MESSAGE BOT")
print("="*70)

# Setup Browser 1 (Digit: 8)
service = Service(r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe')

options1 = webdriver.ChromeOptions()
options1.add_argument("--start-maximized")
options1.add_argument("--user-data-dir=C:\\Users\\rosha\\browser1_data")

browser1 = webdriver.Chrome(service=service, options=options1)

print("\n🚀 BROWSER 1 STARTING (DIGIT: 8)")
print("="*50)

# Step 1: Open Telegram and login
print("📱 Opening Telegram...")
browser1.get("https://web.telegram.org/a/")

print("\n🔑 PLEASE LOGIN WITH QR CODE IN BROWSER 1")
print("Wait until you can see chat messages")
input("Press Enter AFTER you are logged in and can see chat interface: ")

# Step 2: Navigate to target chat
print("📍 Going to target chat...")
browser1.get("https://web.telegram.org/a/#8549408740")
time.sleep(5)

print("✅ Target chat should be loaded")

# Step 3: SPECIFICALLY FIND MESSAGE INPUT FIELD (NOT SEARCH)
print("\n🔍 Finding CHAT MESSAGE INPUT FIELD (not search box)...")

def find_chat_message_input(driver, browser_name):
    """Find the actual chat message input field"""
    
    # Telegram Web has specific structure for message input
    # It's usually at the bottom, in the chat footer
    
    print(f"{browser_name}: Looking for chat message box...")
    
    # STRATEGY 1: Look in footer/chat input area
    for attempt in range(15):
        print(f"{browser_name}: Attempt {attempt+1}/15")
        
        try:
            # Method A: Find by specific Telegram classes
            telegram_classes = [
                'composer_rich_textarea',  # Most common
                'input-message-input',
                'im_editable',
                'message-input',
                'composer-input'
            ]
            
            for class_name in telegram_classes:
                try:
                    elements = driver.find_elements(By.CLASS_NAME, class_name)
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"{browser_name}: Found by class '{class_name}'")
                            return elem
                except:
                    continue
            
            # Method B: Look for contenteditable in footer
            try:
                # Find chat footer first
                footer_selectors = [
                    '.chat-footer',
                    '.im_send_form',
                    '.composer',
                    '.message-input-wrapper',
                    '[class*="send-form"]',
                    '[class*="composer"]'
                ]
                
                for selector in footer_selectors:
                    try:
                        footers = driver.find_elements(By.CSS_SELECTOR, selector)
                        for footer in footers:
                            if footer.is_displayed():
                                # Look for input inside footer
                                inputs = footer.find_elements(By.CSS_SELECTOR, "[contenteditable='true'], input, textarea")
                                for inp in inputs:
                                    if inp.is_displayed():
                                        print(f"{browser_name}: Found in footer with selector '{selector}'")
                                        return inp
                    except:
                        continue
            except:
                pass
            
            # Method C: Look for specific attribute patterns
            try:
                # Telegram message input often has specific attributes
                elements = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true'][data-placeholder*='Message'], [contenteditable='true'][placeholder*='Message']")
                for elem in elements:
                    if elem.is_displayed():
                        print(f"{browser_name}: Found by placeholder")
                        return elem
            except:
                pass
            
            # Method D: Look at the bottom of the screen (where message box usually is)
            try:
                height = driver.execute_script("return window.innerHeight")
                width = driver.execute_script("return window.innerWidth")
                
                # Scan from bottom upwards
                for y_offset in range(50, 200, 20):
                    y = height - y_offset
                    x = width // 2
                    
                    # Click at this position
                    driver.execute_script(f"""
                        var elem = document.elementFromPoint({x}, {y});
                        if(elem) {{
                            elem.click();
                            elem.focus();
                        }}
                        return elem;
                    """)
                    
                    time.sleep(0.5)
                    
                    # Check if active element is input-like
                    try:
                        active = driver.switch_to.active_element
                        tag = active.tag_name.lower()
                        contenteditable = active.get_attribute('contenteditable')
                        
                        if tag in ['input', 'textarea'] or contenteditable == 'true':
                            print(f"{browser_name}: Found by clicking at position ({x}, {y})")
                            return active
                    except:
                        pass
            except:
                pass
            
            # Method E: Try to find "Send" button and go left from there
            try:
                send_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Send') or contains(., 'SEND') or @aria-label='Send']")
                if send_buttons:
                    # Click near send button
                    driver.execute_script("arguments[0].click();", send_buttons[0])
                    time.sleep(1)
                    
                    # Look for input near it
                    elements = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true'], input, textarea")
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"{browser_name}: Found near Send button")
                            return elem
            except:
                pass
            
            # Method F: Use JavaScript to find Telegram's message input
            try:
                element = driver.execute_script("""
                    // Telegram Web specific selectors
                    var selectors = [
                        '.composer_rich_textarea',
                        '[contenteditable="true"].im_editable',
                        '.input-message-input',
                        'div[data-peer-id] [contenteditable="true"]'
                    ];
                    
                    for(var i = 0; i < selectors.length; i++) {
                        var elem = document.querySelector(selectors[i]);
                        if(elem && elem.offsetParent !== null) {
                            elem.click();
                            elem.focus();
                            return elem;
                        }
                    }
                    
                    // Fallback: look for any contenteditable at bottom
                    var allEditables = document.querySelectorAll('[contenteditable="true"]');
                    for(var i = 0; i < allEditables.length; i++) {
                        var rect = allEditables[i].getBoundingClientRect();
                        if(rect.bottom > window.innerHeight - 100) { // Near bottom
                            allEditables[i].click();
                            allEditables[i].focus();
                            return allEditables[i];
                        }
                    }
                    
                    return null;
                """)
                
                if element:
                    print(f"{browser_name}: Found via JavaScript")
                    return element
            except:
                pass
            
            print(f"{browser_name}: Not found yet, waiting 2 seconds...")
            time.sleep(2)
            
        except Exception as e:
            print(f"{browser_name}: Error during search: {e}")
            time.sleep(2)
    
    print(f"{browser_name}: ❌ Could not find message input after 15 attempts")
    return None

# Find message box for Browser 1
msg_box1 = find_chat_message_input(browser1, "Browser 1")

if not msg_box1:
    print("❌ Browser 1: Cannot find chat message input")
    browser1.save_screenshot('browser1_error.png')
    print("Screenshot saved: browser1_error.png")
    browser1.quit()
    exit()

# Test Browser 1
print("🧪 Browser 1: Testing message sending...")
try:
    # Click to focus
    msg_box1.click()
    time.sleep(1)
    
    # Type test message
    test_num = "8" + ''.join(str(random.randint(0, 9)) for _ in range(9))
    test_msg = f"TEST {test_num}"
    
    # Clear if possible
    try:
        if msg_box1.tag_name in ['input', 'textarea']:
            msg_box1.clear()
        else:
            browser1.execute_script("arguments[0].innerHTML = '';", msg_box1)
    except:
        pass
    
    time.sleep(0.5)
    
    # Type slowly
    for char in test_msg:
        msg_box1.send_keys(char)
        time.sleep(0.03)
    
    time.sleep(0.5)
    
    # Send
    msg_box1.send_keys(Keys.RETURN)
    
    print(f"✅ Browser 1: Test successful - '{test_msg}'")
    time.sleep(2)
    
except Exception as e:
    print(f"❌ Browser 1: Test failed - {e}")
    browser1.save_screenshot('browser1_test_error.png')
    browser1.quit()
    exit()

# Setup Browser 2 (Digit: 9)
print("\n\n🚀 BROWSER 2 STARTING (DIGIT: 9)")
print("="*50)

options2 = webdriver.ChromeOptions()
options2.add_argument("--start-maximized")
options2.add_argument("--user-data-dir=C:\\Users\\rosha\\browser2_data")

browser2 = webdriver.Chrome(service=service, options=options2)

# Browser 2 setup
print("📱 Opening Telegram...")
browser2.get("https://web.telegram.org/a/")

print("\n🔑 PLEASE LOGIN WITH QR CODE IN BROWSER 2")
print("Wait until you can see chat messages")
input("Press Enter AFTER you are logged in and can see chat interface: ")

print("📍 Going to target chat...")
browser2.get("https://web.telegram.org/a/?account=2#8549408740")
time.sleep(5)

print("✅ Target chat should be loaded")

# Find message box for Browser 2
msg_box2 = find_chat_message_input(browser2, "Browser 2")

if not msg_box2:
    print("❌ Browser 2: Cannot find chat message input")
    browser2.save_screenshot('browser2_error.png')
    print("Screenshot saved: browser2_error.png")
    browser2.quit()
    browser1.quit()
    exit()

# Test Browser 2
print("🧪 Browser 2: Testing message sending...")
try:
    # Click to focus
    msg_box2.click()
    time.sleep(1)
    
    # Type test message
    test_num = "9" + ''.join(str(random.randint(0, 9)) for _ in range(9))
    test_msg = f"TEST {test_num}"
    
    # Clear if possible
    try:
        if msg_box2.tag_name in ['input', 'textarea']:
            msg_box2.clear()
        else:
            browser2.execute_script("arguments[0].innerHTML = '';", msg_box2)
    except:
        pass
    
    time.sleep(0.5)
    
    # Type slowly
    for char in test_msg:
        msg_box2.send_keys(char)
        time.sleep(0.03)
    
    time.sleep(0.5)
    
    # Send
    msg_box2.send_keys(Keys.RETURN)
    
    print(f"✅ Browser 2: Test successful - '{test_msg}'")
    time.sleep(2)
    
except Exception as e:
    print(f"❌ Browser 2: Test failed - {e}")
    browser2.save_screenshot('browser2_test_error.png')
    browser2.quit()
    browser1.quit()
    exit()

# Both browsers ready
print("\n" + "="*70)
print("🎯 BOTH BROWSERS READY TO SEND MESSAGES!")
print("="*70)
print("Browser 1: Numbers starting with 8")
print("Browser 2: Numbers starting with 9")
print("\n⏱️  Each browser sends 5 numbers every 2 seconds")
print("💬 Sending to CHAT MESSAGE INPUT (not search box)")
print("⏸️  Press Ctrl+C to stop")
print("="*70)

numbers_browser1 = set()
numbers_browser2 = set()
cycle = 0

def send_from_browser(browser, msg_box, starting_digit, numbers_set, browser_name):
    """Send message from a browser"""
    try:
        # Generate 5 unique numbers
        numbers_list = []
        for _ in range(5):
            while True:
                num = str(starting_digit)
                for _ in range(9):
                    num += str(random.randint(0, 9))
                
                if num not in numbers_set:
                    numbers_set.add(num)
                    numbers_list.append(num)
                    break
        
        message = " ".join(numbers_list)
        
        # Focus
        msg_box.click()
        time.sleep(0.3)
        
        # Clear
        try:
            if msg_box.tag_name in ['input', 'textarea']:
                msg_box.clear()
            else:
                browser.execute_script("arguments[0].innerHTML = '';", msg_box)
        except:
            pass
        
        time.sleep(0.3)
        
        # Type
        for char in message:
            msg_box.send_keys(char)
            time.sleep(0.01)
        
        time.sleep(0.3)
        
        # Send
        msg_box.send_keys(Keys.RETURN)
        
        return True, message
        
    except Exception as e:
        print(f"{browser_name}: Send error - {e}")
        return False, None

try:
    while True:
        cycle += 1
        print(f"\n🔄 Cycle #{cycle}")
        
        # Browser 1: Send numbers starting with 8
        success1, message1 = send_from_browser(browser1, msg_box1, 8, numbers_browser1, "Browser 1")
        if success1:
            print(f"✅ Browser 1[8]: Sent {message1}")
        else:
            print(f"❌ Browser 1: Failed to send")
        
        # Browser 2: Send numbers starting with 9
        success2, message2 = send_from_browser(browser2, msg_box2, 9, numbers_browser2, "Browser 2")
        if success2:
            print(f"✅ Browser 2[9]: Sent {message2}")
        else:
            print(f"❌ Browser 2: Failed to send")
        
        # Show stats every 10 cycles
        if cycle % 10 == 0:
            print(f"\n📊 Statistics after {cycle} cycles:")
            print(f"  Browser 1: {len(numbers_browser1)} unique numbers")
            print(f"  Browser 2: {len(numbers_browser2)} unique numbers")
        
        # Wait 2 seconds
        time.sleep(2)
        
except KeyboardInterrupt:
    print(f"\n\n⏹️ Stopped after {cycle} cycles")
    print(f"📊 Final stats:")
    print(f"  Browser 1: {len(numbers_browser1)} unique numbers")
    print(f"  Browser 2: {len(numbers_browser2)} unique numbers")

except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    print("\n🤖 Bot finished. Both browsers remain open.")
    print("Close them manually when done.")
