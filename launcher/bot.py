import time
# import win32com.client as comclt
import win32api, win32con
from datetime import datetime
import signal
import sys
import json


with open("paths.json", "r") as fp:
		path_d = json.load(fp)

log_path = path_d["tempdata"]+"bot_log.csv"


def rightClick():
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
	time.sleep(0.1)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
	
def right_click_pressed(ts):
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
	
def right_click_release():
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)

def leftClick():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(.1)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	
def left_click_pressed(ts):
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	if ts > 0:
		time.sleep(ts)

def left_click_release():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	
def left_click_press_and_release(ts):
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(ts)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	time.sleep(0.05)

def right_click_press_and_release(ts):
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
	time.sleep(ts)	
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
	time.sleep(0.1)

def middleClick():
	win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN,0,0)
	time.sleep(0.1)
	win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP,0,0)

def middle_click_pressed(ts):
	win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN,0,0)
	time.sleep(ts)
	
def middle_click_release():
	win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP,0,0)
	
def keyPress(VK_CODE):
	win32api.keybd_event(VK_CODE, 0,0,0)
	win32api.keybd_event(VK_CODE,0 ,win32con.KEYEVENTF_KEYUP ,0)

def moveMouse(x):
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,x,0)
	
def move_mouse_90():
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,2500,0)

def move_mouse_steady(count):
	i = 0 
	ypix = 0
	xpix = 2
	while i < count:
		win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,xpix,ypix)
		time.sleep(0.001)
		i += 1

def bot_clear_inputs():
	left_click_release()
	right_click_release()
	left_click_release()
	right_click_release()
	middle_click_release()
	middle_click_release()

def bot_farcry5_loop_movement(time_min, platform):

	time_limit = int(time_min * 60.0)
	fh = open(log_path, "w")
	log = ""

	start_time = time.time()
	lapse = 0

	count = 499
	sleep_interval = 3.8

	t1 = 0
	t2 = 0
	diff = 0

	while  lapse < time_limit:
		
		val = str(time.time_ns())+",moveForward\n"
		log += val
		# middle_click_pressed(sleep_interval-diff)
		middle_click_pressed(sleep_interval)

		val = str(time.time_ns())+",Fire\n"
		log += val
		left_click_pressed(0.08)
		left_click_release()
		time.sleep(sleep_interval)

		val = str(time.time_ns())+",Fire\n"
		log += val
		left_click_pressed(0.08)
		left_click_release()

		t1 = time.time_ns()/1000000000.0

		middle_click_release()

		val = str(time.time_ns())+",moveMouse\n"
		log += val
		move_mouse_steady(count)

		val = str(time.time_ns())+",moveMouse\n"
		log += val
		move_mouse_steady(count)

		t2 = time.time_ns()/1000000000.0

		diff = t2-t1

		if platform == "stadia":

			val = str(time.time_ns())+",moveMouse\n"
			log += val
			move_mouse_steady(count)
	
		lapse = time.time() - start_time

		if len(log) > 50000:
			fh.write(log)
			log = ""

	fh.write(log)
	fh.close()
	log = ""



def bot_acv_loop_movement(time_min, platform):

	time_limit = int(time_min * 60.0)
	fh = open(log_path, "w")
	log = ""

	start_time = time.time()
	lapse = 0

	count = 500

	sleep_interval = 2.3

	right_click_press_and_release(0.08)

	while  lapse < time_limit:
	# if 1:
		
		val = str(time.time_ns())+",moveForward\n"
		log += val
		middle_click_pressed(sleep_interval)
				
		val = str(time.time_ns())+",Fire\n"
		log += val
		right_click_press_and_release(0.12)
		time.sleep(sleep_interval)

		val = str(time.time_ns())+",Fire\n"
		log += val
		right_click_press_and_release(0.12)
		time.sleep(sleep_interval)

		val = str(time.time_ns())+",Fire\n"
		log += val
		right_click_press_and_release(0.12)

		middle_click_release()
	
		val = str(time.time_ns())+",moveMouse\n"
		log += val
		move_mouse_steady(count)
		
		val = str(time.time_ns())+",moveMouse\n"
		log += val
		move_mouse_steady(count)

		val = str(time.time_ns())+",Fire\n"
		log += val
		right_click_press_and_release(0.12)
	
		lapse = time.time() - start_time

		if len(log) > 50000:
			fh.write(log)
			log = ""

	fh.write(log)
	fh.close()
	log = ""


key_xy = {"w": [22,29],
			  "s": [26,35],
			  "a": [18,35],
			  "d": [32,35]}


def mouse_osk_pos(key):
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,-10000,-10000)
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,key_xy[key][0],key_xy[key][1])
	
def brake(ts):
	mouse_osk_pos("s")
	left_click_press_and_release(ts)

def accelerate(ts):
	mouse_osk_pos("w")
	left_click_press_and_release(ts)

def steer_right(ts):
	mouse_osk_pos("d")
	left_click_press_and_release(ts)

def steer_left(ts):
	mouse_osk_pos("a")
	left_click_press_and_release(ts)

def bot_crew_loop_movement(time_min, platform):

	time_limit = int(time_min * 60.0)
	fh = open(log_path, "w")
	log = ""

	start_time = time.time()
	lapse = 0

	accelerate(0.2)
	brake(0.07)
	accelerate(0.2)

		
	while  lapse < time_limit:
		val = str(time.time_ns())+",a\n"
		log += val
		accelerate(2.5)

		val = str(time.time_ns())+",s\n"
		log += val
		brake(0.07)
		
		val = str(time.time_ns())+",w\n"
		log += val
		accelerate(0.4)
		time.sleep(2.2)
		
		val = str(time.time_ns())+",s\n"
		log += val
		brake(0.07)
		
		val = str(time.time_ns())+",w\n"
		log += val
		accelerate(0.4)
		time.sleep(2.2)
	
		if platform == "luna":
			val = str(time.time_ns())+",r\n"
			log += val
			brake(6.0)
		else:
			val = str(time.time_ns())+",r\n"
			log += val
			brake(5.4)

		val = str(time.time_ns())+",wb\n"
		log += val
		accelerate(0.4)

		lapse = time.time() - start_time

		if len(log) > 50000:
			fh.write(log)
			log = ""

	fh.write(log)
	fh.close()
	log = ""

	

if __name__ == '__main__':
	pass
	