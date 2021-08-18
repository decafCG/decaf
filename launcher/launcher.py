import multiprocessing 
import sys
import os
import time
import signal
import sys
import subprocess
import time
from datetime import datetime
from scapy.all import *
import json
from collections import OrderedDict 
from bot import *
from filemover import *


args = sys.argv[1:]
argc = len(args)

FIVESECONDS = 5.00
TENSECONDS = 10.00
SEVENSECONDS = 7.00
MINSECONDS = 60

image_name_list = ["dump", "ffmpeg", "nping", "bot", "chrom"]
platform_list = ["stadia", "gfn", "luna"]

def kill_all_processes(proc):
	
	cli_cmd = "TASKLIST"
	process = subprocess.Popen(cli_cmd.split(), stdout=subprocess.PIPE)
	output, error = process.communicate() 
	process.wait()
	
	output = output.decode("utf-8").split("K\r\n")

	pid_l = []
	for line in output:
		line = line.split()

		if len(line) > 1:

			if proc == "all":
				for image in image_name_list:
					if line[0].find(image) >= 0:
						pid_l.append(line[1])
						print(line)
						break
			else:
				if line[0].find(proc) >= 0:
					pid_l.append(line[1])
					print(line)

	for pid in pid_l:
		cli_cmd = "taskkill /F /PID "+pid
		os.system(cli_cmd)

	# JUST IN CASE THE BOT IS KILLED WHILE RUNNING
	bot_clear_inputs()

def signal_handler(sig, frame):
	print('You pressed Ctrl+C! MPP Exit.')
	kill_all_processes("all")

	# Remove Files
	clear_directory("chromedata")
	clear_directory("tempdata")


	sys.exit(0)


def packet_trace_collector(folder_path, tshark_path, interface):
	global endTime
	
	cwd = os.getcwd()
	os.chdir(tshark_path)
	
	ts = str(time.time())
	dump_path = folder_path+"dump.pcapng"
	
	if interface == "wifi":
		cli_cmd = ".\\tshark.exe -i Wi-Fi -w "+dump_path
	else:
		cli_cmd = ".\\tshark.exe -w "+dump_path

	
	os.system(cli_cmd)

	os.chdir(cwd)



def screen_recorder(folder_path, cmd_path):

	cli_cmd = open(cmd_path, 'r').read().split("\n")[0]
	ts = str(time.time())
	cli_cmd += " "+folder_path+"video_"+ts+".mkv"
	print(cli_cmd)
	os.system(cli_cmd)



def get_streaming_server_ip(folder_path, tshark_path, interface):

	cwd = os.getcwd()
	os.chdir(tshark_path)
	ts = str(time.time())

	dump_path = folder_path+"dump_for_ip.pcapng"
	
	if interface == "wifi":
		cli_cmd = ".\\tshark.exe -c 1000 -i Wi-Fi -w "+dump_path
	else:
		cli_cmd = ".\\tshark.exe -c 1000 -i Ethernet -w "+dump_path


	os.system(cli_cmd)
	os.chdir(cwd)

	print("Processing for IP: ", cwd)
	
	packets = rdpcap(dump_path)
	stadia_ip_d = {}

	try:
		for packet in packets:
			# print(packet[IP].src, " > ", packet[IP].dst)
			ip = ""
			if packet[IP].src.find("192") > -1:
				ip = packet[IP].dst
			elif packet[IP].dst.find("192") > -1:
				ip = packet[IP].src
			
			if ip in stadia_ip_d.keys():
				stadia_ip_d[ip] += 1
			else:
				stadia_ip_d[ip] = 1
	except Exception as e:
		pass

	print("IP dictionary: ", stadia_ip_d)

	ping_ip = ""
	count = 0
	keys = list(stadia_ip_d.keys())
	for k in keys:
		if stadia_ip_d[k] > count and k[:4].find("192") == -1:
			count = stadia_ip_d[k]
			ping_ip = k

	print(ping_ip)

	return ping_ip


