import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

class TelegramWindow:
    def __init__(self, window_id, starting_digit):
        self.window_id = window_id
        self.starting_digit = starting_digit
        self.driver = None
        self.numbers_set = set()
        self.message_box = None
        
    def setup_window(self):
        """Setup individual Chrome window"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Add user data directory for separate sessions
        user_data_dir = f"C:/Users/rosha/Downloads/chrome_automation/chrome_data_{self.window_id}"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"✅ Window {self.window_id} started")
            return True
        except Exception as e:
            print(f"❌ Window {self.window_id} setup error: {e}")
            return False
    
    def manual_login_and_setup(self):
        """Manual login and setup for this window"""
        print(f"\n📱 WINDOW {self.window_id} - MANUAL LOGIN REQUIRED")
        print("="*50)
        
        # Open Telegram
        self.driver.get("https://web.telegram.org/a/")
        print(f"✅ Window {self.window_id}: Telegram opened")
        
        print(f"\n⏳ Window {self.window_id}: Please login with QR code")
        print(f"You have 30 seconds...")
        
        # Wait for manual login
        for i in range(30):
            time.sleep(1)
            if (i+1) % 10 == 0:
                print(f"   Window {self.window_id}: {30-(i+1)} seconds remaining...")
        
        # Navigate to target chat
        self.driver.get("https://web.telegram.org/a/?account=2#8549408740")
        time.sleep(3)
        
        print(f"✅ Window {self.window_id}: Setup complete")
        return True
    
    def find_message_box(self):
        """Find message box"""
        print(f"🔍 Window {self.window_id}: Finding message box...")
        
        # Try different methods
        for attempt in range(5):
            try:
                # Method 1: Contenteditable
                editables = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                for elem in editables:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            self.message_box = elem
                            print(f"✅ Window {self.window_id}: Found message box")
                            return True
                    except:
                        continue
                
                # Method 2: Input/textarea
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                for elem in inputs + textareas:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            self.message_box = elem
                            print(f"✅ Window {self.window_id}: Found input box")
                            return True
                    except:
                        continue
                
                # Method 3: Click at likely position
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
                
            except Exception as e:
                print(f"⚠️ Window {self.window_id}: Attempt {attempt+1} failed - {e}")
                time.sleep(1)
        
        print(f"❌ Window {self.window_id}: Could not find message box")
        return False
    
    def generate_number(self):
        """Generate unique number"""
        while True:
            number = str(self.starting_digit)
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.numbers_set:
                self.numbers_set.add(number)
                return number
    
    def send_message(self):
        """Send one message"""
        if not self.message_box:
            if not self.find_message_box():
                return False
        
        try:
            # Generate 5 numbers
            numbers_list = []
            for _ in range(5):
                numbers_list.append(self.generate_number())
            
            message = " ".join(numbers_list)
            
            # Focus and clear
            self.message_box.click()
            time.sleep(0.2)
            
            # Clear
            try:
                if self.message_box.tag_name in ['input', 'textarea']:
                    self.message_box.clear()
                else:
                    self.driver.execute_script("arguments[0].innerHTML = '';", self.message_box)
            except:
                pass
            
            time.sleep(0.2)
            
            # Type
            for char in message:
                self.message_box.send_keys(char)
                time.sleep(0.005)
            
            time.sleep(0.2)
            
            # Send
            self.message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Window {self.window_id}: Sent {message}")
            return True
            
        except Exception as e:
            print(f"❌ Window {self.window_id}: Send error - {e}")
            # Try to find message box again
            self.find_message_box()
            return False
    
    def run_window_bot(self):
        """Run bot for this window"""
        print(f"\n{'='*50}")
        print(f"🚀 WINDOW {self.window_id} STARTING")
        print(f"Starting digit: {self.starting_digit}")
        print(f"{'='*50}")
        
        # Setup window
        if not self.setup_window():
            return
        
        try:
            # Manual login
            self.manual_login_and_setup()
            
            # Find message box
            if not self.find_message_box():
                print(f"❌ Window {self.window_id}: Cannot proceed")
                return
            
            print(f"\n🎯 Window {self.window_id}: READY!")
            print(f"Sending 5 numbers every 2 seconds")
            
            message_count = 0
            try:
                while True:
                    message_count += 1
                    print(f"\n📦 Window {self.window_id}: Message #{message_count}")
                    
                    self.send_message()
                    
                    # Wait 2 seconds
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print(f"\n⏹️ Window {self.window_id}: Stopped")
            except Exception as e:
                print(f"❌ Window {self.window_id}: Error - {e}")
        
        except Exception as e:
            print(f"❌ Window {self.window_id}: Fatal error - {e}")
        
        finally:
            print(f"\n📊 Window {self.window_id}: Finished")
            print(f"Numbers sent: {len(self.numbers_set)}")

def run_single_window(window_id, starting_digit):
    """Run a single window in its own thread"""
    window = TelegramWindow(window_id, starting_digit)
    window.run_window_bot()

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM 10-WINDOW INDEPENDENT BOT")
    print("="*70)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    if not os.path.exists(driver_path):
        print(f"❌ ChromeDriver not found at: {driver_path}")
        return
    
    print("✅ ChromeDriver found")
    
    # Window configuration
    # 3 windows with digit 6, 3 with digit 8, 4 with digit 9
    window_config = [
        (1, 6), (2, 6), (3, 6),  # First 3: digit 6
        (4, 8), (5, 8), (6, 8),  # Next 3: digit 8
        (7, 9), (8, 9), (9, 9), (10, 9)  # Last 4: digit 9
    ]
    
    print("\n📊 Window Configuration:")
    for window_id, digit in window_config:
        print(f"  Window {window_id}: Starting with {digit}")
    
    print("\n⚠️ IMPORTANT:")
    print("1. 10 SEPARATE Chrome windows will open")
    print("2. You need to login in EACH window separately")
    print("3. You have 30 seconds per window to login")
    print("4. This will use more system resources")
    
    print("\n🚀 Starting in 10 seconds...")
    for i in range(10, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Create threads for each window
    threads = []
    
    for window_id, starting_digit in window_config:
        print(f"\n📱 Opening Window {window_id}...")
        
        # Create thread for this window
        thread = threading.Thread(target=run_single_window, args=(window_id, starting_digit))
        threads.append(thread)
        
        # Start thread
        thread.start()
        
        # Wait a bit before opening next window
        time.sleep(2)
    
    # Wait for all threads to complete
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n⏹️ All windows stopped by user")
    
    print("\n" + "="*70)
    print("🎉 ALL WINDOWS COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
