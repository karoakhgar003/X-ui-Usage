from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from selenium import webdriver

def hello(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Hello! Opening webpage...")

    # Create a new Selenium WebDriver instance
    driver = webdriver.Firefox(executable_path='geckodriver.exe')

    # Open the desired webpage
    driver.get("https://google.com")

def main():
    updater = Updater(token="6639628878:AAFqR-an9Iif8iprVhGDHyLnCHUIxKbGM-s", use_context=True)
    dispatcher = updater.dispatcher

    # Register the hello() function as a handler for the "hello" command
    dispatcher.add_handler(CommandHandler("hello", hello))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
