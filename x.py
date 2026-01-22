import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

print("\n" + "="*70)
print("🤖 TELEGRAM BROWSER 1 (DIGIT: 8)")
print("="*70)

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--user-data-dir=C:\\Users\\rosha\\telegram_bot_1")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=options)

# Open Telegram
driver.get("https://web.telegram.org/a/")
print("📱 Please login with QR code in Browser 1")
input("Press Enter AFTER login: ")

# Go to target chat
driver.get("https://web.telegram.org/a/?account=2#8549408740")
time.sleep(5)

# Find message box
print("🔍 Finding message box...")
msg_box = None
for attempt in range(20):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
        for elem in elements:
            if elem.is_displayed():
                msg_box = elem
                print("✅ Found message box")
                break
        
        if not msg_box:
            elements = driver.find_elements(By.TAG_NAME, "input") + driver.find_elements(By.TAG_NAME, "textarea")
            for elem in elements:
                if elem.is_displayed():
                    msg_box = elem
                    print("✅ Found input box")
                    break
        
        if msg_box:
            break
            
    except:
        pass
    
    print(f"Attempt {attempt+1}/20...")
    time.sleep(2)

if not msg_box:
    print("❌ Cannot find message box")
    driver.quit()
    exit()

# Start messaging
print("\n🎯 READY! Sending numbers starting with 8")
print("⏱️  5 numbers every 2 seconds")
print("⏸️  Close browser to stop")

numbers_set = set()

try:
    while True:
        # Generate 5 numbers
        numbers = []
        for _ in range(5):
            while True:
                num = "8" + ''.join(str(random.randint(0, 9)) for _ in range(9))
                if num not in numbers_set:
                    numbers_set.add(num)
                    numbers.append(num)
                    break
        
        message = " ".join(numbers)
        
        # Send
        msg_box.click()
        time.sleep(0.3)
        
        if msg_box.tag_name in ['input', 'textarea']:
            msg_box.clear()
        else:
            driver.execute_script("arguments[0].innerHTML = '';", msg_box)
        
        time.sleep(0.3)
        
        for char in message:
            msg_box.send_keys(char)
            time.sleep(0.01)
        
        time.sleep(0.3)
        msg_box.send_keys(Keys.RETURN)
        
        print(f"✅ Sent: {message}")
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n⏹️ Stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")

print(f"\n📊 Total numbers sent: {len(numbers_set)}")
print("🤖 Browser remains open")
