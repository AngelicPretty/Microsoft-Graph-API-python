# Copyright (c) littlefish Corporation.

import configparser
import asyncio
import os
import microsoft_graph_api

async def main():
	print('Python Graph App-Only Tutorial\n')

	# Load settings
	config = configparser.ConfigParser()
	config.read(['config.ini'])
	azure_settings = config['azure']

	choice = -1

	while choice != 0:
		os.system('cls' if os.name == 'nt' else 'clear')
		print("")
		print('Little Fish Microsoft-Graph-API Tools 1.0')
		print('Copyright (C) Little Fish. All rights reserved.')
		print("______________________________________________________________")
		print('')
		print('[1] Change User Password | Search by Email or Username')
		print('[2] List user chat group members')
		print('[3] Listening to the latest messages')
		print('[4] Access chatgpt in chat One by One | disable')
		print('[5] List user device bitlocker recoveryKeys| Search by Email or Username')
		print("")
		print("——————————————————————————————————————————————————————————————")
		print("")
		print('[9] Read Me')
		print("[0] Exit")
		print("")
		print("——————————————————————————————————————————————————————————————")
		print("")
		try:
			choice = int(input("Enter a menu option in the Keyboard [0,1,2,3,4,5,6,7,8,9]: "))
		except ValueError:
			choice = -1
		if choice == 0:
			print('[+] Goodbye...')
		elif choice == 1:
			await user_password_setting()
		elif choice == 2:
			await test(graph)
		elif choice == 3:
			await listen_messages()
		elif choice == 4:
			await user_profiles()
		elif choice == 5:
			await user_recoverykeys()
		else:
			print('Invalid choice!\n')

async def user_password_setting():
	os.system('cls' if os.name == 'nt' else 'clear')
	microsoft_graph_api.user_password_setting()
	print("[+] Press Enter key to continue")
	input()

async def listen_messages():
	os.system('cls' if os.name == 'nt' else 'clear')
	microsoft_graph_api.auto_send_messages()
	print("[+] Press Enter key to continue")
	input()

async def user_profiles():
	os.system('cls' if os.name == 'nt' else 'clear')
	microsoft_graph_api.user_profiles()
	print("[+] Press Enter key to continue")
	input()

async def user_recoverykeys():
	os.system('cls' if os.name == 'nt' else 'clear')
	microsoft_graph_api.user_recoverykeys()
	print("[+] Press Enter key to continue")
	input()

# Run main
asyncio.run(main())
