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
import concurrent.futures
import os

class ChromeAutomation:
    def __init__(self, browser_id, starting_digit):
        self.browser_id = browser_id
        self.starting_digit = starting_digit
        self.driver = None
        self.generated_numbers = set()
        
    def generate_indian_number(self):
        """Generate a valid 10-digit Indian phone number starting with specific digit"""
        while True:
            # First digit is fixed based on browser type
            number = str(self.starting_digit)
            
            # Generate remaining 9 digits
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            # Check if number is unique across all browsers
            if number not in self.generated_numbers and len(number) == 10:
                self.generated_numbers.add(number)
                return number
    
    def setup_chrome(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Add more options to prevent detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            # YEH LINE IMPORTANT HAI - ChromeDriver ka path specify karo
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            
            # Check karo file exist karti hai ya nahi
            if not os.path.exists(driver_path):
                print(f"ERROR: ChromeDriver nahi mila! Path check karo: {driver_path}")
                print("Please ensure chromedriver.exe is at this location")
                return False
            
            self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            
            # Remove automation flags
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ Browser {self.browser_id} started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting browser {self.browser_id}: {e}")
            print("Tips:")
            print("1. ChromeDriver sahi jagah hai na check karo")
            print("2. Chrome updated hai na?")
            print("3. Antivirus disable karke try karo")
            return False
    
    def login_to_rab(self):
        """Navigate to https://web.telegram.org/a/ and wait"""
        try:
            print(f"Browser {self.browser_id}: Opening https://web.telegram.org/a/...")
            self.driver.get("https://web.telegram.org/a/")
            print(f"✅ Browser {self.browser_id}: Opened https://web.telegram.org/a/")
            
            # Wait for 1 minute with progress
            print(f"Browser {self.browser_id}: Waiting 60 seconds...")
            for i in range(60):
                time.sleep(1)
                if i % 10 == 0:
                    print(f"Browser {self.browser_id}: {60-i} seconds remaining...")
            
            # Refresh the page
            self.driver.refresh()
            print(f"✅ Browser {self.browser_id}: Refreshed https://web.telegram.org/a/")
            
            return True
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Error with rab.com - {e}")
            return False
    
    def navigate_to_rav(self):
        """Navigate to www.rav.com"""
        try:
            print(f"Browser {self.browser_id}: Going to https://web.telegram.org/a/?account=2#8549408740...")
            self.driver.get("https://web.telegram.org/a/?account=2#8549408740")
            print(f"✅ Browser {self.browser_id}: Navigated to https://web.telegram.org/a/?account=2#8549408740")
            time.sleep(2)  # Wait for page to load
            return True
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Error navigating to https://web.telegram.org/a/?account=2#8549408740 - {e}")
            return False
    
    def find_and_fill_message_field(self):
        """Find message field using advanced methods"""
        print(f"Browser {self.browser_id}: Looking for message field...")
        
        try:
            # Pehle screenshots lete hai page ka
            self.driver.save_screenshot(f'browser_{self.browser_id}_page.png')
            print(f"Browser {self.browser_id}: Screenshot saved for debugging")
            
            # Try different methods to find input field
            time.sleep(3)
            
            # Method 1: Try to find by common input fields
            input_fields = []
            
            # All possible input/textarea elements
            try:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                input_fields = all_inputs + all_textareas
            except:
                pass
            
            # Filter visible and enabled fields
            visible_fields = []
            for field in input_fields:
                try:
                    if field.is_displayed() and field.is_enabled():
                        visible_fields.append(field)
                except:
                    continue
            
            if visible_fields:
                print(f"Browser {self.browser_id}: Found {len(visible_fields)} visible fields")
                
                # Try each field by sending test text
                for idx, field in enumerate(visible_fields):
                    try:
                        field.clear()
                        field.send_keys("TEST123")
                        time.sleep(1)
                        
                        # Check if text was entered
                        entered_text = field.get_attribute('value')
                        if entered_text == "TEST123":
                            print(f"✅ Browser {self.browser_id}: Found working field #{idx+1}")
                            field.clear()
                            return field
                        else:
                            field.clear()
                    except:
                        continue
            
            # Method 2: Try by placeholder or name
            print(f"Browser {self.browser_id}: Trying search by attributes...")
            
            search_terms = ['message', 'chat', 'text', 'type', 'input', 'write', 'comment']
            
            for term in search_terms:
                try:
                    # Try CSS selectors
                    selectors = [
                        f"input[placeholder*='{term}']",
                        f"textarea[placeholder*='{term}']",
                        f"input[name*='{term}']",
                        f"textarea[name*='{term}']",
                        f"input[id*='{term}']",
                        f"textarea[id*='{term}']",
                        f"input[class*='{term}']",
                        f"textarea[class*='{term}']"
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    print(f"✅ Browser {self.browser_id}: Found field with selector: {selector}")
                                    return element
                        except:
                            continue
                except:
                    continue
            
            # Method 3: Try contenteditable divs (for modern chat apps)
            try:
                editable_divs = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                for div in editable_divs:
                    if div.is_displayed() and div.is_enabled():
                        print(f"✅ Browser {self.browser_id}: Found contenteditable field")
                        return div
            except:
                pass
            
            print(f"❌ Browser {self.browser_id}: No input field found")
            return None
            
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Error finding message field - {e}")
            return None
    
    def send_numbers_continuously(self, input_field):
        """Send 5 random numbers"""
        try:
            numbers_to_send = ""
            
            for i in range(5):
                number = self.generate_indian_number()
                numbers_to_send += number
                if i < 4:  # Last me space mat dalo
                    numbers_to_send += " "
            
            print(f"Browser {self.browser_id}: Generated: {numbers_to_send}")
            
            # Clear and send
            try:
                input_field.clear()
            except:
                pass
            
            input_field.send_keys(numbers_to_send)
            print(f"✅ Browser {self.browser_id}: Sent: {numbers_to_send}")
            
            # Try to press Enter (optional)
            try:
                input_field.send_keys(Keys.RETURN)
                time.sleep(0.5)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Error sending - {e}")
    
    def run_automation(self):
        """Main automation flow"""
        print(f"\n{'='*50}")
        print(f"🚀 STARTING BROWSER {self.browser_id} (Digit: {self.starting_digit})")
        print(f"{'='*50}")
        
        # Setup Chrome
        if not self.setup_chrome():
            print(f"❌ Browser {self.browser_id}: Setup failed!")
            return
        
        try:
            # Step 1: rab.com
            if not self.login_to_rab():
                print(f"⚠️ Browser {self.browser_id}: Skipping to next step...")
            
            # Step 2: rav.com
            if not self.navigate_to_rav():
                print(f"❌ Browser {self.browser_id}: Cannot continue without rav.com")
                return
            
            # Step 3: Find field
            input_field = self.find_and_fill_message_field()
            
            if input_field:
                print(f"🎯 Browser {self.browser_id}: READY TO SEND NUMBERS!")
                print(f"📝 Sending 5 numbers every 2 seconds...")
                print(f"🎯 Press Ctrl+C to stop")
                
                counter = 0
                try:
                    while True:
                        counter += 1
                        print(f"\nBrowser {self.browser_id}: Batch #{counter}")
                        self.send_numbers_continuously(input_field)
                        time.sleep(2)  # Wait 2 seconds
                        
                except KeyboardInterrupt:
                    print(f"\n⏹️ Browser {self.browser_id}: Stopped by user")
                except Exception as e:
                    print(f"❌ Browser {self.browser_id}: Error - {e}")
            else:
                print(f"⚠️ Browser {self.browser_id}: No input field. Check screenshot.")
                
        except Exception as e:
            print(f"❌ Browser {self.browser_id}: Fatal error - {e}")
        
        finally:
            print(f"\nBrowser {self.browser_id}: Process completed")
            print("Browser will remain open for 30 seconds...")
            time.sleep(30)
            try:
                self.driver.quit()
                print(f"✅ Browser {self.browser_id}: Closed")
            except:
                pass

def main():
    print("\n" + "="*60)
    print("🤖 CHROME AUTOMATION BOT - INDIAN NUMBERS SENDER")
    print("="*60)
    
    # Test ChromeDriver path first
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"\n❌ CRITICAL ERROR: ChromeDriver not found!")
        print(f"Please ensure this file exists: {driver_path}")
        print("\nFollow these steps:")
        print("1. Download ChromeDriver from: https://chromedriver.chromium.org/")
        print("2. Extract the zip file")
        print("3. Copy 'chromedriver.exe' to: C:\\Users\\rosha\\Downloads\\chrome_automation\\")
        print("4. Run the script again")
        return
    
    print(f"✅ ChromeDriver found at: {driver_path}")
    
    # Configuration
    total_browsers = 1  # Pehle 1 se test karo, phir badhao
    # total_browsers = 10  # Baad me isko use karna
    
    # Distribute starting digits
    starting_digits = [6] * 3 + [8] * 3 + [9] * 4
    
    # Limit for testing
    if total_browsers < 10:
        starting_digits = starting_digits[:total_browsers]
    
    print(f"\n📊 Configuration:")
    print(f"Total Browsers: {total_browsers}")
    print(f"Starting Digits: {starting_digits}")
    print(f"Numbers Format: 10-digit Indian (starting with 6/8/9)")
    print(f"Sending: 5 numbers every 2 seconds")
    print("\n" + "="*60)
    
    # Shared numbers set
    all_generated_numbers = set()
    
    def browser_worker(browser_id, starting_digit):
        automation = ChromeAutomation(browser_id, starting_digit)
        automation.generated_numbers = all_generated_numbers
        automation.run_automation()
    
    # Run browsers
    print("\n🚀 Starting automation in 5 seconds...")
    print("📢 Note: Close all Chrome browsers before starting!")
    time.sleep(5)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_browsers) as executor:
        futures = []
        for i in range(total_browsers):
            print(f"\n📦 Launching Browser {i+1}...")
            future = executor.submit(browser_worker, i+1, starting_digits[i])
            futures.append(future)
            time.sleep(2)  # Stagger starts
        
        try:
            # Wait for completion
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Thread error: {e}")
        except KeyboardInterrupt:
            print("\n\n⏹️ Script stopped by user!")
    
    print("\n" + "="*60)
    print("🎉 AUTOMATION COMPLETED!")
    print(f"📊 Total unique numbers generated: {len(all_generated_numbers)}")
    print("="*60)

if __name__ == "__main__":
    # Check dependencies
    try:
        from selenium import webdriver
        print("✅ Selenium is installed")
    except ImportError:
        print("❌ Selenium not installed!")
        print("Run: pip install selenium")
        exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script terminated by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check ChromeDriver path")
        print("2. Close all Chrome windows")
        print("3. Run CMD as Administrator")
        print("4. Disable antivirus temporarily")
