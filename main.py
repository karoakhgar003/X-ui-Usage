import datetime
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from selenium import webdriver
import time
import re
import json

def hello(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Hello! Opening webpage...")

    # Create a new Selenium WebDriver instance

def get_usage(update,context,id,url,port,path,username,password):
    try:
        chat_id = update.message.chat_id
        # Create a new Firefox driver instance
        driver = webdriver.Firefox(executable_path='geckodriver.exe')

        # Open the desired webpage
        address = "http://" + url + ":" + port + path 
        print(address)
        driver.get(f"http://{url}:{port}{path}")

        # Find and fill in the username and password fields
        username_input = driver.find_element_by_xpath("//input[@placeholder='Username']")
        username_input.send_keys(username)
        password_input = driver.find_element_by_xpath("//input[@placeholder='Password']")
        password_input.send_keys(password)

        time.sleep(1)

        # Click on the sign-in button
        sign_in_button = driver.find_element_by_xpath("//button[@class='ant-btn ant-btn-primary']")
        sign_in_button.click()
        

        time.sleep(2)
        # Navigate to the desired page
        driver.get(f"http://{url}:{port}{path}panel/inbounds")

            
        time.sleep(2)
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
        usage_str = result[0]
        usage_list = usage_str.split("/")
        userusage = usage_list[0]
        total = usage_list[1]
        date = result[1].split("Date:")[1].split(" ")[1]
        date_seperated = date.split("-")
        x = datetime.datetime(int(date_seperated[0]), int(date_seperated[1]), int(date_seperated[2]))
        context.bot.send_message(chat_id=chat_id, text=f"User usage: {userusage}\nTotal: {total}\nExpire Time: {x.strftime('%c')}")
        # Close the browser
        driver.quit()
    except:
        get_usage(update,context,id,url)
        driver.quit()

def show_panels_command(update,context):
    f = open('servers.json')
    servers = json.load(f)
    for i in range(len(servers)):
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Domain: {servers[i]['domain']}\nIp address: {servers[i]['ip']}\nPort: {servers[i]['port']}\nPath: {servers[i]['path']}\nUsername: {servers[i]['username']}\nPassword: {servers[i]['password']}")

def add_panel_command(update,context):
    args = context.args
    if args:
        server_ip = args[0]
        server_domain = args[1]
        server_port = args[2]
        server_path = args[3]
        server_username = args[4]
        server_password = args[5]
        f = open('servers.json')
        servers = json.load(f)
        domains_list = []
        for i in range(len(servers)):
            domains_list.append(servers[i]['domain'])

        if server_domain not in domains_list:
            server = {
                'ip' : server_ip,
                'domain' : server_domain,
                'port' : server_port,
                'path' : server_path,
                'username' : server_username,
                'password' : server_password
            }
            servers.append(server)
            with open('servers.json', 'w') as file:
                file.write(json.dumps(servers) + '\n')
            context.bot.send_message(chat_id=update.effective_chat.id, text='panel added successfully')    
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='domain already exists')      

def remove_panel_command(update,context):
    args = context.args
    if args:
        server_ip = args[0]
        f = open('servers.json')
        servers = json.load(f)
        for i in range(len(servers)):
            if server_ip == servers[i]['ip']:
                servers.pop(i)
            break
        with open('servers.json', 'w') as file:
            file.write(json.dumps(servers)) 
        context.bot.send_message(chat_id=update.effective_chat.id, text="Server Deleted")     


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
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Wait 30 Seconds...")
                    get_usage(update,context,uid,servers[i]['ip'],servers[i]['port'],servers[i]['path'],servers[i]['username'],servers[i]['password'])
    else:
        response = "UID or domain not found in the string."
    
    


def main():
    updater = Updater(token="YOUR BOT TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Register the hello() function as a handler for the "hello" command
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("add_panel", add_panel_command))
    dispatcher.add_handler(CommandHandler("show_panels", show_panels_command))
    dispatcher.add_handler(CommandHandler("remove_panel", remove_panel_command))
    handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(handler)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
