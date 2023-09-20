from datetime import datetime
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import re
import json


def is_admin(username):
    username = '@' + username
    f = open('admins.json')
    admins = json.load(f)
    if username in admins:
        return True
    else:
        return False
    
def start_command(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="سلام به ربات حجم Fallen VPN خوش آمدید\n لطفا کانفیگ خود را بفرستید")

def get_usage(update,context,id,url,port,path,username,password):
    try:
        chat_id = update.message.chat_id
        # Create a new Firefox driver instance
        # driver=webdriver.Chrome()
        options = Options()
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

        driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)

        # Open the desired webpage
        address = "http://" + url + ":" + port + path 
        driver.get(f"http://{url}:{port}{path}")
        time.sleep(3)

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
        expand_buttons = driver.find_elements_by_xpath("//div[@aria-label='Expand row']")

        for button in expand_buttons:
            button.click()

        # Execute JavaScript code to capture console logs
        script = """
        let logs = [];
        console.log = function(message) {{
            logs.push(message);
        }};
        b = document.querySelectorAll("tbody")
        for(let j = 1; j < b.length;j++){{
            a = b[j].children
            for (let i = 0; i < a.length; i++) {{
                    if (a[i].children[5].innerText == uid) {{
                        console.log("Usage: " + a[i].children[3].innerText);
                        console.log("Date: " + a[i].children[4].innerText);
                    }}
            }}        
        }}                     
        return logs;
        """

        uid = id
        formatted_script = script.replace('uid', '"'+ uid + '"')

        # Retrieve the console log output
        result = driver.execute_script(formatted_script)
        if len(result) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="کانفیگ مورد نظر یافت نشد!. لطفا با پشتیبانی تماس بگیرید")
        else:
            print("karo")
            usage_str = result[0]
            usage_list = usage_str.split("/")
            userusage = usage_list[0]
            if usage_list[1] != ' ':
                total = usage_list[1].split('GB')[0]
            else:
                total = float('inf')    
            if "-" in result[1]:
                date = result[1].split("Date:")[1].split(" ")[1]
                date_seperated = date.split("-")
                x = datetime(int(date_seperated[0]), int(date_seperated[1]), int(date_seperated[2]))
                today = datetime.now()
                delta = (x - today).days
                if 'MB' in userusage:
                    useruseage2 = float(userusage.split('MB')[0].split('Usage: ')[1])/1000
                elif 'GB' in userusage:
                    useruseage2 = float(userusage.split('GB')[0].split('Usage: ')[1])
                else:
                    useruseage2 = float(userusage.split('B')[0].split('Usage: ')[1])/1000000
                context.bot.send_message(chat_id=chat_id, text=f"مصرف شما : \n{ str(total)+' GB / ' + userusage.split('Usage: ')[1] }\nحجم باقیمانده : \n{str(float(total) - useruseage2) + ' GB' } \nروز های باقیمانده:\n {delta} روز")
            elif "day(s)" in result[1]:
                if 'MB' in userusage:
                    useruseage2 = float(userusage.split('MB')[0].split('Usage: ')[1])/1000
                elif 'GB' in userusage:
                    useruseage2 = float(userusage.split('GB')[0].split('Usage: ')[1])
                else:
                    useruseage2 = float(userusage.split('B')[0].split('Usage: ')[1])/1000000  
                context.bot.send_message(chat_id=chat_id, text=f"مصرف شما :\n{str(total) + ' GB'} / {userusage.split('Usage: ')[1]}\nحجم باقیمانده :\n {str(float(total) - useruseage2) } GB  \nروز های باقیمانده: \n{result[1].split('day(s)')[0]} روز")
            else:
                if 'MB' in userusage:
                    useruseage2 = float(userusage.split('MB')[0].split('Usage: ')[1])/1000
                elif 'GB' in userusage:
                    useruseage2 = float(userusage.split('GB')[0].split('Usage: ')[1])
                else:
                    useruseage2 = float(userusage.split('B')[0].split('Usage: ')[1])/1000000
                context.bot.send_message(chat_id=chat_id, text=f"مصرف شما :\n{str(total) + ' GB'} / {userusage.split('Usage: ')[1]}\nحجم باقیمانده : \n{str(float(total) - useruseage2) } GB  \nروز های باقیمانده: \n{'inf'} روز")

        # Close the browser
        driver.quit()
    except:
        driver.close()
        get_usage(update,context,id,url,port,path,username,password)

