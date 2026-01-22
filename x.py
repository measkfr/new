import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

class TelegramBrowserBot:
    def __init__(self, browser_id, starting_digit):
        self.browser_id = browser_id
        self.starting_digit = starting_digit  # 8 or 9 only
        self.driver = None
        self.generated_numbers = set()
        self.message_box = None
        
    def setup_browser(self):
        """Setup individual Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Use separate user data for each browser
        user_data_dir = f"C:/Users/rosha/Downloads/chrome_automation/browser_{self.browser_id}"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Remove automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"✅ Browser {self.browser_id} (Digit: {self.starting_digit}) started")
            return True
        except Exception as e:
            print(f"❌ Browser {self.browser_id} setup error: {e}")
            return False
    
    def manual_login_and_setup(self):
        """Manual login and setup for this browser"""
        print(f"\n📱 BROWSER {self.browser_id} - MANUAL LOGIN REQUIRED")
        print("="*50)
        
        # Open Telegram
        self.driver.get("https://web.telegram.org/a/")
        print(f"✅ Browser {self.browser_id}: Telegram opened")
        
        print(f"\n🔑 Please login with QR code in Browser {self.browser_id}")
        print(f"Starting digit for this browser: {self.starting_digit}")
        input(f"Press Enter AFTER you are fully logged in to Browser {self.browser_id}: ")
        
        # Navigate to target chat
        print(f"\n📍 Browser {self.browser_id}: Going to target chat...")
        self.driver.get("https://web.telegram.org/a/#8549408740")
        time.sleep(5)
        print(f"✅ Browser {self.browser_id}: Target chat opened")
        
        return True
    
    def find_message_box(self):
        """Find message box in current browser"""
        print(f"🔍 Browser {self.browser_id}: Finding message box...")
        
        for attempt in range(10):
            try:
                # Method 1: Contenteditable
                elements = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        self.message_box = elem
                        print(f"✅ Browser {self.browser_id}: Found contenteditable box")
                        return True
                
                # Method 2: Input/textarea
                elements = self.driver.find_elements(By.TAG_NAME, "input") + self.driver.find_elements(By.TAG_NAME, "textarea")
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        self.message_box = elem
                        print(f"✅ Browser {self.browser_id}: Found input box")
                        return True
                
                # Method 3: Click at bottom center
                if attempt >= 3:
                    width = self.driver.execute_script("return window.innerWidth")
                    height = self.driver.execute_script("return window.innerHeight")
                    
                    self.driver.execute_script(f"""
                        var elem = document.elementFromPoint({width//2}, {height-100});
                        if(elem) {{
                            elem.click();
                            elem.focus();
                        }}
                    """)
                    time.sleep(1)
                
                print(f"⚠️ Browser {self.browser_id}: Attempt {attempt+1}/10 - Retrying...")
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Browser {self.browser_id}: Search error - {e}")
                time.sleep(2)
        
        print(f"❌ Browser {self.browser_id}: Could not find message box")
        return False
    
    def test_browser_functionality(self):
        """Test if browser can send messages"""
        print(f"🧪 Browser {self.browser_id}: Testing functionality...")
        
        if not self.message_box:
            if not self.find_message_box():
                return False
        
        try:
            # Generate test number
            test_num = str(self.starting_digit) + ''.join(str(random.randint(0, 9)) for _ in range(9))
            test_msg = f"TEST {test_num}"
            
            # Focus
            self.message_box.click()
            time.sleep(0.5)
            
            # Clear
            if self.message_box.tag_name in ['input', 'textarea']:
                self.message_box.clear()
            else:
                self.driver.execute_script("arguments[0].innerHTML = '';", self.message_box)
            
            time.sleep(0.5)
            
            # Type test message
            for char in test_msg:
                self.message_box.send_keys(char)
                time.sleep(0.02)
            
            time.sleep(0.5)
            
            # Send
            self.message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Browser {self.browser_id}: Test successful - '{test_msg}'")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Test failed - {e}")
            return False
    
    def generate_unique_number(self):
        """Generate unique 10-digit Indian number"""
        while True:
            number = str(self.starting_digit)
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.generated_numbers:
                self.generated_numbers.add(number)
                return number
    
    def send_batch(self):
        """Send one batch of 5 numbers"""
        try:
            # Generate 5 numbers
            numbers_list = []
            for _ in range(5):
                numbers_list.append(self.generate_unique_number())
            
            message = " ".join(numbers_list)
            
            # Make sure we have message box
            if not self.message_box:
                if not self.find_message_box():
                    return False
            
            # Focus
            self.message_box.click()
            time.sleep(0.3)
            
            # Clear
            if self.message_box.tag_name in ['input', 'textarea']:
                self.message_box.clear()
            else:
                self.driver.execute_script("arguments[0].innerHTML = '';", self.message_box)
            
            time.sleep(0.3)
            
            # Type message
            for char in message:
                self.message_box.send_keys(char)
                time.sleep(0.01)
            
            time.sleep(0.3)
            
            # Send
            self.message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Browser {self.browser_id}[{self.starting_digit}]: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Send error - {e}")
            
            # Try to find message box again
            self.message_box = None
            if self.find_message_box():
                return self.send_batch()  # Retry
            
            return False
    
    def run_browser_bot(self):
        """Main function to run this browser bot"""
        print(f"\n{'='*60}")
        print(f"🚀 BROWSER {self.browser_id} STARTING")
        print(f"Starting digit: {self.starting_digit}")
        print(f"{'='*60}")
        
        # Setup browser
        if not self.setup_browser():
            return
        
        try:
            # Manual login
            self.manual_login_and_setup()
            
            # Find message box
            if not self.find_message_box():
                print(f"❌ Browser {self.browser_id}: Cannot find message box")
                return
            
            # Test functionality
            if not self.test_browser_functionality():
                print(f"❌ Browser {self.browser_id}: Test failed")
                return
            
            # Start continuous messaging
            print(f"\n🎯 Browser {self.browser_id}: READY!")
            print(f"📤 Sending 5 numbers every 2 seconds")
            print(f"⏸️ Press Ctrl+C in terminal to stop")
            print(f"{'='*60}")
            
            batch_count = 0
            try:
                while True:
                    batch_count += 1
                    print(f"\n📦 Browser {self.browser_id}: Batch #{batch_count}")
                    
                    self.send_batch()
                    
                    # Wait 2 seconds
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print(f"\n⏹️ Browser {self.browser_id}: Stopped")
            except Exception as e:
                print(f"❌ Browser {self.browser_id}: Error - {e}")
        
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Fatal error - {e}")
        
        finally:
            print(f"\n📊 Browser {self.browser_id}: Finished")
            print(f"Total numbers sent: {len(self.generated_numbers)}")
            print(f"Browser will remain open")

def run_browser_in_thread(browser_id, starting_digit):
    """Run a browser bot in separate thread"""
    bot = TelegramBrowserBot(browser_id, starting_digit)
    bot.run_browser_bot()

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM 2-BROWSER BOT")
    print("="*70)
    print("Configuration:")
    print("  • Browser 1: Starting with digit 8")
    print("  • Browser 2: Starting with digit 9")
    print("  • 6-digit numbers removed")
    print("="*70)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"❌ ChromeDriver not found at: {driver_path}")
        return
    
    print("✅ ChromeDriver found")
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Two SEPARATE Chrome browsers will open")
    print("2. Login in EACH browser separately")
    print("3. Browser 1 will send numbers starting with 8")
    print("4. Browser 2 will send numbers starting with 9")
    print("5. Each sends 5 numbers every 2 seconds")
    
    print("\n⚠️ IMPORTANT:")
    print("• Close all Chrome windows before starting")
    print("• You need to login in BOTH browsers")
    print("• Each browser has separate session")
    
    print("\n🚀 Starting in 10 seconds...")
    for i in range(10, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Create threads for both browsers
    threads = []
    
    # Browser 1: Starting with 8
    print(f"\n📱 Opening Browser 1 (Digit: 8)...")
    thread1 = threading.Thread(target=run_browser_in_thread, args=(1, 8))
    threads.append(thread1)
    thread1.start()
    
    # Wait before opening second browser
    time.sleep(5)
    
    # Browser 2: Starting with 9
    print(f"\n📱 Opening Browser 2 (Digit: 9)...")
    thread2 = threading.Thread(target=run_browser_in_thread, args=(2, 9))
    threads.append(thread2)
    thread2.start()
    
    # Wait for both threads to complete
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n⏹️ All browsers stopped by user")
    
    print("\n" + "="*70)
    print("🎉 BOTH BROWSERS COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
