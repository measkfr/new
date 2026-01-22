import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os

class TelegramSessionBot:
    def __init__(self):
        self.driver = None
        self.tabs = []
        self.all_numbers = set()
        self.cookies = None
        self.local_storage = None
        
    def setup_browser(self):
        """Setup Chrome with session preservation"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Important: Use user data directory
        user_data_dir = os.path.join(os.path.expanduser("~"), "telegram_session")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Browser started with session persistence")
            return True
        except Exception as e:
            print(f"❌ Browser setup error: {e}")
            return False
    
    def wait_for_manual_login(self):
        """Wait for user to manually login in first tab"""
        print("\n" + "="*60)
        print("📱 MANUAL LOGIN REQUIRED")
        print("="*60)
        
        # Open Telegram
        self.driver.get("https://web.telegram.org/a/")
        print("✅ Telegram opened in first tab")
        
        # Store first tab
        self.tabs.append(self.driver.current_window_handle)
        
        print("\n🔑 Please login manually using QR code")
        print("⏳ Waiting for login... (Press Enter when done)")
        print("="*60)
        
        # Keep checking if login is successful
        login_success = False
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while time.time() - start_time < timeout:
            try:
                # Check if we're on login page or chat page
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # If URL changes from login page or we see chat elements
                if "#" in current_url or "chat" in page_source or "dialog" in page_source:
                    print("✅ Login detected!")
                    login_success = True
                    break
                
                # Also check for logged-in indicators
                try:
                    # Look for chat list or message input
                    elements = self.driver.find_elements(By.CSS_SELECTOR, ".chat, .dialog, [contenteditable='true']")
                    if len(elements) > 0:
                        print("✅ Chat elements found - login successful!")
                        login_success = True
                        break
                except:
                    pass
                
                # Check every 5 seconds
                time.sleep(5)
                print("⏳ Still waiting for login... (Press Enter when done)")
                
            except Exception as e:
                print(f"⚠️ Check error: {e}")
                time.sleep(5)
        
        if not login_success:
            print("❌ Login timeout. Please login manually and press Enter")
            input("Press Enter after login: ")
        
        print("✅ Login process complete")
        
        # Save session data
        self.save_session_data()
        
        return True
    
    def save_session_data(self):
        """Save cookies and localStorage"""
        try:
            # Save cookies
            self.cookies = self.driver.get_cookies()
            
            # Save localStorage via JavaScript
            self.local_storage = self.driver.execute_script("""
                let ls = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    ls[key] = localStorage.getItem(key);
                }
                return ls;
            """)
            
            print("✅ Session data saved")
            return True
        except Exception as e:
            print(f"⚠️ Could not save session: {e}")
            return False
    
    def create_additional_tabs(self):
        """Create 9 more tabs with same session"""
        print("\n➕ Creating additional tabs...")
        
        for i in range(9):
            try:
                # Open new tab
                self.driver.execute_script("window.open('');")
                
                # Get all window handles
                all_handles = self.driver.window_handles
                
                # Switch to new tab (last one)
                new_tab = all_handles[-1]
                self.driver.switch_to.window(new_tab)
                
                # Store tab handle
                self.tabs.append(new_tab)
                
                # Open Telegram in new tab
                self.driver.get("https://web.telegram.org/a/")
                
                # Wait and check if logged in
                time.sleep(3)
                
                # Check if logged in by looking for chat elements
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, ".chat, .dialog, [contenteditable='true']")
                    if elements:
                        print(f"✅ Tab {i+2}/10: Logged in successfully")
                    else:
                        print(f"⚠️ Tab {i+2}/10: May need manual intervention")
                except:
                    print(f"✅ Tab {i+2}/10: Created")
                
            except Exception as e:
                print(f"❌ Tab {i+2}/10 creation error: {e}")
        
        print(f"\n🎯 Total tabs: {len(self.tabs)}")
        
        # Switch back to first tab
        self.driver.switch_to.window(self.tabs[0])
        return True
    
    def navigate_all_tabs_to_chat(self):
        """Navigate all tabs to target chat"""
        print("\n💬 Navigating all tabs to target chat...")
        
        target_url = "https://web.telegram.org/a/?account=2#8549408740"
        
        for i, tab in enumerate(self.tabs):
            try:
                # Switch to tab
                self.driver.switch_to.window(tab)
                
                # Check if we're already on Telegram
                current_url = self.driver.current_url
                if "web.telegram.org" not in current_url:
                    # First go to main Telegram
                    self.driver.get("https://web.telegram.org/a/")
                    time.sleep(2)
                
                # Now go to target chat
                self.driver.get(target_url)
                
                # Wait for chat to load
                time.sleep(3)
                
                print(f"✅ Tab {i+1}: Target chat opened")
                
            except Exception as e:
                print(f"❌ Tab {i+1}: Navigation error - {e}")
        
        # Switch back to first tab
        self.driver.switch_to.window(self.tabs[0])
        return True
    
    def find_message_box_advanced(self, tab_index):
        """Advanced method to find message box with retry"""
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Switch to tab
                self.driver.switch_to.window(self.tabs[tab_index])
                
                # Wait a bit
                time.sleep(1)
                
                # Method 1: Look for contenteditable
                editables = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                for elem in editables:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            size = elem.size
                            if size['width'] > 100:
                                return elem
                    except:
                        continue
                
                # Method 2: Look for input/textarea
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                for elem in inputs + textareas:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            placeholder = elem.get_attribute('placeholder') or ''
                            if 'message' in placeholder.lower() or 'type' in placeholder.lower():
                                return elem
                            elif elem.size['width'] > 100:
                                return elem
                    except:
                        continue
                
                # Method 3: Try clicking at likely position
                if attempt > 2:  # Only try clicking after few attempts
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
                
                # Method 4: Look for Telegram specific classes
                telegram_classes = ['composer_rich_textarea', 'input-message-input', 'im_editable']
                for class_name in telegram_classes:
                    try:
                        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                        for elem in elements:
                            if elem.is_displayed():
                                return elem
                    except:
                        continue
                
                if attempt < max_attempts - 1:
                    print(f"⚠️ Tab {tab_index+1}: Message box not found, retrying ({attempt+1}/{max_attempts})")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"⚠️ Tab {tab_index+1}: Search error - {e}")
                time.sleep(2)
        
        print(f"❌ Tab {tab_index+1}: Could not find message box after {max_attempts} attempts")
        return None
    
    def generate_indian_number(self, starting_digit):
        """Generate unique 10-digit Indian number"""
        while True:
            number = str(starting_digit)
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.all_numbers:
                self.all_numbers.add(number)
                return number
    
    def check_tab_logged_in(self, tab_index):
        """Check if tab is logged in"""
        try:
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Check URL
            current_url = self.driver.current_url
            if "web.telegram.org" not in current_url:
                return False
            
            # Check for chat elements
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, ".chat, .dialog, [contenteditable='true']")
                return len(elements) > 0
            except:
                return False
                
        except:
            return False
    
    def send_from_tab(self, tab_index):
        """Send message from specific tab"""
        # Determine starting digit based on tab index
        if tab_index < 3:  # Tabs 1-3
            starting_digit = 6
        elif tab_index < 6:  # Tabs 4-6
            starting_digit = 8
        else:  # Tabs 7-10
            starting_digit = 9
        
        # Check if tab is logged in
        if not self.check_tab_logged_in(tab_index):
            print(f"⚠️ Tab {tab_index+1}: Not logged in, trying to fix...")
            
            try:
                # Try to reload Telegram
                self.driver.switch_to.window(self.tabs[tab_index])
                self.driver.get("https://web.telegram.org/a/")
                time.sleep(3)
                
                # Check again
                if not self.check_tab_logged_in(tab_index):
                    print(f"❌ Tab {tab_index+1}: Still not logged in, skipping")
                    return False
            except:
                print(f"❌ Tab {tab_index+1}: Error fixing login")
                return False
        
        # Find message box
        message_box = self.find_message_box_advanced(tab_index)
        if not message_box:
            print(f"❌ Tab {tab_index+1}: No message box found")
            return False
        
        # Generate 5 numbers
        numbers_list = []
        for _ in range(5):
            numbers_list.append(self.generate_indian_number(starting_digit))
        
        message = " ".join(numbers_list)
        
        try:
            # Switch to tab
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Focus and clear
            message_box.click()
            time.sleep(0.3)
            
            # Clear existing text
            try:
                if message_box.tag_name in ['input', 'textarea']:
                    message_box.clear()
                else:
                    self.driver.execute_script("arguments[0].innerHTML = '';", message_box)
            except:
                pass
            
            time.sleep(0.3)
            
            # Type message slowly
            for char in message:
                message_box.send_keys(char)
                time.sleep(0.01)
            
            time.sleep(0.3)
            
            # Send
            message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Tab {tab_index+1}[{starting_digit}]: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Tab {tab_index+1}: Send error - {e}")
            return False
    
    def run_automation(self):
        """Main automation flow"""
        print("\n" + "="*70)
        print("🤖 TELEGRAM SESSION-BASED AUTOMATION")
        print("="*70)
        
        # Setup browser
        if not self.setup_browser():
            return
        
        try:
            # Step 1: Manual login in first tab
            self.wait_for_manual_login()
            
            # Step 2: Create additional tabs
            self.create_additional_tabs()
            
            # Step 3: Navigate all to target chat
            self.navigate_all_tabs_to_chat()
            
            # Step 4: Continuously send messages
            print("\n" + "="*70)
            print("🚀 STARTING CONTINUOUS MESSAGING")
            print("="*70)
            print("📊 Tab Distribution:")
            print("  Tabs 1-3: Starting with 6")
            print("  Tabs 4-6: Starting with 8")
            print("  Tabs 7-10: Starting with 9")
            print("⏱️  Each tab sends 5 numbers every 2 seconds")
            print("🔄 Will retry failed tabs automatically")
            print("⏸️  Press Ctrl+C to stop")
            print("="*70)
            
            cycle_count = 0
            
            try:
                while True:
                    cycle_count += 1
                    print(f"\n🔄 CYCLE #{cycle_count}")
                    
                    # Track success/failure
                    success_count = 0
                    fail_count = 0
                    
                    # Try each tab
                    for i in range(len(self.tabs)):
                        try:
                            if self.send_from_tab(i):
                                success_count += 1
                            else:
                                fail_count += 1
                        except Exception as e:
                            print(f"❌ Tab {i+1}: Unexpected error - {e}")
                            fail_count += 1
                    
                    # Summary
                    print(f"\n📊 Cycle Summary:")
                    print(f"  Successful: {success_count}/10")
                    print(f"  Failed: {fail_count}/10")
                    
                    # Wait 2 seconds before next cycle
                    if cycle_count % 5 == 0:
                        print(f"\n⏳ Stats after {cycle_count} cycles:")
                        print(f"  Total unique numbers: {len(self.all_numbers)}")
                    
                    print(f"\n⏳ Waiting 2 seconds...")
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print(f"\n\n⏹️ Automation stopped by user")
                
            except Exception as e:
                print(f"\n❌ Automation error: {e}")
        
        except Exception as e:
            print(f"\n❌ Main error: {e}")
        
        finally:
            print("\n" + "="*70)
            print("📊 FINAL STATISTICS")
            print("="*70)
            print(f"Total cycles completed: {cycle_count}")
            print(f"Total unique numbers generated: {len(self.all_numbers)}")
            print(f"Tabs still active: {len(self.tabs)}")
            print("\n💡 Browser will remain open")
            print("="*70)

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM ONE-LOGIN MULTI-TAB BOT")
    print("="*70)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    
    if not os.path.exists(driver_path):
        print(f"❌ ChromeDriver not found!")
        print(f"Path: {driver_path}")
        return
    
    print("✅ ChromeDriver found")
    
    print("\n📋 HOW THIS WORKS:")
    print("1. ONE manual login in first tab")
    print("2. Automatic session sharing to other tabs")
    print("3. No refresh needed")
    print("4. Continuous retry for failed tabs")
    print("5. Tabs never close, keep trying")
    
    print("\n⚠️ IMPORTANT:")
    print("• Login ONLY in first tab")
    print("• Do NOT refresh any page")
    print("• Let bot handle everything after login")
    
    print("\n🚀 Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Create and run bot
    bot = TelegramSessionBot()
    bot.run_automation()

if __name__ == "__main__":
    main()