def show_panels_command(update,context):
    if is_admin(update.message.chat.username):
        f = open('servers.json')
        servers = json.load(f)
        for i in range(len(servers)):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Domain: {servers[i]['domain']}\nIp address: {servers[i]['ip']}\nPort: {servers[i]['port']}\nPath: {servers[i]['path']}\nUsername: {servers[i]['username']}\nPassword: {servers[i]['password']}")

def add_panel_command(update,context):
    if is_admin(update.message.chat.username):
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
    if is_admin(update.message.chat.username):
        args = context.args
        if args:
            server_ip = args[0]
            f = open('servers.json')
            servers = json.load(f)
            for i in range(len(servers)):
                if server_ip == servers[i]['ip']:
                    servers.pop(i)
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
            if servers[i]['domain'] == domain.lower():
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Wait 30 Seconds...")
                    context.bot.send_message(chat_id=update.effective_chat.id, text=uid)
                    get_usage(update,context,uid,servers[i]['ip'],servers[i]['port'],servers[i]['path'],servers[i]['username'],servers[i]['password'])
    else:
        response = "UID or domain not found in the string."

def extend_config(update,context,id,url,port,path,username,password,traffic,date):
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

    driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)

    # Open the desired webpage
    address = "http://" + url + ":" + port + path 
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
    expand_buttons = driver.find_elements_by_xpath("//div[@aria-label='Expand row']")

    for button in expand_buttons:
        button.click()

    script = """
    let logs = [];
        console.log = function(message) {
            logs.push(message);
        };
    b = document.querySelectorAll("tbody")
    for(let j = 1; j < b.length;j++){
        a = b[j].children
        for (let i = 0; i < a.length; i++) {
                if (a[i].children[5].innerText == uid ) {
                    a[i].children[0].children[1].click()
                }
        }     
    }
    c = document.querySelectorAll(".ant-form-item")
    setTimeout(() => {
        traffic = c[6].children[1].children[0].children[0].children[0].children[1].children[0]
        reset_button = c[6].children[1].children[0].children[0].children[4]
        traffic.value = budapest
        reset_button.click()
    }, 500);
    setTimeout(() => {
        confirm_button = document.querySelectorAll(".ant-btn-primary")[3]
        confirm_button.click()
    }, 500);
    setTimeout(() => {
        switch1 = document.querySelectorAll(".ant-switch")
        switch1 = switch1[switch1.length - 1]
        switch1.click()
    },500);

    setTimeout(() => {
        expire_input = a[8].children[1].children[0].children[0].children[0].children[1].children[0]
        expire_input.value = rwanda
        confirm_button = document.querySelectorAll(".ant-btn-primary")[2]
        confirm_button.click()
    },500);
    return logs;    
    """
    uid = id
    print(uid)
    formatted_script = script.replace('uid', '"'+ uid + '"')
    formatted_script = formatted_script.replace('budapest', traffic)
    formatted_script = formatted_script.replace('rwanda', date)
    print(formatted_script)
    driver.execute_script(formatted_script)
    


def extention_command(update,context):
    args = context.args
    if args:
        config = args[0]
        traffic = args[1]
        time = args[2]
        string = config
        uid_match = re.search(r'//([^@]+)@', string)
        domain_match = re.search(r'@(.+):', string)
        if uid_match and domain_match:
            uid = uid_match.group(1)
            domain = domain_match.group(1)
            f = open('servers.json')
            servers = json.load(f)
            for i in range(len(servers)):
                if servers[i]['domain'] == domain.lower():
                    extend_config(update,context,uid,servers[i]['ip'],servers[i]['port'],servers[i]['path'],servers[i]['username'],servers[i]['password'],traffic,time)

def main():
    updater = Updater(token="6658677040:AAHG3sU6ICkzzp1sCh7qg2KKfiI66LMjp7M", use_context=True)
    dispatcher = updater.dispatcher

    # Register the hello() function as a handler for the "hello" command
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("add_panel", add_panel_command))
    dispatcher.add_handler(CommandHandler("show_panels", show_panels_command))
    dispatcher.add_handler(CommandHandler("remove_panel", remove_panel_command))
    dispatcher.add_handler(CommandHandler("extend", extention_command))
    handler = MessageHandler(Filters.text & ~Filters.command, handle_message, run_async=True)
    dispatcher.add_handler(handler)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
