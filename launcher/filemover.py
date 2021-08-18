import os
from os import path
from os import listdir
from os.path import isfile, join
import shutil
import sys
import json


def clear_directory(folder):
	with open('paths.json', 'r') as fp:
		path_d = json.load(fp)

	folder = path_d[folder]
	
	print("START: **********************************")
	print("Removing all files from ", folder)

	

	for filename in os.listdir(folder):
		file_path = os.path.join(folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))
	print("END: **********************************")


def move_files(platform, folder):
	with open('paths.json', 'r') as fp:
		path_d = json.load(fp)

	dataset_path = path_d["dataset"]

	dataset_path = dataset_path+platform+"\\"

	# CHECK IF platform FOLDER EXISTS
	if os.path.isdir(dataset_path):

		dataset_path = dataset_path+"\\"+folder   	

		# CREATE GAME ITERATION FOLDER
		if not os.path.isdir(dataset_path):
		   os.makedirs(dataset_path)
		else:
			print("Path Exists: ", dataset_path)

		dataset_path_img = dataset_path+"\\frames"
		if not os.path.isdir(dataset_path_img):
		   os.makedirs(dataset_path_img)
		else:
			print("Path Exists: ", dataset_path_img)

		dataset_path_img = dataset_path+"\\extractedFrames"
		if not os.path.isdir(dataset_path_img):
		   os.makedirs(dataset_path_img)
		else:
			print("Path Exists: ", dataset_path_img)

		
		for key in list(path_d["files_to_move"].keys()):
			path = path_d["files_to_move"][key]
			if key == "tempdata":
				print("Here")
				files = [f for f in listdir(path) if isfile(join(path, f))]

				for file in files:
					try:
						shutil.move(path+file, dataset_path)
						print("Moved: ", path+file)
					except Exception as e:
						print(e)
				
			else:
				try:
					shutil.move(path, dataset_path)
					print("Moved: ", path)
				except Exception as e:
					print(e)


	else:
		print("\nError: Platform '"'{}'"' folder does not exist. Create manually.\n".format(platform))

	