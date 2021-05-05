#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
import sys, traceback
sys.path.insert(0, '../')

import time
import sqlite3
import csv
from datetime import datetime
from telegram import Bot, Update, User, Message
from telegram.ext import CommandHandler, Updater, MessageHandler, CallbackContext, Filters
from telegram.utils.request import Request
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def tryUpdateChatRegistration(conn, tgid, chat_id, chat_name=None, active=None, last_update_time=0): #обновляет пользователя добавленного из чата
	cursor = conn.cursor()
	result = 0
	try:
		cursor.execute(""" update users_field set chat_name = ?, is_active = ?, last_update_time = ? where user_id = ? and chat_id = ?""", (chat_name, active, last_update_time, tgid, chat_id))
		conn.commit()
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'tryUpdateChatRegistration()'. Подробности в _.log")
		print('-' * 50)
		result = 1
	finally:
		pass	
	return result

def tryInsertChatRegistration(conn, tgid, chat_id, chat_name=None, active=None, last_update_time=0): #добавляет пользователя добавленного из чата
	cursor = conn.cursor()
	result = 0
	try:
		cursor.execute("""INSERT INTO users_field (user_id, chat_id, chat_name, is_active, last_update_time) VALUES (?, ?, ?, ?, ?)""", (tgid, chat_id, chat_name, active, last_update_time))
		conn.commit()
	except:
		# traceback.print_exc(limit=2, file=open('_.log', 'a'))
		# print("Произошла ошибка в блоке 'tryInsertChatRegistration()'. Подробности в _.log")
		# print('-' * 50)
		result = 1
	finally:
		pass	
	return result

def alterChatRegistration(tgid, chat_id, chat_name=None, active=None, last_update_time=0): #попытка добавления или обновления пользователя из чата
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	result = 0
	if tryInsertChatRegistration(conn, tgid, chat_id, chat_name, active, last_update_time) == 1:
		result = tryUpdateChatRegistration(conn, tgid, chat_id, chat_name, active, last_update_time)
		if result == 0:
			print("Обновлен пользователь с ID {} в чате:{} - {} \n".format(str(tgid), str(chat_id), str(chat_name)))
		else:
			print("Изменение пользователя с ID {} в чате:{} не удалось!\n".format(str(tgid), str(chat_id)))
	else:
		print("Добавлен пользователь с ID {} в чат:{} - {} \n".format(str(tgid), str(chat_id), str(chat_name)))
	conn.close()
	return result

def tryUpdateUserRegistration(conn, tgid, username=None, fname=None, lname=None, last_update_time=0):
	cursor = conn.cursor()
	result = 0
	try:
		cursor.execute(""" update users set username = ?, fname = ?, lname = ?, last_update_time = ? where id_tg = ?""", (username, fname, lname, last_update_time, tgid))
		conn.commit()
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'tryUpdateUserRegistration()'. Подробности в _.log")
		print('-' * 50)
		result = 1
	finally:
		pass	
	return result

def tryInsertUserRegistration(conn, tgid, username=None, fname=None, lname=None, role_id=None, last_update_time=0):
	cursor = conn.cursor()
	result = 0
	try:
		cursor.execute("""INSERT INTO users (id_tg, username, fname, lname, role_id, last_update_time) VALUES (?, ?, ?, ?, ?, ?)""", (tgid, username, fname, lname, role_id, last_update_time))
		conn.commit()
	except:
		# traceback.print_exc(limit=2, file=open('_.log', 'a'))
		# print("Произошла ошибка в блоке 'tryInsertUserRegistration()'. Подробности в _.log")
		# print('-' * 50)
		result = 1
	finally:
		pass	
	return result

def alterUserRegistration(tgid, username=None, fname=None, lname=None, role_id=None, last_update_time=0):
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	result = 0
	if tryInsertUserRegistration(conn, tgid, username, fname, lname, role_id, last_update_time) == 1:
		result = tryUpdateUserRegistration(conn, tgid, username, fname, lname, last_update_time)
		if result == 0:
			print("Обновлен пользователь с ID {} \n".format(str(tgid)))
		else:
			print("Изменение пользователя с ID {} не удалось!\n".format(str(tgid)))
	else:
		print("Добавлен пользователь с ID {} \n".format(str(tgid)))
	conn.close()
	return result

