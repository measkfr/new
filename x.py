import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

class TelegramMasterBot:
    def __init__(self):
        self.driver = None
        self.tabs = []
        self.all_numbers = set()
        self.first_tab_ready = False
        
    def setup_chrome(self):
        """Setup Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Add user data for session persistence
        chrome_options.add_argument(f"--user-data-dir=C:\\Users\\rosha\\telegram_session")
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Chrome started with session persistence")
            return True
        except Exception as e:
            print(f"❌ Chrome setup error: {e}")
            return False
    
    def wait_for_first_tab_login_and_setup(self):
        """Wait for first tab to be completely ready"""
        print("\n" + "="*60)
        print("🔑 STEP 1: FIRST TAB SETUP")
        print("="*60)
        
        # Step 1: Open Telegram
        self.driver.get("https://web.telegram.org/a/")
        print("✅ Telegram opened in first tab")
        
        # Store first tab
        self.tabs.append(self.driver.current_window_handle)
        print(f"📌 First tab stored: {self.tabs[0][:10]}...")
        
        print("\n📱 PLEASE LOGIN MANUALLY WITH QR CODE")
        print("⏳ Waiting for login completion...")
        print("="*60)
        
        # Phase 1: Wait for login
        login_complete = False
        while not login_complete:
            try:
                # Check for login indicators
                current_url = self.driver.current_url
                page_text = self.driver.page_source.lower()
                
                # Login successful indicators
                if "#" in current_url or "chat" in page_text or "dialog" in page_text:
                    login_complete = True
                    print("✅ Login detected!")
                else:
                    # Check for QR code or login page
                    if "qr" in page_text or "login" in page_text or "scan" in page_text:
                        print("⏳ Still on login page... Please scan QR code")
                    else:
                        print("⏳ Waiting for login...")
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Login check error: {e}")
                time.sleep(5)
        
        # Phase 2: Navigate to target chat
        print("\n📍 Navigating to target chat...")
        target_url = "https://web.telegram.org/a/?account=2#8549408740"
        self.driver.get(target_url)
        time.sleep(5)
        print("✅ Target chat opened")
        
        # Phase 3: Find message box in first tab
        print("\n🔍 Finding message box in first tab...")
        first_tab_message_box = self.find_message_box_with_retry(0)
        
        if not first_tab_message_box:
            print("❌ Could not find message box in first tab")
            return False
        
        # Phase 4: Test sending a message in first tab
        print("\n🧪 Testing message sending in first tab...")
        test_success = self.test_send_message(0, first_tab_message_box)
        
        if not test_success:
            print("❌ First tab test failed")
            return False
        
        print("\n✅ FIRST TAB IS FULLY READY!")
        print("   ✓ Logged in")
        print("   ✓ Target chat loaded")
        print("   ✓ Message box found")
        print("   ✓ Test message sent successfully")
        
        self.first_tab_ready = True
        return True
    
    def find_message_box_with_retry(self, tab_index=0, max_attempts=15):
        """Find message box with multiple retries"""
        print(f"🔍 Searching for message box (Attempts: {max_attempts})...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                if tab_index > 0:
                    self.driver.switch_to.window(self.tabs[tab_index])
                
                # Method 1: Contenteditable elements
                editables = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                for elem in editables:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            print(f"✅ Found contenteditable message box (Attempt {attempt})")
                            return elem
                    except:
                        continue
                
                # Method 2: Input/textarea elements
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                for elem in inputs + textareas:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            placeholder = elem.get_attribute('placeholder') or ''
                            if 'message' in placeholder.lower() or 'type' in placeholder.lower():
                                print(f"✅ Found input with placeholder (Attempt {attempt})")
                                return elem
                            elif elem.size['width'] > 100:
                                print(f"✅ Found wide input element (Attempt {attempt})")
                                return elem
                    except:
                        continue
                
                # Method 3: Click at likely position
                if attempt % 3 == 0:  # Try clicking every 3 attempts
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
                
                # Method 4: Telegram specific classes
                telegram_classes = ['composer_rich_textarea', 'input-message-input', 'im_editable']
                for class_name in telegram_classes:
                    try:
                        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                        for elem in elements:
                            if elem.is_displayed():
                                print(f"✅ Found by class '{class_name}' (Attempt {attempt})")
                                return elem
                    except:
                        continue
                
                if attempt < max_attempts:
                    print(f"⚠️ Attempt {attempt}/{max_attempts}: Message box not found, retrying...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"⚠️ Attempt {attempt} error: {e}")
                time.sleep(2)
        
        print(f"❌ Could not find message box after {max_attempts} attempts")
        return None
    
    def test_send_message(self, tab_index, message_box):
        """Test sending a message"""
        try:
            # Generate test number
            test_number = "6" + ''.join(str(random.randint(0, 9)) for _ in range(9))
            
            # Focus
            message_box.click()
            time.sleep(0.5)
            
            # Clear
            if message_box.tag_name in ['input', 'textarea']:
                message_box.clear()
            else:
                self.driver.execute_script("arguments[0].innerHTML = '';", message_box)
            
            time.sleep(0.5)
            
            # Type test message
            test_message = f"TEST {test_number}"
            for char in test_message:
                message_box.send_keys(char)
                time.sleep(0.02)
            
            time.sleep(0.5)
            
            # Send
            message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Test message sent: {test_message}")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Test send failed: {e}")
            return False
    
    def create_additional_tabs_only_after_first_ready(self):
        """Create additional tabs only after first tab is ready"""
        if not self.first_tab_ready:
            print("❌ First tab not ready yet!")
            return False
        
        print("\n" + "="*60)
        print("📑 STEP 2: CREATING ADDITIONAL TABS")
        print("="*60)
        
        target_url = "https://web.telegram.org/a/?account=2#8549408740"
        
        for i in range(9):
            try:
                print(f"\n➕ Creating tab {i+2}/10...")
                
                # Open new tab
                self.driver.execute_script("window.open('');")
                
                # Get all handles
                all_handles = self.driver.window_handles
                new_tab = all_handles[-1]
                
                # Switch to new tab
                self.driver.switch_to.window(new_tab)
                
                # Store tab
                self.tabs.append(new_tab)
                
                # Open Telegram with same session
                self.driver.get("https://web.telegram.org/a/")
                time.sleep(3)
                
                # Check if logged in automatically
                current_url = self.driver.current_url
                if "web.telegram.org" in current_url:
                    # Navigate to target chat
                    self.driver.get(target_url)
                    time.sleep(3)
                    
                    print(f"✅ Tab {i+2}: Created and navigated to chat")
                else:
                    print(f"⚠️ Tab {i+2}: May have session issue")
                
            except Exception as e:
                print(f"❌ Tab {i+2} creation error: {e}")
        
        print(f"\n🎯 Total tabs created: {len(self.tabs)}")
        
        # Switch back to first tab
        self.driver.switch_to.window(self.tabs[0])
        return True
    
    def initialize_all_tabs_message_boxes(self):
        """Initialize message boxes for all tabs"""
        print("\n" + "="*60)
        print("🔧 STEP 3: INITIALIZING ALL TABS")
        print("="*60)
        
        message_boxes = []
        
        for i in range(len(self.tabs)):
            print(f"\n🔍 Initializing tab {i+1}/10...")
            
            # Find message box for this tab
            msg_box = self.find_message_box_with_retry(i, max_attempts=10)
            
            if msg_box:
                message_boxes.append(msg_box)
                print(f"✅ Tab {i+1}: Ready")
            else:
                message_boxes.append(None)
                print(f"❌ Tab {i+1}: Not ready (will retry during sending)")
        
        return message_boxes
    
    def generate_indian_number(self, starting_digit):
        """Generate unique 10-digit Indian number"""
        while True:
            number = str(starting_digit)
            for _ in range(9):
                number += str(random.randint(0, 9))
            
            if number not in self.all_numbers:
                self.all_numbers.add(number)
                return number
    
    def get_starting_digit_for_tab(self, tab_index):
        """Get starting digit based on tab index"""
        if tab_index < 3:  # Tabs 1-3: digit 6
            return 6
        elif tab_index < 6:  # Tabs 4-6: digit 8
            return 8
        else:  # Tabs 7-10: digit 9
            return 9
    
    def send_from_tab_with_recovery(self, tab_index, message_boxes):
        """Send message from tab with automatic recovery"""
        starting_digit = self.get_starting_digit_for_tab(tab_index)
        
        # Generate 5 numbers
        numbers_list = []
        for _ in range(5):
            numbers_list.append(self.generate_indian_number(starting_digit))
        
        message = " ".join(numbers_list)
        
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Switch to tab
                self.driver.switch_to.window(self.tabs[tab_index])
                
                # Get or find message box
                msg_box = message_boxes[tab_index]
                if not msg_box:
                    msg_box = self.find_message_box_with_retry(tab_index, max_attempts=5)
                    if msg_box:
                        message_boxes[tab_index] = msg_box
                    else:
                        print(f"❌ Tab {tab_index+1}: No message box found (retry {retry+1}/{max_retries})")
                        time.sleep(2)
                        continue
                
                # Focus and clear
                msg_box.click()
                time.sleep(0.3)
                
                # Clear
                if msg_box.tag_name in ['input', 'textarea']:
                    msg_box.clear()
                else:
                    self.driver.execute_script("arguments[0].innerHTML = '';", msg_box)
                
                time.sleep(0.3)
                
                # Type
                for char in message:
                    msg_box.send_keys(char)
                    time.sleep(0.01)
                
                time.sleep(0.3)
                
                # Send
                msg_box.send_keys(Keys.RETURN)
                
                print(f"✅ Tab {tab_index+1}[{starting_digit}]: Sent {len(numbers_list)} numbers")
                return True, message_boxes
                
            except Exception as e:
                print(f"❌ Tab {tab_index+1}: Send error (retry {retry+1}/{max_retries}) - {e}")
                
                # Reset message box for this tab
                message_boxes[tab_index] = None
                time.sleep(2)
        
        print(f"❌ Tab {tab_index+1}: Failed after {max_retries} retries")
        return False, message_boxes
    
    def run_continuous_messaging(self):
        """Run continuous messaging from all tabs"""
        print("\n" + "="*70)
        print("🚀 STEP 4: STARTING CONTINUOUS MESSAGING")
        print("="*70)
        
        print("📊 Tab Distribution:")
        print("  • Tabs 1-3: Starting with digit 6")
        print("  • Tabs 4-6: Starting with digit 8")
        print("  • Tabs 7-10: Starting with digit 9")
        print("⏱️  Each tab sends 5 numbers every 2 seconds")
        print("🔄 Automatic recovery for failed tabs")
        print("⏸️  Press Ctrl+C to stop")
        print("="*70)
        
        # Initialize message boxes
        message_boxes = self.initialize_all_tabs_message_boxes()
        
        cycle_count = 0
        stats = {i: {"success": 0, "fail": 0} for i in range(10)}
        
        try:
            while True:
                cycle_count += 1
                print(f"\n🔄 CYCLE #{cycle_count}")
                
                # Process each tab
                for i in range(len(self.tabs)):
                    success, message_boxes = self.send_from_tab_with_recovery(i, message_boxes)
                    
                    if success:
                        stats[i]["success"] += 1
                    else:
                        stats[i]["fail"] += 1
                
                # Show statistics every 5 cycles
                if cycle_count % 5 == 0:
                    print(f"\n📊 STATISTICS after {cycle_count} cycles:")
                    total_success = sum(stats[i]["success"] for i in range(10))
                    total_fail = sum(stats[i]["fail"] for i in range(10))
                    total_attempts = total_success + total_fail
                    
                    if total_attempts > 0:
                        success_rate = (total_success / total_attempts) * 100
                        print(f"  Success rate: {success_rate:.1f}%")
                    
                    print(f"  Total unique numbers: {len(self.all_numbers)}")
                    
                    # Show per-tab stats
                    for i in range(10):
                        tab_total = stats[i]["success"] + stats[i]["fail"]
                        if tab_total > 0:
                            tab_rate = (stats[i]["success"] / tab_total) * 100
                            digit = self.get_starting_digit_for_tab(i)
                            print(f"  Tab {i+1}[{digit}]: {stats[i]['success']}/{tab_total} ({tab_rate:.1f}%)")
                
                # Wait before next cycle
                print(f"\n⏳ Waiting 2 seconds...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Stopped after {cycle_count} cycles")
        
        except Exception as e:
            print(f"\n❌ Error in messaging loop: {e}")
        
        finally:
            print("\n" + "="*70)
            print("📊 FINAL REPORT")
            print("="*70)
            print(f"Total cycles completed: {cycle_count}")
            print(f"Total unique numbers generated: {len(self.all_numbers)}")
            print(f"Browser remains open with all tabs")
            print("="*70)
    
    def run_bot(self):
        """Main bot execution flow"""
        print("\n" + "="*70)
        print("🤖 TELEGRAM MASTER BOT - SEQUENTIAL SETUP")
        print("="*70)
        
        # Setup Chrome
        if not self.setup_chrome():
            return
        
        try:
            # STEP 1: First tab complete setup
            if not self.wait_for_first_tab_login_and_setup():
                print("❌ First tab setup failed. Exiting.")
                return
            
            # STEP 2: Create additional tabs (only after first is ready)
            if not self.create_additional_tabs_only_after_first_ready():
                print("❌ Failed to create additional tabs")
                return
            
            # STEP 3: Run continuous messaging
            self.run_continuous_messaging()
            
        except Exception as e:
            print(f"\n❌ Bot execution error: {e}")
        
        finally:
            print("\n💡 Bot finished. All tabs remain open.")
            print("   Close browser manually when done.")

def main():
    print("\n" + "="*70)
    print("🤖 TELEGRAM SEQUENTIAL BOT")
    print("="*70)
    
    # Check ChromeDriver
    driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
    if not os.path.exists(driver_path):
        print(f"❌ ChromeDriver not found at: {driver_path}")
        return
    
    print("✅ ChromeDriver found")
    
    print("\n📋 SEQUENTIAL WORKFLOW:")
    print("1. ➡️  First tab opens")
    print("2. 🔑 You login manually in first tab")
    print("3. ✅ Bot verifies first tab is working")
    print("4. 📑 Only THEN other tabs are created")
    print("5. 🚀 All tabs start messaging together")
    
    print("\n⚠️ IMPORTANT:")
    print("• DO NOT close first tab")
    print("• Wait for 'FIRST TAB IS FULLY READY' message")
    print("• Other tabs will open automatically")
    
    print("\n🚀 Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Create and run bot
    bot = TelegramMasterBot()
    bot.run_bot()

if __name__ == "__main__":
    main()
