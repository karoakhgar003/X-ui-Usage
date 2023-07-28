from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from selenium import webdriver
import time

def hello(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Hello! Opening webpage...")

    # Create a new Selenium WebDriver instance
    get_usage(update,context)

def get_usage(update,context):
    chat_id = update.message.chat_id
    # Create a new Firefox driver instance
    driver = webdriver.Firefox(executable_path='geckodriver.exe')

    # Open the desired webpage
    driver.get("URL")

    # Find and fill in the username and password fields
    username_input = driver.find_element_by_xpath("//input[@placeholder='Username']")
    username_input.send_keys("USERNAME")
    password_input = driver.find_element_by_xpath("//input[@placeholder='Password']")
    password_input.send_keys("PASSWORD")

    time.sleep(2)

    # Click on the sign-in button
    sign_in_button = driver.find_element_by_xpath("//button[@class='ant-btn ant-btn-primary']")
    sign_in_button.click()

    time.sleep(2)

    # Navigate to the desired page
    driver.get("URL")

    time.sleep(4)

    # Click on the expand row button
    expand_button = driver.find_element_by_xpath("//div[@aria-label='Expand row']")
    expand_button.click()

    # Execute JavaScript code to capture console logs
    script = """
    let logs = [];
    console.log = function(message) {{
        logs.push(message);
    }};
    a = document.querySelectorAll("tbody")[1].children;
    uid = '{}';
    for (let i = 0; i < a.length; i++) {{
        if (a[i].children[5].innerText == uid) {{
            console.log("Usage: " + a[i].children[3].innerText);
            console.log("Date: " + a[i].children[4].innerText);
        }}
    }}
    return logs;
    """

    uid = '9ec1f9c0-20c2-4ca8-df33-0ca1fca92892'
    formatted_script = script.format(uid)
    print(formatted_script)

    # Retrieve the console log output
    result = driver.execute_script(formatted_script)
    # Close the browser
    context.bot.send_message(chat_id=chat_id, text=result)
    driver.quit()



def main():
    updater = Updater(token="YOUR BOT TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Register the hello() function as a handler for the "hello" command
    dispatcher.add_handler(CommandHandler("hello", hello))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
