import time
import random
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os

print("\n" + "="*70)
print("🤖 TELEGRAM 2-BROWSER BOT (FIXED)")
print("="*70)

def run_browser(starting_digit, browser_id):
    """Run a browser instance"""
    print(f"\n🚀 BROWSER {browser_id} STARTING (DIGIT: {starting_digit})")
    print("="*50)
    
    try:
        # Setup Chrome options
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--start-maximized")
        
        # Use different user data directories
        user_data_dir = f"C:\\Users\\rosha\\telegram_bot_{browser_id}"
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # IMPORTANT: Use different port for each browser
        if browser_id == 1:
            options.add_argument("--remote-debugging-port=9222")
        else:
            options.add_argument("--remote-debugging-port=9223")
        
        # Try different methods to start Chrome
        driver = None
        
        # Method 1: Direct webdriver (simplest)
        try:
            print(f"Method 1: Starting Chrome directly...")
            driver = webdriver.Chrome(options=options)
        except:
            # Method 2: Try with Service
            try:
                print(f"Method 2: Trying with Service...")
                from selenium.webdriver.chrome.service import Service
                driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            except:
                # Method 3: Manual chromedriver
                print(f"Method 3: Manual approach...")
                # Copy chromedriver to temp location
                import shutil
                temp_driver = f"C:\\Users\\rosha\\Downloads\\chrome_automation\\chromedriver_{browser_id}.exe"
                shutil.copy(r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe', temp_driver)
                
                from selenium.webdriver.chrome.service import Service
                service = Service(temp_driver)
                driver = webdriver.Chrome(service=service, options=options)
        
        if not driver:
            print(f"❌ Browser {browser_id}: Could not start Chrome")
            return
        
        print(f"✅ Browser {browser_id}: Chrome started successfully")
        
        # Step 1: Open Telegram
        print("📱 Opening Telegram...")
        driver.get("https://web.telegram.org/a/")
        
        print(f"\n🔑 BROWSER {browser_id}: PLEASE LOGIN WITH QR CODE")
        print(f"Starting digit for this browser: {starting_digit}")
        input(f"Press Enter AFTER you are fully logged in to Browser {browser_id}: ")
        
        # Step 2: Navigate to target chat
        print(f"\n📍 Browser {browser_id}: Going to target chat...")
        driver.get("https://web.telegram.org/a/#8549408740")
        time.sleep(5)
        
        # Step 3: Find message box
        print(f"🔍 Browser {browser_id}: Finding message box...")
        
        def find_message_input():
            for attempt in range(20):
                try:
                    # Method 1: Contenteditable
                    elements = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"✅ Browser {browser_id}: Found contenteditable box")
                            return elem
                    
                    # Method 2: Input/textarea
                    elements = driver.find_elements(By.TAG_NAME, "input") + driver.find_elements(By.TAG_NAME, "textarea")
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"✅ Browser {browser_id}: Found input box")
                            return elem
                    
                    # Method 3: Click at bottom
                    if attempt % 3 == 0:
                        width = driver.execute_script("return window.innerWidth")
                        height = driver.execute_script("return window.innerHeight")
                        driver.execute_script(f"""
                            var elem = document.elementFromPoint({width//2}, {height-50});
                            if(elem) {{
                                elem.click();
                                elem.focus();
                            }}
                        """)
                        time.sleep(1)
                    
                    print(f"⚠️ Browser {browser_id}: Attempt {attempt+1}/20, retrying...")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️ Browser {browser_id}: Search error - {e}")
                    time.sleep(2)
            
            return None
        
        msg_box = find_message_input()
        
        if not msg_box:
            print(f"❌ Browser {browser_id}: Cannot find message box")
            driver.save_screenshot(f'browser_{browser_id}_error.png')
            driver.quit()
            return
        
        # Step 4: Test browser
        print(f"🧪 Browser {browser_id}: Testing...")
        try:
            msg_box.click()
            time.sleep(1)
            
            test_num = str(starting_digit) + ''.join(str(random.randint(0, 9)) for _ in range(9))
            test_msg = f"TEST {test_num}"
            
            # Clear
            if msg_box.tag_name in ['input', 'textarea']:
                msg_box.clear()
            else:
                driver.execute_script("arguments[0].innerHTML = '';", msg_box)
            
            time.sleep(0.5)
            
            # Type
            for char in test_msg:
                msg_box.send_keys(char)
                time.sleep(0.02)
            
            time.sleep(0.5)
            msg_box.send_keys(Keys.RETURN)
            
            print(f"✅ Browser {browser_id}: Test successful")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Browser {browser_id}: Test failed - {e}")
            driver.quit()
            return
        
        # Step 5: Start messaging
        print(f"\n🎯 Browser {browser_id}: READY!")
        print(f"📤 Sending 5 numbers every 2 seconds")
        print(f"⏸️ Press Ctrl+C in terminal to stop all browsers")
        print(f"{'='*50}")
        
        numbers_set = set()
        cycle = 0
        
        try:
            while True:
                cycle += 1
                print(f"\n📦 Browser {browser_id}: Batch #{cycle}")
                
                try:
                    # Generate 5 numbers
                    numbers = []
                    for _ in range(5):
                        while True:
                            num = str(starting_digit)
                            for _ in range(9):
                                num += str(random.randint(0, 9))
                            
                            if num not in numbers_set:
                                numbers_set.add(num)
                                numbers.append(num)
                                break
                    
                    message = " ".join(numbers)
                    
                    # Send
                    msg_box.click()
                    time.sleep(0.3)
                    
                    # Clear
                    if msg_box.tag_name in ['input', 'textarea']:
                        msg_box.clear()
                    else:
                        driver.execute_script("arguments[0].innerHTML = '';", msg_box)
                    
                    time.sleep(0.3)
                    
                    # Type
                    for char in message:
                        msg_box.send_keys(char)
                        time.sleep(0.01)
                    
                    time.sleep(0.3)
                    msg_box.send_keys(Keys.RETURN)
                    
                    print(f"✅ Browser {browser_id}[{starting_digit}]: Sent {len(numbers)} numbers")
                    
                except Exception as e:
                    print(f"❌ Browser {browser_id}: Send error - {e}")
                    # Try to find message box again
                    msg_box = find_message_input()
                    if not msg_box:
                        print(f"❌ Browser {browser_id}: Lost message box, exiting")
                        break
                
                # Wait 2 seconds
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Browser {browser_id}: Stopped")
        except Exception as e:
            print(f"\n❌ Browser {browser_id}: Error - {e}")
        
        finally:
            print(f"\n📊 Browser {browser_id}: Finished")
            print(f"Total numbers sent: {len(numbers_set)}")
            print(f"Browser remains open")
            
    except Exception as e:
        print(f"\n❌ Browser {browser_id}: Fatal error - {e}")

# Run browsers in sequence
print("\n📋 INSTRUCTIONS:")
print("1. First Browser 1 will start (Digit: 8)")
print("2. Login in Browser 1")
print("3. Then Browser 2 will start (Digit: 9)")
print("4. Login in Browser 2")
print("5. Both will send messages independently")

print("\n⚠️ IMPORTANT:")
print("• Close ALL Chrome windows before starting")
print("• You need to login in BOTH browsers separately")
print("• Each browser runs independently")

print("\n🚀 Starting Browser 1 in 5 seconds...")
for i in range(5, 0, -1):
    print(f"   {i}...")
    time.sleep(1)

# Run Browser 1
run_browser(8, 1)

print("\n\n🚀 Starting Browser 2 in 5 seconds...")
for i in range(5, 0, -1):
    print(f"   {i}...")
    time.sleep(1)

# Run Browser 2
run_browser(9, 2)

print("\n" + "="*70)
print("🎉 BOTH BROWSERS COMPLETED")
print("="*70)
