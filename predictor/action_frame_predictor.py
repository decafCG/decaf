import numpy as np 
import pandas as pd 
import os, sys
from IPython.display import display
from IPython.display import Image as _Imgdis
from PIL import Image, ImageOps
from time import time
from time import sleep
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img, DirectoryIterator
import tensorflow as tf
from tensorflow import keras
from collections import OrderedDict
import shutil
import json
import os, sys
from helper import *
from PIL import Image, ImageEnhance
import pytesseract
import csv
from datetime import datetime
import psutil
from statistics import mean, stdev, median
from multiprocessing import Process, Manager, Pool





args = sys.argv[1:]
argc = len(args)

platform_list = ["stadia" , "luna", "gfn"]

enhancer_set = 1
location = ""

def data_loading(data_path, game):
	# Predetermined variables
	batch_size = 32
	epochs = 15
	batch_size_test = 1

	if game == "acv":
		IMAGE_SHAPE = (70, 70) # (height, width) in no. of pixels
	else:
		IMAGE_SHAPE = (224, 224) # (height, width) in no. of pixels

	
	image_gen_val = ImageDataGenerator(rescale=1./255)

	valid_generator = image_gen_val.flow_from_directory(
	    batch_size = batch_size,
	    directory=data_path,
	    target_size=(IMAGE_SHAPE),
	    shuffle=False,
	    )

	return valid_generator

def prediction(model, tmp_path, game):

	valid_generator = data_loading(tmp_path+"cropped/", game)

	# Get file paths/name.png into batch_filepath_list
	batch_filepath_list = []
	batch_index = 0
	while batch_index < len(valid_generator):
		idx = (batch_index)  * valid_generator.batch_size
		tmp = valid_generator.filenames[idx : idx + valid_generator.batch_size]
		batch_filepath_list.append(tmp)
		batch_index += 1

	print(len(batch_filepath_list))

	# Number of batch iteration in the valid_generator
	total_iterations = np.ceil(valid_generator.samples/valid_generator.batch_size)
	iter_idx = 0

	prediction_d = {}
	# Run prediction on all the batches
	while iter_idx < total_iterations:
		if iter_idx % 200 == 0:
			print("BATCH ITERATION #: ", iter_idx, "/", total_iterations)
		
		val_image_batch, val_label_batch = next(iter(valid_generator))

		# Prediction on batch using model
		tf_model_predictions = model.predict(val_image_batch)

		predicted_ids = np.argmax(tf_model_predictions, axis=-1)
		# predicted_labels = dataset_labels[predicted_ids]

		predicted_labels = []
		for val in predicted_ids:
			if val == 0:
				predicted_labels.append("Action")
			else:
				predicted_labels.append("NoAction")

		filenames = batch_filepath_list[iter_idx]
		for n in range(0,len(predicted_labels)):
			if predicted_labels[n] == "Action":
				prediction_d[filenames[n]] = predicted_labels[n]
		iter_idx += 1

	print("BATCH ITERATION #: ", iter_idx, "/", total_iterations)
	path = tmp_path+"predicted_files.json"

	writeDict(path, prediction_d)



characters_l = ["A", "o", "O", "B", "l", "$", "Q"]
number_l     = ["4", "0", "0", "8", "1", "5", "0"]



def generate_extracted_frames_timestamp_dictionary_multiprocessing(args):

	## TIMESTAMP CONVERTION W.R.T UTC
	## Timestamps are recorded by FFmpeg and python are wrt to local time of the location
	# However, python converts it into UTC. Therefore, we have to ADD the offset for western location wrt to UTC

	# Raleigh, Boston +4
	EST = 14400.00

	
	if location == "sanjose":
		# +7
		EST = 25200.00
	elif location == "dallas":
		# +5
		EST = 18000.00


	path = args[0]
	file = args[1]
	val_d = args[2]


	skip_flag = 0

	img = Image.open(path+file+".png")
	img = img.crop((0, 0, 300, 37)) 
	newsize = (1500, 200)
	img = img.resize(newsize)

	enhancer = ImageEnhance.Contrast(img)
	factor = 6 #increase contrast
	img = enhancer.enhance(factor)

	text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
	text = text.split()
	# print(file, temp)

	date = ""
	time = ""


	if len(text) == 4:
		date = text[0]
		time = "{}.{}".format(text[1], text[2])


	elif len(text) == 3:
		date = text[0].split("-")
		time = text[1].split(":")
		millisecond = text[2]

		if len(date) == 3 and len(time) == 3 and len(time[2]) == 2:
			date = text[0]
			time = "{}.{}".format(text[1], text[2])
	else:
		skip_flag = 1



	if skip_flag == 0:				

		ts = date+"~"+time

		# Fix characters in the text
		for j, char in enumerate(characters_l):
			if ts.find(char) >= 0:
				tmp_ts =  "Character found: {}".format(ts)
				ts = ts.replace(char, number_l[j])
				# print(tmp_ts, "Replaced: ", ts)
				# print("Character found: ", ts, "Replaced: ", ts)

		try:
			utc_time = datetime.strptime(ts, "%Y-%m-%d~%H:%M:%S.%f")
			epoch_time = float((utc_time - datetime(1970, 1, 1)).total_seconds())
			val_d[str(file)] = [text, float(epoch_time+EST)]

		except Exception as e:
			print("utc failor at ts {}. Reason {}".format(ts, e))
			print("skipped", text, file, "\n")

			val_d[str(file)] = [text, "skipped"]

	else:
		print("skipped len:", text, file)
		val_d[str(file)] = [text, "skipped"]




