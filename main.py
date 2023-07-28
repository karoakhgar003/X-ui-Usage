from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from selenium import webdriver
import time
import re
import json

def hello(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Hello! Opening webpage...")

    # Create a new Selenium WebDriver instance
    

def get_usage(update,context,id,url):
    chat_id = update.message.chat_id
    # Create a new Firefox driver instance
    driver = webdriver.Firefox(executable_path='geckodriver.exe')

    # Open the desired webpage
    driver.get(f"http://{url}:2549")

    # Find and fill in the username and password fields
    username_input = driver.find_element_by_xpath("//input[@placeholder='Username']")
    username_input.send_keys("karo")
    password_input = driver.find_element_by_xpath("//input[@placeholder='Password']")
    password_input.send_keys("138292Kk")

    time.sleep(2)

    # Click on the sign-in button
    sign_in_button = driver.find_element_by_xpath("//button[@class='ant-btn ant-btn-primary']")
    sign_in_button.click()

    time.sleep(2)

    # Navigate to the desired page
    driver.get(f"http://{url}:2549/panel/inbounds")

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

    uid = id
    formatted_script = script.format(uid)

    # Retrieve the console log output
    result = driver.execute_script(formatted_script)
    context.bot.send_message(chat_id=chat_id, text=result)
    # Close the browser
    driver.quit()

def add_panel_command(update,context):
    args = context.args
    if args:
        server_ip = args[0]
        server_domain = args[1]
        f = open('servers.json')
        servers = json.load(f)
        domains_list = []
        for i in range(len(servers)):
            domains_list.append(servers[i]['domain'])

        if server_domain not in domains_list:
            server = {
                'ip' : server_ip,
                'domain' : server_domain,
            }
            servers.append(server)
            with open('servers.json', 'w') as file:
                file.write(json.dumps(servers) + '\n')
            context.bot.send_message(chat_id=update.effective_chat.id, text='panel added successfully')    
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='domain already exists')      


def handle_message(update, context):
    string = update.message.text
    
    uid_match = re.search(r'//([^@]+)@', string)
    domain_match = re.search(r'@(.+):', string)

    if uid_match and domain_match:
        uid = uid_match.group(1)
        domain = domain_match.group(1)
        
        response = f"uid: {uid}\ndomain: {domain}"
        f = open('servers.json')
        servers = json.load(f)
        for i in range(len(servers)):
            if servers[i]['domain'] == domain:
                get_usage(update,context,uid,servers[i]['ip'])
    else:
        response = "UID or domain not found in the string."
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def main():
    updater = Updater(token="6639628878:AAFqR-an9Iif8iprVhGDHyLnCHUIxKbGM-s", use_context=True)
    dispatcher = updater.dispatcher

    # Register the hello() function as a handler for the "hello" command
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("add_panel", add_panel_command))
    handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(handler)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
