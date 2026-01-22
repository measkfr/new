
import subprocess
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
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
        """Setup Chrome with Telegram-friendly options"""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Telegram-specific - prevent detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to look like real user
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable notifications
        chrome_options.add_argument("--disable-notifications")
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            
            if not os.path.exists(driver_path):
                print(f"❌ ChromeDriver nahi mila: {driver_path}")
                return False
            
            self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            
            # Execute JavaScript to hide automation
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            print(f"✅ Browser {self.browser_id}: Started")
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id} setup error: {e}")
            return False
    
    def login_to_telegram(self):
        """Navigate to Telegram Web and handle login"""
        try:
            print(f"Browser {self.browser_id}: Opening Telegram...")
            
            # Open Telegram Web
            self.driver.get("https://web.telegram.org/a/")
            print(f"✅ Browser {self.browser_id}: Telegram opened")
            
            # Wait for page load
            time.sleep(5)
            
            # Check if already logged in or need login
            try:
                # Look for login elements
                login_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Log in') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
                
                if login_elements:
                    print(f"⚠️ Browser {self.browser_id}: Login required")
                    print(f"   Please login manually in Browser {self.browser_id}")
                    
                    # Wait for manual login
                    print(f"⏳ Browser {self.browser_id}: Waiting 60 seconds for manual login...")
                    for i in range(60):
                        time.sleep(1)
                        if i % 10 == 0:
                            print(f"   {60-i} seconds remaining...")
                    
                    # Check if logged in by looking for chat elements
                    try:
                        chat_elements = self.driver.find_elements(By.CSS_SELECTOR, ".chat, .dialog, [data-peer-id]")
                        if chat_elements:
                            print(f"✅ Browser {self.browser_id}: Login successful")
                        else:
                            print(f"⚠️ Browser {self.browser_id}: Still on login page")
                    except:
                        pass
                else:
                    print(f"✅ Browser {self.browser_id}: Already logged in")
                    
            except Exception as e:
                print(f"⚠️ Browser {self.browser_id}: Login check error - {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Telegram error - {e}")
            return False
    
    def navigate_to_target_chat(self):
        """Navigate to specific chat URL"""
        try:
            print(f"Browser {self.browser_id}: Going to target chat...")
            
            # Direct URL to specific chat
            target_url = "https://web.telegram.org/a/?account=2#8549408740"
            self.driver.get(target_url)
            
            print(f"✅ Browser {self.browser_id}: Target chat opened")
            
            # Wait for chat to load
            time.sleep(5)
            
            # Check if chat loaded
            try:
                # Look for message input field
                input_field = self.find_message_input()
                if input_field:
                    print(f"✅ Browser {self.browser_id}: Chat loaded successfully")
                    return True
                else:
                    print(f"⚠️ Browser {self.browser_id}: Chat loading... waiting more")
                    time.sleep(5)
                    return True
            except:
                return True
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Chat navigation error - {e}")
            return False
    
    def find_message_input(self):
        """Find Telegram message input field"""
        print(f"Browser {self.browser_id}: Finding message box...")
        
        # Telegram Web has specific classes for message input
        telegram_selectors = [
            # New Telegram Web selectors
            ".input-message-container .input-message-input",
            "[contenteditable='true'][placeholder*='Message']",
            "[contenteditable='true'][data-placeholder*='Message']",
            ".composer .message-input",
            ".input-field .input-text",
            
            # Common contenteditable divs
            "[contenteditable='true']",
            ".ProseMirror",
            
            # Alternative selectors
            "div[data-role='message-input']",
            ".chat-input",
            ".message-input",
            
            # Try by placeholder text
            "*[placeholder*='message']",
            "*[placeholder*='Message']",
            "*[placeholder*='Type a message']",
        ]
        
        for selector in telegram_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            # Check if it's likely a message input
                            placeholder = element.get_attribute('placeholder') or ''
                            if 'message' in placeholder.lower() or 'type' in placeholder.lower():
                                print(f"✅ Browser {self.browser_id}: Found by placeholder - {selector}")
                                return element
                            elif '[contenteditable' in selector:
                                # For contenteditable, check size and position
                                location = element.location
                                size = element.size
                                if size['width'] > 100 and size['height'] > 20:
                                    print(f"✅ Browser {self.browser_id}: Found contenteditable - {selector}")
                                    return element
                    except:
                        continue
            except:
                continue
        
        # Try by finding the bottom area of chat
        print(f"Browser {self.browser_id}: Trying advanced search...")
        try:
            # Look for footer or bottom container
            footer_selectors = [
                ".chat-footer",
                ".message-input-container",
                ".input-message-container",
                ".composer-container"
            ]
            
            for selector in footer_selectors:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Find all contenteditable inside
                    inputs = container.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                    if inputs:
                        print(f"✅ Browser {self.browser_id}: Found in footer - {selector}")
                        return inputs[0]
                except:
                    continue
        except Exception as e:
            print(f"Browser {self.browser_id}: Footer search error - {e}")
        
        # Last resort: Take screenshot for debugging
        try:
            self.driver.save_screenshot(f'telegram_browser_{self.browser_id}.png')
            print(f"📸 Browser {self.browser_id}: Screenshot saved for debugging")
        except:
            pass
        
        print(f"❌ Browser {self.browser_id}: Message input not found")
        return None
    
    def send_telegram_message(self, input_field, message):
        """Send message in Telegram"""
        try:
            print(f"Browser {self.browser_id}: Sending message...")
            
            # Clear existing text if any
            try:
                input_field.clear()
                time.sleep(0.5)
            except:
                # For contenteditable, use JavaScript
                self.driver.execute_script("arguments[0].innerHTML = '';", input_field)
                time.sleep(0.5)
            
            # Click to focus
            input_field.click()
            time.sleep(0.5)
            
            # Type message
            input_field.send_keys(message)
            time.sleep(1)
            
            # Press Enter to send
            input_field.send_keys(Keys.RETURN)
            
            print(f"✅ Browser {self.browser_id}: Message sent: {message}")
            time.sleep(1)  # Wait for message to send
            
            return True
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Send error - {e}")
            return False
    
    def send_numbers_batch(self):
        """Generate and send 5 numbers"""
        numbers_to_send = ""
        
        for i in range(5):
            number = self.generate_indian_number()
            numbers_to_send += number
            if i < 4:
                numbers_to_send += " "
        
        return numbers_to_send
    
    def run_automation(self):
        """Main automation flow"""
        print(f"\n{'='*60}")
        print(f"🤖 TELEGRAM BOT - Browser {self.browser_id} (Digit: {self.starting_digit})")
        print(f"{'='*60}")
        
        # Setup Chrome
        if not self.setup_chrome():
            print(f"❌ Browser {self.browser_id}: Setup failed")
            return
        
        try:
            # Step 1: Login to Telegram
            print(f"\n📱 STEP 1: Telegram Login")
            print(f"{'-'*40}")
            if not self.login_to_telegram():
                print(f"⚠️ Browser {self.browser_id}: Login issue, but continuing...")
            
            # Step 2: Navigate to target chat
            print(f"\n💬 STEP 2: Target Chat")
            print(f"{'-'*40}")
            if not self.navigate_to_target_chat():
                print(f"❌ Browser {self.browser_id}: Cannot access chat")
                return
            
            # Step 3: Find message input
            print(f"\n🔍 STEP 3: Find Message Box")
            print(f"{'-'*40}")
            input_field = self.find_message_input()
            
            if not input_field:
                print(f"❌ Browser {self.browser_id}: Cannot find message box")
                print("Trying alternative method...")
                
                # Try clicking in chat area
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body.click()
                    time.sleep(1)
                    
                    # Try finding input again
                    input_field = self.find_message_input()
                except:
                    pass
            
            if input_field:
                print(f"\n🎯 Browser {self.browser_id}: READY TO SEND!")
                print(f"📊 Will send 5 numbers every 2 seconds")
                print(f"⏸️ Press Ctrl+C to stop")
                print(f"{'-'*40}")
                
                batch_count = 0
                try:
                    while True:
                        batch_count += 1
                        print(f"\n📦 Browser {self.browser_id}: Batch #{batch_count}")
                        
                        # Generate and send numbers
                        numbers = self.send_numbers_batch()
                        
                        if self.send_telegram_message(input_field, numbers):
                            print(f"✅ Sent: {numbers}")
                        else:
                            print(f"⚠️ Failed to send, retrying...")
                            time.sleep(2)
                            continue
                        
                        # Wait 2 seconds before next batch
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    print(f"\n⏹️ Browser {self.browser_id}: Stopped by user")
                    
                except Exception as e:
                    print(f"❌ Browser {self.browser_id}: Error in loop - {e}")
                    
            else:
                print(f"\n❌ Browser {self.browser_id}: Cannot proceed without message box")
                print("Possible reasons:")
                print("1. Not logged into Telegram")
                print("2. Wrong chat URL")
                print("3. Page not loaded properly")
                print("\nCheck screenshot: telegram_browser_{self.browser_id}.png")
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Fatal error - {e}")
        
        finally:
            print(f"\n{'='*40}")
            print(f"Browser {self.browser_id}: Process ended")
            print(f"Browser will close in 10 seconds...")
            time.sleep(10)
            try:
                self.driver.quit()
                print(f"✅ Browser {self.browser_id}: Closed")
            except:
                pass

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM INDIAN NUMBERS AUTOMATION BOT")
    print("="*70)
    print("📱 Login: https://web.telegram.org/a/")
    print("💬 Chat: https://web.telegram.org/a/?account=2#8549408740")
    print("="*70)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"\n❌ ERROR: ChromeDriver not found!")
        print(f"Path: {driver_path}")
        print("\n📌 Please ensure chromedriver.exe is in this folder")
        print("📌 Download from: https://chromedriver.chromium.org/")
        return
    
    print(f"✅ ChromeDriver found: {driver_path}")
    
    # Configuration
    total_browsers = 1  # Start with 1 for testing
    # total_browsers = 10  # Uncomment for full run
    
    # Digits distribution
    starting_digits = [6] * 3 + [8] * 3 + [9] * 4
    
    if total_browsers < 10:
        starting_digits = starting_digits[:total_browsers]
    
    print(f"\n⚙️ Configuration:")
    print(f"   Browsers: {total_browsers}")
    print(f"   Digits: {starting_digits}")
    print(f"   Format: 10-digit Indian numbers")
    print(f"   Interval: 2 seconds between messages")
    print(f"   Each message: 5 numbers")
    print("\n" + "="*70)
    
    # IMPORTANT INSTRUCTIONS
    print("\n📋 IMPORTANT INSTRUCTIONS:")
    print("1. Close ALL Chrome browsers before starting")
    print("2. You may need to login manually in each browser")
    print("3. Make sure QR code scanner is ready")
    print("4. Run as Administrator")
    print("\n⏳ Starting in 10 seconds...")
    time.sleep(10)
    
    # Shared numbers set
    all_generated_numbers = set()
    
    def browser_worker(browser_id, starting_digit):
        bot = TelegramAutomation(browser_id, starting_digit)
        bot.generated_numbers = all_generated_numbers
        bot.run_automation()
    
    # Run browsers
    print("\n🚀 Launching browsers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_browsers) as executor:
        futures = []
        
        for i in range(total_browsers):
            print(f"\n📦 Launching Browser {i+1}/10...")
            future = executor.submit(browser_worker, i+1, starting_digits[i])
            futures.append(future)
            time.sleep(3)  # Stagger launches
        
        try:
            # Monitor progress
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Thread error: {e}")
        except KeyboardInterrupt:
            print("\n\n🛑 Script stopped by user!")
    
    print("\n" + "="*70)
    print("🎉 AUTOMATION COMPLETED!")
    print(f"📊 Total unique numbers sent: {len(all_generated_numbers)}")
    print(f"📁 Screenshots saved in current folder")
    print("="*70)

if __name__ == "__main__":
    try:
        from selenium import webdriver
        print("✅ Selenium ready")
    except ImportError:
        print("❌ Install: pip install selenium")
        exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Main error: {e}")
        print("\n💡 Tips:")
        print("1. Update ChromeDriver")
        print("2. Disable antivirus")
        print("3. Run CMD as Admin")
        print("4. Check internet connection")