game_list = ["fc5", "acv", "crew", "crew2"]
def game_bot(game, bot_runtime_min, platform):

	if game == "fc5":
		bot_farcry5_loop_movement(bot_runtime_min, platform)
	elif game == "acv":
		bot_acv_loop_movement(bot_runtime_min, platform)
	elif game in ["crew", "crew2"]:
		bot_crew_loop_movement(bot_runtime_min, platform)

	bot_clear_inputs()



if __name__ == "__main__": 

	bot_clear_inputs()
	
	if argc != 5:
		print("Usage: launcher.py <platform>{} <game>{} <total_runtime_min> <bot_runtime_min> <folder_name>[fc5_stadia_lan_0423_1am]".format(platform_list, game_list))
		sys.exit(0)


	net_em = 0

	if net_em == 1:
		proceed = "N"
		while proceed.upper() == "N":
			print("\n*** Net Emulation Flag Set? ")
			proceed = str(input("Is IP good? (Y/N): ")).upper()
			if proceed.upper() == "N":
				exit(1) 


	platform = args[0]
	game = args[1]
	total_runtime_min = float(args[2])
	bot_runtime_min = float(args[3])
	folder_name = args[4]

	interface = folder_name.split("_")[0].lower()

	folder_name = game+"_"+platform+"_"+folder_name


	if game in ["crew", "crew2"]:
		proceed = "N"
		while proceed == "N":
			print("\n*** On-screen keyboard? ")
			proceed = str(input("Is IP good? (Y/N): ")).upper()

	print(interface)


	# Input correction check for game crew with respect to platform
	if platform in ["stadia", "gfn"]:
		if game.find("crew") >= 0:
			if game != "crew2" or folder_name.split("_")[0] != "crew2":
				print("Incorrect game with respect to platform")
				exit(1)
	elif platform == "luna":
		if game.find("crew") >= 0:
			if game != "crew" or folder_name.split("_")[0] != "crew":
				print("Incorrect game with respect to platform")
				exit(1)


	if total_runtime_min < bot_runtime_min:
		print("Input runtimes incorrect.")
		sys.exit(0)


	signal.signal(signal.SIGINT, signal_handler)

	with open('paths.json', 'r') as fp:
		path_d = json.load(fp)

	folder_path = str(path_d["tempdata"])
	tshark_path = str(path_d["tshark"])
	ffmpeg_cmd_path = str(path_d["ffmpeg"][game])

	print(folder_path)
	print(tshark_path)
	print(ffmpeg_cmd_path)

	dst_ip = ""
	dst_ip = get_streaming_server_ip(folder_path, tshark_path, interface)	
		
	# SAVE THE IPS
	ip_d = {"local": path_d["my_ip"],
			"server": dst_ip}

	with open(folder_path+'ips.json', 'w') as fp:
		json.dump(ip_d, fp, sort_keys=True, indent=4)
	start_time = time.time()


	process_list = []
	
	p = multiprocessing.Process(target=packet_trace_collector, args=(folder_path, tshark_path, interface)) 		# tshark
	process_list.append(p)
	p.start()
	time.sleep(1)


	p = multiprocessing.Process(target=screen_recorder, args=(folder_path, ffmpeg_cmd_path)) 		# ffmpeg
	process_list.append(p)
	p.start()
	time.sleep(1)

	print("\n\nLaunching bot in 5 seconds...")
	time.sleep(5)

	p = multiprocessing.Process(target=game_bot, args=(game, bot_runtime_min, platform)) 		# bot
	process_list.append(p)
	p.start()
	

	time.sleep(int((total_runtime_min+0.3)*60.0))
	kill_all_processes("ffmpeg")
	kill_all_processes("nping")
	kill_all_processes("tshark")

	time.sleep(60)
	

	print("\n\nExiting processses...")

	kill_all_processes("all")

	for p in process_list:
		p.terminate()
		p.join()

	time.sleep(3)

	print("\n\nMoving Files...\n")

	move_files(platform, folder_name)

	print("Exiting Launcher.")
	sys.exit()



