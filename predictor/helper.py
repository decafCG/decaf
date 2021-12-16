import json
import os
from os import listdir
from os.path import isfile, join


# DICTIONARY OPERATIONS

def readDict(path):
	with open(path, 'r') as fp:
		data_d = json.load(fp)
	return data_d


def writeDict(path, data_d):
	with open(path, 'w') as fp:
		json.dump(data_d, fp, sort_keys=True, indent=4, separators=(',', ': '))


def dictKeys(data_d):
	return list(data_d.keys())


# PRINTING

def printDict(data_d):
	print(json.dumps(data_d, sort_keys=True, indent=4, separators=(',', ': ')))


def printList(data_l):
	print("\nPrint List entries: ", len(data_l))
	for i, entry in enumerate(data_l):
		print(i, entry)

def printLL(data_l):
	print("List length: ", len(data_l))

def printDL(data_d):
	print("Dictionary key length: ", len((data_d.keys())))


# FILESYSTEM OPERATIONS

def mkDir(p):
	if not os.path.exists(p):
		os.mkdir(p)

def getDirFiles(mypath):
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	return onlyfiles

# SORTING

def bubbleSort(main_l, second_l, order):

	n = len(main_l)

	for i in range(n-1):
		flag = 0
		for j in range(n-1):

			if order == "A":
				if main_l[j] > main_l[j+1] : 
					main_l[j], main_l[j+1] = main_l[j+1], main_l[j]
					second_l[j], second_l[j+1] = second_l[j+1], second_l[j]

					flag = 1
			else:
				if main_l[j] < main_l[j+1] : 
					main_l[j], main_l[j+1] = main_l[j+1], main_l[j]
					second_l[j], second_l[j+1] = second_l[j+1], second_l[j]

					flag = 1

			if flag == 0:
				break

	return main_l, second_l