def tryInactivateUser(tgid):
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	
	try:
		cursor.execute("""select user_id from users_field where user_id = '%s' """ % tgid)
		res = cursor.fetchone()
		if res:
			cursor.execute("""UPDATE users_field SET is_active = ? WHERE user_id = ? """, ("N", tgid))
			conn.commit()
			print("Пользователь c ID: {} больше не активен\n".format(str(tgid)))
		else:
			print("Пользователь c ID: {} не найден\n".format(str(tgid)))
		
	except:
		conn.close()
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'tryInactivateUser()'. Подробности в _.log")
		print('-' * 50)
	finally:
		conn.close()

def csv_writer(data): #пишем в файл
	try:
		with open("import.csv", "w", newline='') as csv_file: # открываем файл на запись
			writer = csv.writer(csv_file, delimiter=';') # добавляем разделителб
			for line in data:
				writer.writerow(line)
		with open("import.csv", "w", newline='') as csv_file:
			writer = csv.writer(csv_file, delimiter=';')
			writer.writerow(['Идентификатор пользователя', 'Имя пользователя', 'Имя', 'Фамилия', 'Идентификатор чата', 'Название чата', 'Активен']) #добавляем заголовки
			writer.writerows(data)
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'csv_writer()'. Подробности в _.log")
		print('-' * 50)
	finally:
		pass

def getUsersOnGroups(cname): #получаем список групп по запросу
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	try:
		cursor.execute("""select u.id_tg, u.username, u.fname, u.lname, uf.chat_id, uf.chat_name, uf.is_active
							from users as u 
							left join users_field as uf 
							on uf.user_id = u.id_tg 
							where uf.chat_name like '%s' and uf.is_active = 'Y'""" % cname)
		res = cursor.fetchall()
		if res:
			csv_writer(data=res) #пишем csv
		else:
			print("getUsersOnGroups(): --> Что-то пошло не так")
	except:
		conn.close()
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'getUsersOnGroups()'. Подробности в _.log")
		print('-' * 50)
	finally:
		conn.close()

def getAllUsersOnGroups(): #получаем список всех групп
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	try:
		cursor.execute("""select u.id_tg, u.username, u.fname, u.lname, uf.chat_id, uf.chat_name, uf.is_active
							from users as u 
							left join users_field as uf 
							on uf.user_id = u.id_tg 
							where uf.is_active = 'Y'""")
		res = cursor.fetchall()
		if res:
			csv_writer(data=res)
		else:
			print("getUsersOnGroups(): --> Что-то пошло не так")
	except:
		conn.close()
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'getAllUsersOnGroups()'. Подробности в _.log")
		print('-' * 50)
	finally:
		conn.close()

def addUserOnTextMessage(tgid, chat_id, chat_name=None, username=None, fname=None, lname=None): #Добавляем пользователя если он написал сообщение в чат
	role_id = 0
	active = 'Y'
	last_update_time = int(time.time())
	alterUserRegistration(tgid, username, fname, lname, role_id, last_update_time)
	alterChatRegistration(tgid, chat_id, chat_name, active, last_update_time)

def addNewUserOnChatMember(update, context): #Добавляем пользователя если он вошел в чата
	# TODO Проверка на SQL INJECTION
	if update.message.new_chat_members is not None:
		for member in update.message.new_chat_members:
			addUserOnTextMessage(tgid=member.id, chat_id=update.message.chat.id, chat_name=update.message.chat.title, username=member.username, fname=member.first_name, lname=member.last_name)
	else:
		print("Что-то пошло не так!")

def delUserOnChatMember(update, context): # Деактивируем пользователя если он вышел из чата
	# TODO Проверка на SQL INJECTION
	tryInactivateUser(tgid=update.message.left_chat_member.id)

def is_admin(tgid): #проверяем пользователя на админа.
	# Подключаемся к базе данных.
	conn = sqlite3.connect("collector.db") # указываем файл базы данных или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	result = 0
	try:
		cursor.execute("""select u.role_id, uf.is_active from users as u left join users_field as uf on uf.user_id = u.id_tg where u.id_tg = '%s' limit 1""" % tgid)
		res = cursor.fetchone()
		if res:
			if res[0] == 1 and res[1] == 'Y':
				result = 1
			else:
				result = 2
		else:
			print("Is_admin: --> Пользователь c ID: {} не найден\n".format(str(tgid)))

	except:
		conn.close()
		result = 0
		# traceback.print_exc(limit=2, file=open('_.log', 'a'))
		# print("Произошла ошибка в блоке 'is_admin()'. Подробности в _.log")
		# print('-' * 50)
	finally:
		conn.close()
	return result

