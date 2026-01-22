import subprocess
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import concurrent.futures
import os

class TelegramAutomation:
    def __init__(self, browser_id, starting_digit):
        self.browser_id = browser_id
        self.starting_digit = starting_digit
        self.driver = None
        self.generated_numbers = set()
        
    def generate_indian_number(self):
        """Generate a valid 10-digit Indian phone number"""
        while True:
            number = str(self.starting_digit)
            
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.generated_numbers and len(number) == 10:
                self.generated_numbers.add(number)
                return number
    
    def setup_chrome(self):
        """Setup Chrome with correct Selenium 4 syntax"""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Prevent detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable notifications
        chrome_options.add_argument("--disable-notifications")
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            
            if not os.path.exists(driver_path):
                print(f"❌ ChromeDriver nahi mila: {driver_path}")
                print(f"Download from: https://chromedriver.chromium.org/")
                return False
            
            print(f"✅ Browser {self.browser_id}: ChromeDriver found")
            
            # NEW SELENIUM 4 SYNTAX - Service object use karo
            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Hide automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ Browser {self.browser_id}: Chrome opened successfully")
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Chrome open error - {e}")
            
            # Try alternative method
            try:
                print(f"🔄 Browser {self.browser_id}: Trying alternative method...")
                
                # Option 2: Add ChromeDriver to PATH
                os.environ['PATH'] += r';C:\Users\rosha\Downloads\chrome_automation'
                
                self.driver = webdriver.Chrome(options=chrome_options)
                print(f"✅ Browser {self.browser_id}: Chrome opened (alternative)")
                return True
            except Exception as e2:
                print(f"❌ Browser {self.browser_id}: Alternative also failed - {e2}")
                return False
    
    def login_to_telegram(self):
        """Navigate to Telegram Web"""
        try:
            print(f"🌐 Browser {self.browser_id}: Opening Telegram...")
            
            # Open Telegram Web
            self.driver.get("https://web.telegram.org/a/")
            print(f"✅ Browser {self.browser_id}: Telegram opened")
            
            # Wait for page load
            time.sleep(3)
            
            # Check page title
            print(f"📄 Browser {self.browser_id}: Page title: {self.driver.title}")
            
            # Check for login page
            page_html = self.driver.page_source.lower()
            if 'login' in page_html or 'qr' in page_html or 'scan' in page_html:
                print(f"📱 Browser {self.browser_id}: Login page detected")
                print(f"⏳ Please login manually with QR code")
                print(f"⏳ Waiting 30 seconds for login...")
                
                for i in range(30):
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"   {30-i} seconds remaining...")
            
            # Check if logged in
            time.sleep(2)
            current_url = self.driver.current_url
            print(f"🔗 Browser {self.browser_id}: Current URL: {current_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Telegram error - {e}")
            return False
    
    def navigate_to_target_chat(self):
        """Navigate to specific chat URL"""
        try:
            print(f"💬 Browser {self.browser_id}: Opening target chat...")
            
            # Target chat URL
            target_url = "https://web.telegram.org/a/?account=2#8549408740"
            
            # Check if already on this URL
            if self.driver.current_url != target_url:
                self.driver.get(target_url)
                print(f"✅ Browser {self.browser_id}: Target chat opened")
            else:
                print(f"✅ Browser {self.browser_id}: Already in target chat")
            
            # Wait for chat to load
            time.sleep(5)
            
            # Take screenshot for debugging
            try:
                screenshot_path = f"telegram_browser_{self.browser_id}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Browser {self.browser_id}: Screenshot saved: {screenshot_path}")
            except:
                pass
            
            return True
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Chat error - {e}")
            return False
    
    def find_message_input(self):
        """Find Telegram message input field"""
        print(f"🔍 Browser {self.browser_id}: Finding message box...")
        
        # Try multiple methods
        methods = [
            self._find_by_contenteditable,
            self._find_by_placeholder,
            self._find_by_class_name,
            self._find_by_xpath
        ]
        
        for method in methods:
            try:
                element = method()
                if element:
                    return element
            except:
                continue
        
        print(f"❌ Browser {self.browser_id}: Message box not found")
        return None
    
    def _find_by_contenteditable(self):
        """Find by contenteditable attribute"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    size = element.size
                    if size['width'] > 100:  # Message box should be wide
                        print(f"✅ Browser {self.browser_id}: Found contenteditable div")
                        return element
        except:
            pass
        return None
    
    def _find_by_placeholder(self):
        """Find by placeholder text"""
        placeholders = ['message', 'type a message', 'write a message']
        for text in placeholders:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[@placeholder[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]]")
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Browser {self.browser_id}: Found by placeholder")
                        return element
            except:
                continue
        return None
    
    def _find_by_class_name(self):
        """Find by common Telegram class names"""
        telegram_classes = [
            'input-message-input',
            'composer_rich_textarea',
            'message-input',
            'chat-input'
        ]
        
        for class_name in telegram_classes:
            try:
                elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Browser {self.browser_id}: Found by class: {class_name}")
                        return element
            except:
                continue
        return None
    
    def _find_by_xpath(self):
        """Find by XPath"""
        xpaths = [
            "//div[@role='textbox']",
            "//div[contains(@class, 'input')]",
            "//div[contains(@class, 'composer')]"
        ]
        
        for xpath in xpaths:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Browser {self.browser_id}: Found by XPath")
                        return element
            except:
                continue
        return None
    
    def send_message(self, input_field, message):
        """Send message in Telegram"""
        try:
            print(f"📤 Browser {self.browser_id}: Sending message...")
            
            # Click to focus
            input_field.click()
            time.sleep(0.5)
            
            # Clear if possible
            try:
                self.driver.execute_script("arguments[0].innerHTML = '';", input_field)
            except:
                pass
            
            # Type message character by character (more natural)
            for char in message:
                input_field.send_keys(char)
                time.sleep(0.01)  # Small delay for natural typing
            
            time.sleep(0.5)
            
            # Press Enter to send
            input_field.send_keys(Keys.RETURN)
            
            print(f"✅ Browser {self.browser_id}: Sent: {message}")
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Send error - {e}")
            return False
    
    def send_numbers_batch(self):
        """Generate 5 numbers"""
        numbers = []
        for _ in range(5):
            numbers.append(self.generate_indian_number())
        return " ".join(numbers)
    
    def run_automation(self):
        """Main automation flow"""
        print(f"\n{'='*50}")
        print(f"🤖 BROWSER {self.browser_id} STARTING")
        print(f"{'='*50}")
        
        # Setup Chrome
        if not self.setup_chrome():
            return
        
        try:
            # Step 1: Telegram
            if not self.login_to_telegram():
                print(f"⚠️ Browser {self.browser_id}: Telegram issue, continuing...")
            
            # Step 2: Target chat
            if not self.navigate_to_target_chat():
                return
            
            # Step 3: Find message box
            input_field = self.find_message_input()
            
            if not input_field:
                print(f"❌ Browser {self.browser_id}: No message box found")
                print(f"   Trying manual click...")
                
                # Try clicking in middle of screen
                try:
                    action = webdriver.ActionChains(self.driver)
                    action.move_by_offset(400, 500).click().perform()
                    time.sleep(2)
                    input_field = self.find_message_input()
                except:
                    pass
            
            if input_field:
                print(f"\n🎯 Browser {self.browser_id}: READY!")
                print(f"   Sending 5 numbers every 2 seconds")
                print(f"   Press Ctrl+C to stop")
                
                count = 0
                try:
                    while True:
                        count += 1
                        print(f"\n📦 Batch #{count}")
                        
                        # Generate numbers
                        numbers = self.send_numbers_batch()
                        
                        # Send message
                        if self.send_message(input_field, numbers):
                            print(f"✅ Success")
                        else:
                            print(f"⚠️ Failed, retrying...")
                            time.sleep(3)
                            continue
                        
                        # Wait 2 seconds
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    print(f"\n⏹️ Stopped")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print(f"\n❌ Browser {self.browser_id}: Cannot proceed")
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Fatal error - {e}")
        
        finally:
            print(f"\n📊 Browser {self.browser_id}: Finished")
            print(f"   Keeping browser open for 30 seconds...")
            time.sleep(30)
            try:
                self.driver.quit()
            except:
                pass

def main():
    print("\n" + "="*60)
    print("🤖 TELEGRAM AUTOMATION BOT v2.0")
    print("="*60)
    print("Selenium 4 Compatible")
    print("Fixed ChromeDriver Issue")
    print("="*60)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"\n❌ ChromeDriver not found!")
        print(f"Path: {driver_path}")
        print("\nSteps to fix:")
        print("1. Download from: https://chromedriver.chromium.org/")
        print("2. Extract zip file")
        print("3. Copy chromedriver.exe to above path")
        return
    
    print(f"✅ ChromeDriver: {driver_path}")
    
    # Configuration
    total_browsers = 1  # Start with 1
    starting_digits = [6] * 3 + [8] * 3 + [9] * 4
    starting_digits = starting_digits[:total_browsers]
    
    print(f"\n⚙️ Settings:")
    print(f"   Browsers: {total_browsers}")
    print(f"   Starting with digit: {starting_digits[0]}")
    print(f"   Interval: 2 seconds")
    
    print(f"\n📋 Instructions:")
    print("1. Make sure Chrome is installed")
    print("2. Close all Chrome windows")
    print("3. Ready QR code scanner on phone")
    print(f"\n⏳ Starting in 5 seconds...")
    time.sleep(5)
    
    # Shared numbers
    all_numbers = set()
    
    def worker(browser_id, digit):
        bot = TelegramAutomation(browser_id, digit)
        bot.generated_numbers = all_numbers
        bot.run_automation()
    
    print(f"\n🚀 Launching Browser 1...")
    
    # Single browser for testing
    worker(1, starting_digits[0])
    
    print(f"\n" + "="*60)
    print(f"📊 Total numbers: {len(all_numbers)}")
    print("="*60)

def check_installation():
    """Check if everything is installed"""
    print("🔍 Checking installation...")
    
    # Check Python
    try:
        import sys
        print(f"✅ Python: {sys.version}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Selenium
    try:
        import selenium
        print(f"✅ Selenium: {selenium.__version__}")
    except:
        print("❌ Selenium not installed")
        print("Run: pip install selenium")
        return False
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    if os.path.exists(driver_path):
        print(f"✅ ChromeDriver: Found")
    else:
        print(f"❌ ChromeDriver: Not found at {driver_path}")
        return False
    
    return True

if __name__ == "__main__":
    print("🤖 Telegram Bot - Starting...")
    
    if check_installation():
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n👋 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("\n❌ Please fix installation issues first")
