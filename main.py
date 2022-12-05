# My imports
from Constants import TOKEN as keys

# Other imports
import logging
import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ContextTypes, Application, ConversationHandler, MessageHandler, CommandHandler, filters)

# Enabling logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States of conversation handler
SELECTING_ACTION = 1
ADDING_DESCRIPTION = 2
ADDING_VALUE = 3
ADDING_DATE = 4

# Handling json requests
HEADERS = {'Accept': 'application/json'}


# Starts the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Adicionar gasto", "Ver gastos"], ["/sair"]]

    await update.message.reply_text(
        f"Olá, {update.message.from_user.first_name}, sou o robô que vai te auxiliar no controle financeiro!\n\nEscolha uma opção ou envie /sair para encerrar nossa conversa\n\nO que você quer fazer?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Selecione uma ação"
        )
    )

    return SELECTING_ACTION

async def action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Storing chosen option
    option = update.message.text

    if option == "Adicionar gasto":
        await update.message.reply_text(
            f"Você escolheu a opção '{option}...'\n\nPara começar, digite uma descrição:"
        )

        return ADDING_DESCRIPTION

    elif option == "Ver gastos":
        # Get data from DB
        expenses = requests.get("http://localhost/expenses", headers=HEADERS)

        # If there's anything in DB
        if (len(expenses.json()) > 0):
            text = ""
            for expense in expenses.json():
                text += f"{expense['date']} -- {expense['description']} -- R${expense['value']}\n"

            await update.message.reply_text(
                f"Você escolheu a opção '{option}'... Aqui estão:\n\n{text}\n/start para voltar"
            )
        else:
            await update.message.reply_text(
                f"Você escolheu a opção '{option}', mas não há registros no banco de dados.\n\n/start para voltar"
            )

    return ConversationHandler.END

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Storing data in telegram local storage before sending to DB
    context.user_data["DESCRIPTION"] = update.message.text

    await update.message.reply_text(
        f"Descrição registrada...\n\nAgora digite um valor:"
    )

    return ADDING_VALUE

async def value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Storing data in telegram local storage before sending to DB
    context.user_data["VALUE"] = update.message.text

    await update.message.reply_text(
        f"Valor registrado...\n\nAgora digite uma data:"
    )

    return ADDING_DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Storing data in telegram local storage before sending to DB
    context.user_data["DATE"] = update.message.text

    url = 'http://localhost/register'

    inserting_obj = {
        "description": context.user_data["DESCRIPTION"],
	    "value": context.user_data["VALUE"],
	    "date": context.user_data["DATE"]
    }

    # Sending to DB
    db_response = requests.post(url, json=inserting_obj)

    await update.message.reply_text(
        f"Ok! Salvando informações no banco de dados...\n\n/start para voltar"
    )

    return ConversationHandler.END

async def quit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    await update.message.reply_text(
        f"Até mais, {user.first_name}!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    # Starting application
    application = Application.builder().token(keys).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, action)],
            ADDING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            ADDING_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, value)],
            ADDING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
        },
        fallbacks=[CommandHandler("sair", quit)],
    )

    application.add_handler(conv_handler)
    
    application.run_polling()

if __name__ == '__main__':
    main()