def process_game_video(data_path_list, prediction_param_dict):	

	cancel_iteration = 0

	for path in data_path_list:
		
		print("Processing dir: {}".format(path))
	
		path, game, platform = path[0], path[1], path[2] 
		

		# Get all files in data directory specified by path
		file_l = os.listdir(path)

		# Get original video file
		video_orig = ""
		for file in file_l:
			if file.find("video_1") >= 0:
				video_orig = file
				break

		if video_orig != "":
			print(video_orig)


			# Create folders in data directory
			uncropped_frames_path = path+"uncropped/"
			cropped_frames_path = path+"cropped/"
			cropped_action_frames_path = path+"cropped/Action/"
			extracted_frames_path = path+"extractedFrames/"
			

			crop_paths = [uncropped_frames_path, cropped_frames_path, cropped_action_frames_path, extracted_frames_path]
			for p in crop_paths:
				if not os.path.exists(p):
					os.mkdir(p)

			
			# Crop video according to the game so that cropped images can be used in prediction
			if not os.path.exists(path+"video_cropped.mkv"):
				cmd = "ffmpeg -i "+path+video_orig+" -filter:v "+"'"+prediction_param_dict["video_crop_param"][game+"_"+platform]+"' "+path+"video_cropped.mkv"
				print("\nCroping video: ", cmd)
				os.system(cmd)
				print("Cropped")
			else:
				print("\nCropped video already exists.")


			# Convert to frames both uncropped(original) and cropped video
			print("\n-> Frame conversion...")
			if len(os.listdir(uncropped_frames_path)) == 0:
				cmd = "ffmpeg -i "+path+video_orig+" "+uncropped_frames_path+"%d.png"
				print("Converting {} to frames: {}\n".format(video_orig, cmd))
				os.system(cmd)

			if len(os.listdir(cropped_action_frames_path)) == 0:
				cmd = "ffmpeg -i "+path+"video_cropped.mkv"+" "+cropped_action_frames_path+"%d.png"
				print("\nConverting video_cropped.mkv to frames: {}\n".format(cmd))
				os.system(cmd)

			print("Frame conversion complete")


			# Test if any cropped file is corrupt. This may happen because of FFmpeg recording crash.
			print("Testing for corrupt cropped files")
			corrupt_imgs = 0
			cancel_iteration = 0
			for file in os.listdir(cropped_action_frames_path):
				try: 
					img = Image.open(cropped_action_frames_path+file)
					img.verify()
				except Exception as e:
					corrupt_imgs += 1
					os.remove(cropped_action_frames_path+file)
			
			print("Corrupt files: ", corrupt_imgs)

			# In case, corrupt images exceed 100, we terminate processing and declare the data corrupt. 
			# Recollect data for this iteration. 
			if corrupt_imgs > 100:
				cancel_iteration = 1
				print("*** Cancel_iteration-> "+path+" corrupt_imgs: "+str(corrupt_imgs)+"\n")
				


			if cancel_iteration == 0:
				# Prediction on cropped frames
				print("\nStarting prediction")
				model = tf.keras.models.load_model(prediction_param_dict["models"][game])
				prediction(model, path, game)
				print("\nPrediction complete")


				# Extract predicted frames from uncropped_frames_path and place them in extracted_frames_path
				prediction_d = readDict(path+"predicted_files.json")

				for file in list(prediction_d.keys()):
					try: 
						file = file.split("/")
						if len(file) > 0:
							file = file[1]
							shutil.copyfile(uncropped_frames_path+file, extracted_frames_path+file)
					except Exception as e:
						print('Failed to copy %s. Reason: %s' % (file, e))

				print("ExtractedFrames: "+str(len(os.listdir(extracted_frames_path)))+"\n")
				

				# Generate timestamps for extracted frames
				if len(os.listdir(extracted_frames_path)) > 0:
					manager = Manager()
					print("\nGenerating timestamps")
					files = os.listdir(extracted_frames_path)
					files_num = []
					for f in files:
						files_num.append(int(f[:len(f)-4]))
					files_num.sort()

					args_l = []
					d = manager.dict()

					for file in files_num:
						d[str(file)] = []
						args_l.append((extracted_frames_path, str(file), d))

					pool = Pool(2)
					results = pool.map(generate_extracted_frames_timestamp_dictionary_multiprocessing, args_l)

					# Generate output dictionary
					tmp_d = {}
					for key in list(d.keys()):
						tmp_d[key] = d[key]

					writeDict(path+"frame_timestamps.json", tmp_d)

					print("Timestamps processed: "+str(len(list(tmp_d.keys()))))					
					
				else:
					print("\nNo frames to generate timestamps")
	
				print("Complete: "+path)		

		else:
			print("No video_orig in dir: ", path)





if __name__ == "__main__":

	

	# Param and path dictionary
	pp_path = "./prediction_paths_params.json"
	prediction_param_dict = readDict(pp_path)

	data_path_list = [("./", "stadia", "fc5")]

	process_game_video(data_path_list, prediction_param_dict)


	