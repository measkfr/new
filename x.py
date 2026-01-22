import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os

def run_browser(browser_id, starting_digit):
    """Run a browser instance with specific starting digit"""
    print(f"\n" + "="*60)
    print(f"🤖 BROWSER {browser_id} STARTING (DIGIT: {starting_digit})")
    print("="*60)
    
    try:
        # Setup Chrome options
        options = Options()
        options.add_argument("--start-maximized")
        
        # Use different user data for each browser
        user_data_dir = f"C:\\Users\\rosha\\telegram_data_{browser_id}"
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Different remote debugging ports
        if browser_id == 1:
            options.add_argument("--remote-debugging-port=9222")
        else:
            options.add_argument("--remote-debugging-port=9223")
        
        # Start Chrome
        print(f"🚀 Starting Chrome Browser {browser_id}...")
        driver = webdriver.Chrome(options=options)
        
        print(f"✅ Browser {browser_id} started successfully")
        
        # Step 1: Open Telegram
        print(f"\n📱 Opening Telegram...")
        driver.get("https://web.telegram.org/a/")
        
        print(f"\n🔑 BROWSER {browser_id}: PLEASE LOGIN WITH QR CODE")
        print(f"This browser will send numbers starting with: {starting_digit}")
        input(f"Press Enter AFTER you are fully logged in and can see chats: ")
        
        # Step 2: Navigate to target chat
        print(f"\n📍 Navigating to target chat...")
        target_url = "https://web.telegram.org/a/?account=2#8549408740"
        driver.get(target_url)
        time.sleep(5)
        
        print(f"✅ Target chat loaded")
        
        # Step 3: SPECIFICALLY FIND THE MESSAGE INPUT FIELD
        print(f"\n🔍 Looking for MESSAGE INPUT FIELD...")
        print("Searching for: contenteditable='true' with aria-label='Message'")
        
        message_box = None
        max_attempts = 15
        
        for attempt in range(1, max_attempts + 1):
            print(f"Attempt {attempt}/{max_attempts}...")
            
            try:
                # STRATEGY 1: Find by the EXACT element you provided
                # <div id="editable-message-text" class="form-control allow-selection" contenteditable="true" role="textbox" dir="auto" tabindex="0" aria-label="Message">
                
                # Try exact CSS selector
                selectors = [
                    "#editable-message-text",  # By ID
                    "div[contenteditable='true'][aria-label='Message']",  # By attributes
                    "div[contenteditable='true'][role='textbox']",  # By role
                    "div.form-control.allow-selection[contenteditable='true']",  # By class
                    "[contenteditable='true'][aria-label*='Message']",  # Contains Message
                ]
                
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            if elem.is_displayed():
                                message_box = elem
                                print(f"✅ Found message box with selector: {selector}")
                                break
                        if message_box:
                            break
                    except:
                        continue
                
                # STRATEGY 2: Look for contenteditable elements and check their attributes
                if not message_box:
                    try:
                        editables = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                        for elem in editables:
                            try:
                                aria_label = elem.get_attribute('aria-label') or ''
                                role = elem.get_attribute('role') or ''
                                classes = elem.get_attribute('class') or ''
                                
                                # Check if this looks like a message input
                                if ('message' in aria_label.lower() or 
                                    'textbox' in role.lower() or
                                    'form-control' in classes):
                                    message_box = elem
                                    print(f"✅ Found by attributes - aria-label: {aria_label}")
                                    break
                            except:
                                continue
                    except:
                        pass
                
                # STRATEGY 3: Look in the message composer/send area
                if not message_box:
                    try:
                        # Look for send button/form area
                        composer_selectors = [
                            '.composer',
                            '.message-input-wrapper',
                            '.im_send_form',
                            '.chat-footer'
                        ]
                        
                        for container_selector in composer_selectors:
                            try:
                                containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
                                for container in containers:
                                    if container.is_displayed():
                                        # Look for input inside container
                                        inputs = container.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                                        for inp in inputs:
                                            if inp.is_displayed():
                                                message_box = inp
                                                print(f"✅ Found in container: {container_selector}")
                                                break
                                        if message_box:
                                            break
                            except:
                                continue
                    except:
                        pass
                
                # STRATEGY 4: Click at bottom center where message box usually is
                if not message_box and attempt % 3 == 0:
                    try:
                        width = driver.execute_script("return window.innerWidth")
                        height = driver.execute_script("return window.innerHeight")
                        
                        # Click at position where message box typically is
                        driver.execute_script(f"""
                            var elem = document.elementFromPoint({width//2}, {height - 80});
                            if(elem) {{
                                elem.click();
                                elem.focus();
                            }}
                        """)
                        time.sleep(1)
                        
                        # Check active element
                        active_elem = driver.switch_to.active_element
                        contenteditable = active_elem.get_attribute('contenteditable')
                        if contenteditable == 'true':
                            message_box = active_elem
                            print(f"✅ Found by clicking at bottom")
                    except:
                        pass
                
                if message_box:
                    break
                    
                print(f"⚠️ Not found yet, waiting 2 seconds...")
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Search error: {e}")
                time.sleep(2)
        
        if not message_box:
            print(f"❌ Browser {browser_id}: Could not find message input field")
            print("Taking screenshot for debugging...")
            driver.save_screenshot(f'browser_{browser_id}_error.png')
            driver.quit()
            return
        
        print(f"\n✅ Browser {browser_id}: MESSAGE INPUT FIELD FOUND!")
        print(f"   Element: {message_box.tag_name}")
        print(f"   ID: {message_box.get_attribute('id')}")
        print(f"   Class: {message_box.get_attribute('class')}")
        print(f"   aria-label: {message_box.get_attribute('aria-label')}")
        
        # Step 4: Test sending a message
        print(f"\n🧪 Testing message sending...")
        try:
            # Click to focus
            message_box.click()
            time.sleep(1)
            
            # Generate test number
            test_num = str(starting_digit) + ''.join(str(random.randint(0, 9)) for _ in range(9))
            test_msg = f"TEST {test_num}"
            
            # Clear if possible
            try:
                driver.execute_script("arguments[0].innerHTML = '';", message_box)
                time.sleep(0.5)
            except:
                pass
            
            # Type test message slowly
            print(f"   Typing: {test_msg}")
            for char in test_msg:
                message_box.send_keys(char)
                time.sleep(0.03)
            
            time.sleep(0.5)
            
            # Send message (Enter key)
            message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Test successful! Message sent: {test_msg}")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            driver.quit()
            return
        
        # Step 5: Start continuous messaging
        print(f"\n" + "="*60)
        print(f"🚀 BROWSER {browser_id}: READY FOR CONTINUOUS MESSAGING")
        print("="*60)
        print(f"Starting digit: {starting_digit}")
        print(f"Each message: 5 numbers")
        print(f"Interval: Every 2 seconds")
        print(f"⏸️  Close browser or press Ctrl+C in terminal to stop")
        print("="*60)
        
        numbers_set = set()
        batch_count = 0
        
        try:
            while True:
                batch_count += 1
                print(f"\n📦 Browser {browser_id}: Batch #{batch_count}")
                
                # Generate 5 unique numbers
                numbers_list = []
                for _ in range(5):
                    while True:
                        number = str(starting_digit)
                        for _ in range(9):
                            number += str(random.randint(0, 9))
                        
                        if number not in numbers_set:
                            numbers_set.add(number)
                            numbers_list.append(number)
                            break
                
                message = " ".join(numbers_list)
                
                try:
                    # Focus on message box
                    message_box.click()
                    time.sleep(0.3)
                    
                    # Clear previous content
                    driver.execute_script("arguments[0].innerHTML = '';", message_box)
                    time.sleep(0.3)
                    
                    # Type the message
                    print(f"   Typing: {message}")
                    for char in message:
                        message_box.send_keys(char)
                        time.sleep(0.01)  # Natural typing speed
                    
                    time.sleep(0.3)
                    
                    # Send (Enter key)
                    message_box.send_keys(Keys.RETURN)
                    
                    print(f"✅ Sent successfully")
                    
                except Exception as e:
                    print(f"❌ Send error: {e}")
                    # Try to find message box again
                    try:
                        message_box = driver.find_element(By.CSS_SELECTOR, "#editable-message-text")
                    except:
                        try:
                            message_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][aria-label='Message']")
                        except:
                            print(f"❌ Lost message box, exiting...")
                            break
                
                # Wait 2 seconds before next batch
                time.sleep(2)
                
                # Show stats every 10 batches
                if batch_count % 10 == 0:
                    print(f"\n📊 Browser {browser_id} Stats:")
                    print(f"   Batches sent: {batch_count}")
                    print(f"   Total numbers: {len(numbers_set)}")
                    
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Browser {browser_id}: Stopped by user")
        except Exception as e:
            print(f"\n❌ Browser {browser_id}: Error - {e}")
        
        finally:
            print(f"\n📊 Browser {browser_id} Final Stats:")
            print(f"   Total batches: {batch_count}")
            print(f"   Unique numbers sent: {len(numbers_set)}")
            print(f"\n💡 Browser {browser_id} remains open")
            print("   Close it manually when done")
            
    except Exception as e:
        print(f"\n❌ Browser {browser_id}: Fatal error - {e}")

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM 2-BROWSER MESSAGE BOT")
    print("="*70)
    print("This bot will open TWO Chrome browsers:")
    print("  • Browser 1: Sends numbers starting with 8")
    print("  • Browser 2: Sends numbers starting with 9")
    print("="*70)
    
    # Check ChromeDriver
    chromedriver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    if not os.path.exists(chromedriver_path):
        print(f"❌ ChromeDriver not found at: {chromedriver_path}")
        print("Please ensure chromedriver.exe is in this location")
        return
    
    print("✅ ChromeDriver found")
    
    print("\n📋 IMPORTANT INSTRUCTIONS:")
    print("1. Close ALL Chrome windows before starting")
    print("2. You will login in EACH browser separately")
    print("3. Look for the MESSAGE INPUT FIELD (not search)")
    print("4. Each browser runs independently")
    
    print("\n🚀 Starting Browser 1 in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Run Browser 1
    run_browser(1, 8)
    
    print("\n\n🚀 Starting Browser 2 in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Run Browser 2
    run_browser(2, 9)
    
    print("\n" + "="*70)
    print("🎉 BOTH BROWSERS HAVE COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
