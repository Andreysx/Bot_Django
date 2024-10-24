import os
from django.core.wsgi import get_wsgi_application
from telebot import TeleBot, types

# Установка переменной окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stsproject.settings')

# Загрузка настроек Django
from django import setup

setup()

# Теперь вы можете использовать модели и другие части Django
from goodsapp.models import Orders, Products

# Your Telegram bot token
TOKEN = '7902068127:AAFs6JQKHllInr0ebRzHEJtZ8gpDCs-ccvs'

bot = TeleBot(TOKEN)

# Словарь для хранения пользовательских данных
user_data = {}


# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_list_orders = types.KeyboardButton("📋 Список заказов")
    button_choose_order = types.KeyboardButton("🛒 Выбрать заказ")

    markup.add(button_list_orders, button_choose_order)

    bot.send_message(message.chat.id, 'Привет! Выберите команду:', reply_markup=markup)


# Функция для вывода всех заказов
@bot.message_handler(func=lambda message: message.text == "📋 Список заказов")
def list_orders_message(message):
    orders = Orders.objects.all()
    message_text = 'Список заказов:\n'

    if orders.exists():
        for order in orders:
            message_text += f"{order.name} - {order.date}\n"
    else:
        message_text = "Нет доступных заказов."

    bot.send_message(message.chat.id, message_text)


# Функция для обработки выбора конкретного заказа
@bot.message_handler(func=lambda message: message.text == "🛒 Выбрать заказ")
def choose_order_message(message):
    bot.send_message(message.chat.id, "Введите имя заказа для выбора:")
    user_data[message.chat.id] = {'waiting_for_order': True}


# Функция для обработки сообщения с именем заказа
@bot.message_handler(content_types=['text'], func=lambda message: message.text and not message.text.startswith('/'))
def handle_order_name(message):
    if message.chat.id in user_data and 'waiting_for_order' in user_data[message.chat.id]:
        # Попробуем найти заказ по имени
        orders = Orders.objects.filter(name=message.text)
        if orders.exists():
            order = orders.first()  # Получаем первый найденный заказ
            user_data[message.chat.id] = {'chosen_order_id': order.id}
            bot.send_message(message.chat.id, f"Выбран заказ: {order.name}")
            bot.send_message(message.chat.id, "Введите артикул продукта для поиска:")
        else:
            bot.send_message(message.chat.id, "Заказ не найден. Пожалуйста, попробуйте снова.")

        # Удаляем ключ 'waiting_for_order', если он существует
        user_data[message.chat.id].pop('waiting_for_order', None)
    else:
        # Обработка других текстовых сообщений (например, поиск артикула)
        if message.chat.id in user_data and 'chosen_order_id' in user_data[message.chat.id]:
            order_id = user_data[message.chat.id]['chosen_order_id']
            order = Orders.objects.get(pk=order_id)
            article = message.text
            products = Products.objects.filter(order=order, article=article)
            if products.exists():
                product = products.first()
                bot.send_message(message.chat.id,
                                 f"Продукт найден:\nАртикул: {product.article}\nНазвание: {product.name}\nКоличество: {product.quantity} штук\nЦена за единицу: {product.unit_price} RUB\nВес: {product.weight} кг\nСтоимость: {product.amount} RUB")
            else:
                bot.send_message(message.chat.id, "Продукт не найден.")
        else:
            bot.send_message(message.chat.id, "Сначала выберите заказ.")


# Функция для обработки инлайн кнопок (не используется в этом случае)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    pass  # Not needed in this scenario


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)