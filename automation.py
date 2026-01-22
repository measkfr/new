import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

class TelegramBot:
    def __init__(self, browser_id, starting_digit):
        self.browser_id = browser_id
        self.starting_digit = starting_digit
        self.driver = None
        self.generated_numbers = set()
    
    def setup_chrome(self):
        """Setup Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        try:
            # ChromeDriver path
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            
            # Use Service for Selenium 4
            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"✅ Browser {self.browser_id}: Chrome started")
            return True
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Chrome error - {e}")
            print("\n💡 ChromeDriver fix karo:")
            print("1. Chrome update karo")
            print("2. Ya correct ChromeDriver download karo")
            print("3. Download from: https://chromedriver.chromium.org/")
            return False
    
    def wait_on_telegram(self):
        """Open Telegram and wait 1 minute, then refresh"""
        try:
            print(f"🌐 Browser {self.browser_id}: Opening Telegram...")
            self.driver.get("https://web.telegram.org/a/")
            print(f"✅ Browser {self.browser_id}: Telegram opened")
            
            # Wait exactly 1 minute (60 seconds)
            print(f"⏳ Browser {self.browser_id}: Waiting 60 seconds...")
            for i in range(60):
                time.sleep(1)
                if (i+1) % 10 == 0:  # Every 10 seconds
                    print(f"   {60-(i+1)} seconds remaining...")
            
            # Refresh the page
            print(f"🔄 Browser {self.browser_id}: Refreshing page...")
            self.driver.refresh()
            time.sleep(3)  # Wait for refresh to complete
            
            print(f"✅ Browser {self.browser_id}: Page refreshed")
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Telegram error - {e}")
            return False
    
    def go_to_target_chat(self):
        """Navigate to target chat"""
        try:
            print(f"💬 Browser {self.browser_id}: Going to target chat...")
            
            target_url = "https://web.telegram.org/a/?account=2#8549408740"
            self.driver.get(target_url)
            
            print(f"✅ Browser {self.browser_id}: Target chat opened")
            time.sleep(5)  # Wait for chat to load
            
            return True
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Chat error - {e}")
            return False
    
    def find_message_box(self):
        """Find message input box"""
        print(f"🔍 Browser {self.browser_id}: Finding message box...")
        
        # Try different methods
        methods_to_try = [
            self._find_by_contenteditable,
            self._find_by_input_tag,
            self._find_by_placeholder,
            self._find_by_class
        ]
        
        for method in methods_to_try:
            element = method()
            if element:
                return element
        
        print(f"❌ Browser {self.browser_id}: Message box not found")
        return None
    
    def _find_by_contenteditable(self):
        """Find contenteditable div"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    print(f"✅ Found contenteditable box")
                    return elem
        except:
            pass
        return None
    
    def _find_by_input_tag(self):
        """Find input or textarea"""
        try:
            # Try textarea first
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for elem in textareas:
                if elem.is_displayed() and elem.is_enabled():
                    print(f"✅ Found textarea")
                    return elem
            
            # Try input
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for elem in inputs:
                if elem.is_displayed() and elem.is_enabled():
                    print(f"✅ Found input box")
                    return elem
        except:
            pass
        return None
    
    def _find_by_placeholder(self):
        """Find by placeholder text"""
        try:
            elements = self.driver.find_elements(By.XPATH, "//*[@placeholder]")
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    placeholder = elem.get_attribute('placeholder') or ''
                    if 'message' in placeholder.lower() or 'type' in placeholder.lower():
                        print(f"✅ Found by placeholder: {placeholder}")
                        return elem
        except:
            pass
        return None
    
    def _find_by_class(self):
        """Find by class name"""
        class_names = ['input-message-input', 'composer', 'message-input', 'chat-input']
        for class_name in class_names:
            try:
                elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        print(f"✅ Found by class: {class_name}")
                        return elem
            except:
                continue
        return None
    
    def generate_indian_number(self):
        """Generate unique 10-digit Indian number"""
        while True:
            number = str(self.starting_digit)
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.generated_numbers:
                self.generated_numbers.add(number)
                return number
    
    def send_numbers(self, input_field):
        """Send 5 numbers to chat"""
        # Generate 5 numbers
        numbers_list = []
        for _ in range(5):
            numbers_list.append(self.generate_indian_number())
        
        # Format: number1 number2 number3 number4 number5
        message = " ".join(numbers_list)
        
        try:
            # Clear and type
            input_field.clear()
            time.sleep(0.5)
            
            input_field.send_keys(message)
            time.sleep(0.5)
            
            # Send message (Enter key)
            input_field.send_keys(Keys.RETURN)
            
            print(f"✅ Sent: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    def run_bot(self):
        """Main bot function"""
        print(f"\n{'='*60}")
        print(f"🤖 TELEGRAM BOT - Browser {self.browser_id}")
        print(f"{'='*60}")
        
        # Step 1: Setup Chrome
        if not self.setup_chrome():
            return
        
        try:
            # Step 2: Wait on Telegram for 1 minute and refresh
            self.wait_on_telegram()
            
            # Step 3: Go to target chat
            self.go_to_target_chat()
            
            # Step 4: Find message box
            message_box = self.find_message_box()
            
            if message_box:
                print(f"\n🎯 Browser {self.browser_id}: READY!")
                print(f"📤 Will send 5 numbers every 2 seconds")
                print(f"⏸️ Press Ctrl+C to stop")
                
                message_count = 0
                try:
                    while True:
                        message_count += 1
                        print(f"\n📦 Message #{message_count}")
                        
                        # Send numbers
                        self.send_numbers(message_box)
                        
                        # Wait 2 seconds
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    print(f"\n⏹️ Stopped by user")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print(f"\n❌ Browser {self.browser_id}: Cannot find message box")
                print("Taking screenshot for debugging...")
                try:
                    self.driver.save_screenshot(f'error_browser_{self.browser_id}.png')
                    print(f"Screenshot saved")
                except:
                    pass
        
        except Exception as e:
            print(f"❌ Fatal error: {e}")
        
        finally:
            print(f"\n📊 Browser {self.browser_id}: Finished")
            print("Browser will stay open for inspection")
            print("Close it manually when done")

def main():
    print("\n" + "="*70)
    print("🤖 SIMPLE TELEGRAM AUTOMATION BOT")
    print("="*70)
    print("Steps:")
    print("1. Open https://web.telegram.org/a/")
    print("2. Wait 60 seconds")
    print("3. Refresh page")
    print("4. Go to target chat")
    print("5. Send 5 numbers every 2 seconds")
    print("="*70)
    
    # Fix ChromeDriver first
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"\n❌ ChromeDriver not found at: {driver_path}")
        print("\nPlease download ChromeDriver:")
        print("1. Go to: https://chromedriver.chromium.org/")
        print("2. Download matching version")
        print("3. Place in: C:\\Users\\rosha\\Downloads\\chrome_automation\\")
        return
    
    print(f"✅ ChromeDriver found")
    
    # Configuration
    print(f"\n⚙️ Configuration:")
    print(f"   Starting digit: 6")
    print(f"   Numbers: 10-digit Indian")
    print(f"   Interval: 2 seconds")
    print(f"   Each message: 5 numbers")
    
    print(f"\n🚀 Starting in 5 seconds...")
    print("   Close all Chrome windows first!")
    time.sleep(5)
    
    # Create and run bot
    bot = TelegramBot(1, 6)  # Single browser with digit 6
    bot.run_bot()
    
    print(f"\n" + "="*70)
    print("🎉 Bot finished!")
    print("="*70)

# SIMPLE TEST FUNCTION
def test_chromedriver():
    """Test if ChromeDriver works"""
    print("🔧 Testing ChromeDriver...")
    
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"❌ ChromeDriver not found!")
        return False
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service)
        
        driver.get("https://www.google.com")
        print("✅ ChromeDriver test PASSED!")
        print("✅ Chrome opened successfully")
        
        time.sleep(3)
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test FAILED: {e}")
        
        # Version mismatch error
        if "version" in str(e).lower() and "chrome" in str(e).lower():
            print("\n🔧 VERSION MISMATCH DETECTED!")
            print("Please fix ChromeDriver version:")
            print("1. Check Chrome version: chrome://version/")
            print("2. Download matching ChromeDriver from:")
            print("   https://chromedriver.chromium.org/")
            print("3. Replace the chromedriver.exe file")
        
        return False

if __name__ == "__main__":
    # First test ChromeDriver
    if test_chromedriver():
        print("\n" + "="*70)
        print("✅ ChromeDriver working, starting main bot...")
        print("="*70)
        time.sleep(2)
        main()
    else:
        print("\n❌ Please fix ChromeDriver first!")
