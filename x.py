import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

class PersistentTelegramBot:
    def __init__(self):
        self.driver = None
        self.tabs = []
        self.all_numbers = set()
        
    def setup_with_persistent_session(self):
        """Setup Chrome with persistent session"""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # CRITICAL: Use persistent profile
        profile_path = os.path.join(os.getcwd(), "telegram_profile")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Browser with persistent session started")
            print(f"📁 Profile saved at: {profile_path}")
            return True
        except Exception as e:
            print(f"❌ Browser error: {e}")
            return False
    
    def single_login_setup(self):
        """One-time manual login setup"""
        print("\n" + "="*60)
        print("🔑 ONE-TIME MANUAL LOGIN SETUP")
        print("="*60)
        
        # Open Telegram
        self.driver.get("https://web.telegram.org/a/")
        print("✅ Telegram opened")
        
        # Store first tab
        self.tabs.append(self.driver.current_window_handle)
        
        print("\n📱 Please login now using QR code")
        print("The browser will remember your login forever")
        print("⏳ Waiting for login completion...")
        print("="*60)
        
        # Wait indefinitely for login
        login_detected = False
        while not login_detected:
            try:
                # Check multiple indicators
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Indicators of successful login
                indicators = [
                    "#" in current_url,  # Has hash (chat ID)
                    "chat" in page_source,
                    "dialog" in page_source,
                    "message" in page_source and "input" in page_source
                ]
                
                if any(indicators):
                    login_detected = True
                    print("✅ Login detected!")
                    break
                
                # Also try to find chat elements
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true'], .chat, .dialog")
                    if elements:
                        login_detected = True
                        print("✅ Chat interface detected!")
                        break
                except:
                    pass
                
                print("⏳ Still waiting for login... (Login and wait)")
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Check error: {e}")
                time.sleep(5)
        
        print("\n✅ Login successful! Session saved.")
        print("This session will be used for all tabs.")
        
        return True
    
    def create_messaging_tabs(self):
        """Create tabs for messaging"""
        print("\n📑 Creating messaging tabs...")
        
        # First, navigate first tab to target chat
        target_url = "https://web.telegram.org/a/?account=2#8549408740"
        self.driver.get(target_url)
        time.sleep(3)
        print("✅ Tab 1: Target chat loaded")
        
        # Create 9 more tabs
        for i in range(9):
            try:
                # Open new tab
                self.driver.execute_script("window.open('');")
                
                # Get new tab handle
                all_handles = self.driver.window_handles
                new_tab = all_handles[-1]
                
                # Switch to new tab
                self.driver.switch_to.window(new_tab)
                
                # Open target chat directly (session is shared)
                self.driver.get(target_url)
                
                # Store tab
                self.tabs.append(new_tab)
                
                # Wait for load
                time.sleep(2)
                
                print(f"✅ Tab {i+2}/10: Created and loaded")
                
            except Exception as e:
                print(f"❌ Tab {i+2} error: {e}")
        
        print(f"\n🎯 Total tabs ready: {len(self.tabs)}")
        
        # Switch back to first tab
        self.driver.switch_to.window(self.tabs[0])
        return True
    
    def smart_message_box_finder(self, tab_index):
        """Smart message box finder with multiple strategies"""
        strategies = [
            self._find_by_direct_click,
            self._find_by_element_search,
            self._find_by_javascript_injection,
            self._find_by_coordinate_scan
        ]
        
        for strategy in strategies:
            result = strategy(tab_index)
            if result:
                return result
        
        return None
    
    def _find_by_direct_click(self, tab_index):
        """Strategy 1: Direct element search"""
        try:
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Look for contenteditable
            elements = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
            for elem in elements:
                if elem.is_displayed():
                    return elem
            
            # Look for input/textarea
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            for elem in inputs + textareas:
                if elem.is_displayed():
                    return elem
            
        except:
            pass
        return None
    
    def _find_by_javascript_injection(self, tab_index):
        """Strategy 2: JavaScript injection"""
        try:
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Inject helper script
            js_code = """
            function findMessageBox() {
                // Try contenteditable
                let editables = document.querySelectorAll("[contenteditable='true']");
                for(let el of editables) {
                    let rect = el.getBoundingClientRect();
                    if(rect.width > 100 && el.offsetParent !== null) {
                        el.click();
                        el.focus();
                        return el;
                    }
                }
                
                // Try input/textarea
                let inputs = document.querySelectorAll("input, textarea");
                for(let el of inputs) {
                    let rect = el.getBoundingClientRect();
                    if(rect.width > 100 && el.offsetParent !== null) {
                        el.click();
                        el.focus();
                        return el;
                    }
                }
                
                // Click at bottom center
                let x = window.innerWidth / 2;
                let y = window.innerHeight - 50;
                let el = document.elementFromPoint(x, y);
                if(el) {
                    el.click();
                    el.focus();
                    return el;
                }
                
                return null;
            }
            
            return findMessageBox();
            """
            
            element = self.driver.execute_script(js_code)
            return element
            
        except:
            return None
    
    def _find_by_coordinate_scan(self, tab_index):
        """Strategy 3: Coordinate scanning"""
        try:
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Scan different Y positions
            for y in range(500, 800, 50):
                x = self.driver.execute_script("return window.innerWidth") // 2
                
                self.driver.execute_script(f"""
                    var el = document.elementFromPoint({x}, {y});
                    if(el) {{
                        el.click();
                        el.focus();
                    }}
                """)
                
                time.sleep(0.5)
                
                # Check if we got focus
                try:
                    active = self.driver.switch_to.active_element
                    if active:
                        return active
                except:
                    pass
            
        except:
            pass
        return None
    
    def _find_by_element_search(self, tab_index):
        """Strategy 4: Deep element search"""
        try:
            self.driver.switch_to.window(self.tabs[tab_index])
            
            # Try different selectors
            selectors = [
                "[contenteditable='true']",
                "input[type='text']",
                "textarea",
                ".composer_rich_textarea",
                ".input-message-input",
                "[role='textbox']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            time.sleep(0.5)
                            return elem
                except:
                    continue
            
        except:
            pass
        return None
    
    def generate_and_send(self, tab_index):
        """Generate numbers and send from tab"""
        # Determine starting digit
        if tab_index < 3:
            digit = 6
        elif tab_index < 6:
            digit = 8
        else:
            digit = 9
        
        # Generate 5 unique numbers
        numbers = []
        for _ in range(5):
            while True:
                num = str(digit)
                for _ in range(9):
                    num += str(random.randint(0, 9))
                
                if num not in self.all_numbers:
                    self.all_numbers.add(num)
                    numbers.append(num)
                    break
        
        message = " ".join(numbers)
        
        # Find message box
        message_box = self.smart_message_box_finder(tab_index)
        if not message_box:
            print(f"❌ Tab {tab_index+1}: No message box found")
            return False
        
        try:
            # Send message
            message_box.click()
            time.sleep(0.2)
            
            # Clear
            if message_box.tag_name in ['input', 'textarea']:
                message_box.clear()
            else:
                self.driver.execute_script("arguments[0].innerHTML = '';", message_box)
            
            time.sleep(0.2)
            
            # Type
            for char in message:
                message_box.send_keys(char)
                time.sleep(0.005)
            
            time.sleep(0.2)
            
            # Send
            message_box.send_keys(Keys.RETURN)
            
            print(f"✅ Tab {tab_index+1}[{digit}]: Sent {len(numbers)} numbers")
            return True
            
        except Exception as e:
            print(f"❌ Tab {tab_index+1}: Send error - {e}")
            return False
    
    def run_continuous_messaging(self):
        """Continuous messaging loop"""
        print("\n" + "="*70)
        print("🚀 CONTINUOUS MESSAGING STARTED")
        print("="*70)
        
        cycle = 0
        stats = {i: {"success": 0, "fail": 0} for i in range(10)}
        
        try:
            while True:
                cycle += 1
                print(f"\n🔄 CYCLE {cycle}")
                
                # Process each tab
                for i in range(len(self.tabs)):
                    try:
                        if self.generate_and_send(i):
                            stats[i]["success"] += 1
                        else:
                            stats[i]["fail"] += 1
                    except Exception as e:
                        print(f"❌ Tab {i+1}: Fatal error - {e}")
                        stats[i]["fail"] += 1
                
                # Show stats every 5 cycles
                if cycle % 5 == 0:
                    print(f"\n📊 STATS after {cycle} cycles:")
                    for i in range(10):
                        total = stats[i]["success"] + stats[i]["fail"]
                        if total > 0:
                            rate = (stats[i]["success"] / total) * 100
                            print(f"  Tab {i+1}: {stats[i]['success']}/{total} ({rate:.1f}%)")
                    print(f"  Total numbers: {len(self.all_numbers)}")
                
                # Wait before next cycle
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ Stopped after {cycle} cycles")
        
        print(f"\n📊 Final: {len(self.all_numbers)} unique numbers sent")
        print("💡 Browser stays open with your session saved!")

def main():
    print("\n" + "="*70)
    print("🤖 PERSISTENT TELEGRAM BOT - LOGIN ONCE, USE FOREVER")
    print("="*70)
    
    bot = PersistentTelegramBot()
    
    # Setup with persistent session
    if not bot.setup_with_persistent_session():
        return
    
    # One-time manual login
    bot.single_login_setup()
    
    # Create messaging tabs
    bot.create_messaging_tabs()
    
    # Start continuous messaging
    bot.run_continuous_messaging()
    
    print("\n" + "="*70)
    print("✅ Session saved! Next time, you won't need to login.")
    print("="*70)

if __name__ == "__main__":
    main()