def keyboard_menu(): #Добавляем клавиатуру с основным меню
	conn = sqlite3.connect("collector.db")
	cursor = conn.cursor()
	cursor.execute("""SELECT distinct chat_name FROM users_field  where chat_name IS NOT NULL""")
	res = cursor.fetchall()
	if res:
		keyboard = []
		for rows in res:
			lst = map(lambda x: 'Участники: %s' % x, rows)
			keyboard.append(lst)
		keyboard.append(["Весь список"])
	return ReplyKeyboardMarkup(
		keyboard=keyboard,
		resize_keyboard=True
	)

def keyboard_remove(): # удаляем клавиатуру пользователю который не админ. На всякий случай
	return ReplyKeyboardRemove(
		remove_keyboard=True
	)

def start(update, context): # срабатывает на команду /start в телеграм чате
	try:
		if is_admin(tgid=update.message.from_user.id) == 1: #проверка на админа
			update.message.reply_text("Здравствуйте {}! Чтобы получить список участников, нажмите соответвующую кнопку на клавиатуре".format(str(update.message.from_user.first_name)), reply_markup=keyboard_menu())
		else: #если не админ то а-та-та
			update.message.reply_text("Извините! Я общаюсь только с админом.", reply_markup=keyboard_remove())
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'start()'. Подробности в _.log")
		print('-' * 50)
	finally:
		pass

def update(update, context): # обновляет бота по команде /update
	try:
		if is_admin(tgid=update.message.from_user.id) == 1: #проверка на админа
			update.message.reply_text("Отлично {}! Давайте приступим к работе.".format(str(update.message.from_user.first_name)), reply_markup=keyboard_menu())
		else: #если не админ то а-та-та
			update.message.reply_text("Извините! Я общаюсь только с админом.", reply_markup=keyboard_remove())
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'start()'. Подробности в _.log")
		print('-' * 50)
	finally:
		pass

def echoMessage(update, context): #TEST OK!
	# TODO Проверка на SQL INJECTION
	try:
		addUserOnTextMessage(tgid=update.message.from_user.id, chat_id=update.message.chat.id, chat_name=update.message.chat.title, username=update.message.from_user.username, fname=update.message.from_user.first_name, lname=update.message.from_user.last_name)
		print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
		print('Текст сообщения: ' + str(update.message.text))
		print('ID пользователя: ' + str(update.message.from_user.id))
		print('-' * 50)
		if is_admin(tgid=update.message.from_user.id) == 1: #проверка на админа
			text = update.message.text
			if text.find("Участники") != -1:
				getUsersOnGroups(cname=text[11:])
				update.message.reply_text("Секунду..")
				update.message.reply_document(document=open('import.csv', 'rb'), caption="Я подготовил для Вас список участников.")
			elif text == "Весь список":
				getAllUsersOnGroups()
				update.message.reply_text("Секундочку..")
				update.message.reply_document(document=open('import.csv', 'rb'), caption="Я подготовил для Вас список всех участников.")
		else: #если не админ то а-та-та
			print("Is_admin: --> Пользователь не имеет прав доступа для скачивания файлов с данными других пользователей")
			# update.message.reply_text(":)", reply_markup=keyboard_remove())
	except:
		traceback.print_exc(limit=2, file=open('_.log', 'a'))
		print("Произошла ошибка в блоке 'echoMessage()'. Подробности в _.log")
		print('-' * 50)
	finally:
		pass

def test(update, context):
	print(update)

def main():
	try:
		request = Request(
			connect_timeout=0.5,
			read_timeout=1.0
		)
		bot = Bot(
			request=request,
			token=config.token,
			base_url=config.proxy #Подготовка прокси на случай блокировки ТГ. в конфиге поменять ссылку на прокси сервер
		)
		updater = Updater(
			bot=bot,
			use_context=True
		)

		response = updater.bot.get_me()
		
		print('*' * 30)
		print('Start telegram: ' + response.username + '\nID: ' + str(response.id) + '')
		print('*' * 30)

		dispatcher = updater.dispatcher
		dispatcher.add_handler(CommandHandler("start", start))
		dispatcher.add_handler(CommandHandler("update", update))
		dispatcher.add_handler(MessageHandler(Filters.text, echoMessage))
		dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, addNewUserOnChatMember))
		dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, delUserOnChatMember))
		updater.start_polling()
		updater.idle()
		
		print('\nFinish telegram\n')

	except Exception as e:
		print(e)

if __name__ == '__main__':
	# alterChatRegistration(tgid=123, chat_id="'; select true; --", chat_name='test', active='Y', last_update_time=0)
	main()