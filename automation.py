import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import os

class TelegramUltimateBot:
    def __init__(self):
        self.driver = None
        self.numbers_set = set()
    
    def setup(self):
        """Setup browser"""
        driver_path = r'C:\Users\rosha\Downloads\chrome_automation\chromedriver.exe'
        service = Service(driver_path)
        
        # Minimal options
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(service=service, options=options)
        return True
    
    def inject_telegram_helper(self):
        """Inject JavaScript to help find Telegram elements"""
        js_code = """
        // Create global helper object
        window.telegramHelper = {
            findMessageBox: function() {
                // Method 1: Contenteditable
                let editables = document.querySelectorAll("[contenteditable='true']");
                for(let elem of editables) {
                    let rect = elem.getBoundingClientRect();
                    if(rect.width > 200 && rect.height > 20) {
                        return elem;
                    }
                }
                
                // Method 2: Specific classes
                let classes = ['input-message-input', 'composer_rich_textarea', 'im_editable'];
                for(let className of classes) {
                    let elems = document.getElementsByClassName(className);
                    if(elems.length > 0) return elems[0];
                }
                
                // Method 3: Look in footer
                let footers = document.querySelectorAll('.chat-footer, .im_send_form');
                for(let footer of footers) {
                    let inputs = footer.querySelectorAll('input, textarea, [contenteditable]');
                    if(inputs.length > 0) return inputs[0];
                }
                
                return null;
            },
            
            clickAndFocus: function(element) {
                element.click();
                element.focus();
            }
        };
        
        console.log("Telegram Helper injected");
        return true;
        """
        
        self.driver.execute_script(js_code)
        return True
    
    def find_message_box_js(self):
        """Use JavaScript to find message box"""
        print("🔍 Using JavaScript to find message box...")
        
        # Inject helper if not already injected
        try:
            self.driver.execute_script("return window.telegramHelper;")
        except:
            self.inject_telegram_helper()
        
        # Find using JavaScript
        result = self.driver.execute_script("""
            try {
                let box = window.telegramHelper.findMessageBox();
                if(box) {
                    window.telegramHelper.clickAndFocus(box);
                    return box;
                }
                return null;
            } catch(e) {
                console.error("Error:", e);
                return null;
            }
        """)
        
        if result:
            print("✅ Found using JavaScript")
            return result
        else:
            print("❌ JavaScript method failed")
            return None
    
    def brute_force_find(self):
        """Brute force method to find input"""
        print("🔍 Brute force search for input...")
        
        # Try clicking at different positions
        for y in [600, 650, 700, 750]:  # Different Y positions
            for x in [300, 400, 500, 600]:  # Different X positions
                try:
                    self.driver.execute_script(f"""
                        var elem = document.elementFromPoint({x}, {y});
                        if(elem) {{
                            elem.click();
                            elem.focus();
                        }}
                    """)
                    time.sleep(0.5)
                    
                    # Check if we found an input
                    try:
                        active = self.driver.switch_to.active_element
                        tag = active.tag_name.lower()
                        if tag in ['input', 'textarea'] or active.get_attribute('contenteditable') == 'true':
                            print(f"✅ Found at position ({x}, {y})")
                            return active
                    except:
                        pass
                except:
                    pass
        
        return None
    
    def run_bot(self):
        """Main bot"""
        print("🤖 Ultimate Telegram Bot")
        print("="*50)
        
        if not self.setup():
            return
        
        try:
            # Step 1: Open Telegram
            print("🌐 Opening Telegram...")
            self.driver.get("https://web.telegram.org/a/")
            
            print("\n📱 MANUAL LOGIN REQUIRED")
            print("Login with QR code within 60 seconds")
            print("="*40)
            
            for i in range(60):
                time.sleep(1)
                if (i+1) % 10 == 0:
                    print(f"{60-(i+1)} seconds remaining...")
            
            print("\n✅ Assuming login complete")
            
            # Step 2: Open target chat
            print("💬 Opening target chat...")
            self.driver.get("https://web.telegram.org/a/?account=2#8549408740")
            time.sleep(5)
            
            # Step 3: Find message box
            message_box = self.find_message_box_js()
            
            if not message_box:
                message_box = self.brute_force_find()
            
            if not message_box:
                print("❌ Could not find message box")
                self.driver.save_screenshot('error.png')
                return
            
            print("🎯 Ready to send messages!")
            
            # Generate and send numbers
            count = 0
            try:
                while True:
                    count += 1
                    print(f"\n📦 Message #{count}")
                    
                    # Generate 5 numbers
                    numbers = []
                    for _ in range(5):
                        num = '6' + ''.join(str(random.randint(0, 9)) for _ in range(9))
                        numbers.append(num)
                    
                    message = " ".join(numbers)
                    print(f"📝: {message}")
                    
                    # Send
                    try:
                        # Clear
                        if message_box.tag_name in ['input', 'textarea']:
                            message_box.clear()
                        else:
                            self.driver.execute_script("arguments[0].innerHTML = '';", message_box)
                        
                        time.sleep(0.3)
                        
                        # Type
                        for char in message:
                            message_box.send_keys(char)
                            time.sleep(0.01)
                        
                        time.sleep(0.3)
                        
                        # Send
                        message_box.send_keys(Keys.RETURN)
                        
                        print("✅ Sent")
                        
                    except Exception as e:
                        print(f"❌ Send error: {e}")
                        # Try to find again
                        message_box = self.find_message_box_js()
                    
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print("\n⏹️ Stopped")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            print("\n🤖 Bot finished")
            print("Close browser manually")

# Run simple bot
if __name__ == "__main__":
    bot = TelegramUltimateBot()
    bot.run_bot()
