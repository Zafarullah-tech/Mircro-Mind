from flask import Flask, request, render_template, jsonify
import openai
import pyautogui
import time
import pyperclip
import threading
import webbrowser

app = Flask(__name__)

# Initialize OpenAI (you should use environment variables for the API key in production)
openai.api_key = "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"

def get_ai_response(message, is_whatsapp=False):
    """Shared helper function to get AI responses"""
    system_message = None
    if is_whatsapp:
        system_message = {
            "role": "system", 
            "content": """you are real person name Awais sabir ,you know urdu , hindi amd english language . 
                        you are a student of BS artifical intelligence.you  is very good in python and he is very good in AI . 
                        you is also good friend and talk like a real person.you will talk on whatsapp and will talk as two real person . 
                        Do each other talk like a real person.use emojis in chat and use short sentences.never take name of Awais sabir in chat. 
                        Don;t write Hi,again and again. Always respond in one brief sentence. 
                        Analyze the chat history and reply appropriately while maintaining a decent and professional tone."""
        }
    
    messages = []
    if system_message:
        messages.append(system_message)
    messages.append({"role": "user", "content": message})
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message['content']

def start_whatsapp_bot(target_user):
    """WhatsApp bot function that runs in a separate thread"""
    try:
        # Open WhatsApp Web
        webbrowser.open('https://web.whatsapp.com')
        # Wait for WhatsApp to load
        time.sleep(20)  # Adjust this time based on your internet speed
        
        if not search_and_click_user(target_user):
            print("Could not find the specified user. Please check the name and try again.")
            return

        time.sleep(5)  # Wait for chat to load
        
        while True:
            # Move to the chat area and click
            time.sleep(2)
            pyautogui.moveTo(680, 780, duration=1)
            pyautogui.click()
            time.sleep(2)

            # First drag operation (horizontal)
            pyautogui.moveTo(720, 780, duration=2)
            time.sleep(1)

            # Second drag operation (to bottom-right)
            pyautogui.dragTo(1830, 900, duration=3)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)

            # Get the copied text
            copied_text = pyperclip.paste()
            print(f"Copied text: {copied_text}")

            # Check if the last message is from the target user
            if is_last_message_from_current_user(copied_text, target_user):
                print(f"Detected message from {target_user}.")
                # Create a chat completion request with updated prompt
                response = get_ai_response(copied_text, is_whatsapp=True)
                print(f"Response: {response}")
                pyperclip.copy(response)

                # Click to send the response
                pyautogui.click(986, 940)
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(8)
            else:
                print(f"No new messages detected from {target_user}.")
                time.sleep(8)
                
    except Exception as e:
        print(f"Error in WhatsApp bot: {e}")
        return

def is_last_message_from_current_user(chat_log, current_user= None):
    """Check if the last message is from the current user we're talking to"""
    messages = chat_log.strip().split("\n")
    if not messages:
        return False
        
    # If we don't have a current user, get the sender of the last message
    last_message = messages[-1]
   
    if current_user is None: #  it is  true because the current user and none has same memory location
        # Extract sender name from the last message (assuming format: "[time] sender_name: message")
        try:
            current_user = last_message.split(']')[1].split(':')[0].strip()
        except:
            return False
    
    return current_user in last_message


def search_and_click_user(user_name):
    """Search for a user on WhatsApp and click on their chat"""
    try:
        # Wait for WhatsApp to fully load and be interactive
        time.sleep(2)
        
        # Click on the search box (new chat button first)
        # pyautogui.moveTo(330, 100, duration=1)  # Click new chat button
        # pyautogui.click()
        # time.sleep(2)
        
        # Now click the search box
        pyautogui.moveTo(252, 226, duration=1)
        pyautogui.click()
        time.sleep(1)
        
        # Clear any existing text in search box
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(1)
        
        # Type the user name
        pyperclip.copy(user_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)  # Increased wait time for search results
        
        # Click on the first search result
        pyautogui.moveTo(275, 430, duration=1)
        pyautogui.click()
        time.sleep(2)
        
        return True
    except Exception as e:
        print(f"Error in search_and_click_user: {e}")
        return False

@app.route('/')
def splash():
    return render_template("splash.html")

@app.route('/landing')
def landing():
    return render_template("landing.html")

@app.route('/chat')
def chatbot():
    return render_template("chat.html")


@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        user_message = request.json.get('message')
        
        # Call OpenAI API
        ai_response = get_ai_response(user_message)
        return jsonify({"response": ai_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start_whatsapp', methods=['POST'])
def start_whatsapp():
    try:
        target_user = request.json.get('username')
        if not target_user:
            return jsonify({"error": "Username is required"}), 400
            
        # Start WhatsApp bot in a separate thread
        bot_thread = threading.Thread(target=start_whatsapp_bot, args=(target_user,))
        bot_thread.daemon = True
        bot_thread.start()
        
        return jsonify({"message": f"WhatsApp bot started for user: {target_user}"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)