import numpy as np 
from time import time, sleep
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img, DirectoryIterator
import tensorflow as tf
from tensorflow import keras
import shutil
import json
import os, sys
from helper import *
from PIL import Image, ImageEnhance
import pytesseract
from datetime import datetime
from statistics import mean, stdev, median
from multiprocessing import Process, Manager, Pool


args = sys.argv[1:]
argc = len(args)

#################################################
######## START: CHROMIUM LOGS PROCESSING ########
#################################################

platform_list = ["stadia" , "luna", "gfn"]

TAGS = {"count": 		"count",
		"time_ms": 		"time_ms",
		"ssrc": 		"ssrc",
		"total_bps": 	"totbps",
		"net_fps": 		"nfps",
		"dec_fps": 		"dfps",
		"ren_fps": 		"rfps",
		"current_delay": "cur",
		"jb_delay": 	"jbd",
		"jb_cuml_delay": "jbcd",
		"jb_emit_count": "jbec",
		"decode_delay":  "dec",
		"width": 		"w",
		"height": 		"h",
		"frame_drop":	"fd",

		"freeze_count": "fc",
		"pause_count": "pc",
		"total_freezes_duration_ms": "tfd",
		"total_pauses_duration_ms": "pd",
		"total_frames_duration_ms": "tfmd",
		"sync_offset_ms": "sync",
		"sum_squared_frame_durations": "ssfd",
		"total_squared_inter_frame_delay": "tsif",
		"first_frame_received_to_decoded_ms": "ffrd",
		"frames_decoded": "fdec",
		"frames_rendered": "fren",
		"max_decode_ms":  "mdec",
		"rx_bps": 		"rxbps",
		"rtx_bps": 		"rtxbps",
		"target_delay_ms": "tar",
		"min_playout_delay_ms": "minpd",
		"render_delay_ms": "ren",
		"total_decode_time_ms": "tdec",
		"total_inter_frame_delay": "tifd",
		"interframe_delay_max_ms": "ifdm"}


STREAMFILE = "videoReceiveStream.txt"
RTCSTATS   = "rtcStatsCollector.txt"
LOGFILE = "bot_log.csv"



def process_videoReceiveStream_log(path):

	print("Processing chromium VRS stats in: {}".format(path))

	# Path directory fix
	if path[-1] != "/":
		path += "/"

	# CHECK FOR LOG FILE
	log_data = ""
	log_start = 0
	log_end = 0

	if os.path.isfile(path+LOGFILE):
		log_data = open(path+LOGFILE, "r").read().split("\n")
	elif os.path.isfile(path+"log.csv"):
		log_data = open(path+"log.csv", "r").read().split("\n")

	if len(log_data) > 0:
		for e in log_data:
			if len(e) > 1:
				e = e.split(",")

				if log_start == 0:
					log_start = float(e[0])/1000000000.00
				else:
					log_end = float(e[0])/1000000000.00

	# print("PATH: ", path)
	# print("LOG TS:", log_start, log_end, log_end - log_start, "\n")

	data = open(path+STREAMFILE, 'r').read().split("\n")
	data_dict = {}

	ts_start = 0

	tags_list = list(TAGS.keys())

	N = len(data)
	progress = 0
	progress_threshold = int(N*0.25)+1

	for line in data:
		if line.find("VRSSTATS") > 0:

			line = line.split(",")
			ts_mili = float(line[1])/1000.00
			if ts_start == 0:
				ts_start = ts_mili
			process = False

			if log_start > 0 and log_start <= ts_mili and log_end >= ts_mili:
				process = True

			if process == True:
				# print(ts_mili)
				ssrc = ""
				for i in range(3,len(line)):
					# print(item)
					stat = line[i].split(":")
					# print(stat[0], TAGS["ssrc"])
					if stat[0] == TAGS["ssrc"]:
						ssrc = stat[1]
						if ssrc not in list(data_dict.keys()):
							data_dict[ssrc] = {}
							
							for tag in tags_list:
								# tag = TAGS[tag]
								if tag == "count":
									data_dict[ssrc][TAGS["count"]] = 0
								else:
									if tag not in ["ssrc"]:
										data_dict[ssrc][tag] = []	


				
						data_dict[ssrc][TAGS["count"]] += 1
						data_dict[ssrc][TAGS["time_ms"]].append(ts_mili)
					
					for tag in tags_list:
						tag_val = TAGS[tag]
						if stat[0] == tag_val and tag_val not in [TAGS["time_ms"], "ssrc"]:
					 		data_dict[ssrc][tag].append(float(stat[1]))
					 		break

		# Progress tracking
		progress += 1
		if progress % progress_threshold == 0:
			print("Parsed {}%".format(int(progress*100.0/N)))

	writeDict(path+"parsed_videoReceiveStream.json", data_dict)

	print("Parsed {}%".format(int(progress*100.0/N)))
		
	
	# Generate video summary statistitcs
	ssrc_list = list(data_dict.keys())
	ssrc = ""
	maxi = 0
	summary_dict = {}

	for ent in ssrc_list:
		if data_dict[ent][TAGS["count"]] > maxi:
			ssrc = ent
			maxi = data_dict[ent][TAGS["count"]]

	for tag in tags_list:
		if tag not in  ["count", "ssrc"]:
			summary_dict[tag] = {"mean": mean(data_dict[ssrc][tag]),
							"stdev": stdev(data_dict[ssrc][tag]),
							"median": median(data_dict[ssrc][tag]),
							"min": min(data_dict[ssrc][tag]),
							"max": max(data_dict[ssrc][tag])}

	writeDict(path+"vrs_summary_stats.json", summary_dict)


def process_rtcStatsCollector_log(path):

	print("Processing chromium RTC stats in: {}".format(path))

	# Path directory fix
	if path[-1] != "/":
		path += "/"


	# CHECK FOR LOG FILE
	# log_file_path = path+LOGFILE
	log_data = ""
	log_start = 0
	log_end = 0

	if os.path.isfile(path+LOGFILE):
		log_data = open(path+LOGFILE, "r").read().split("\n")
	elif os.path.isfile(path+"log.csv"):
		log_data = open(path+"log.csv", "r").read().split("\n")

	
	if len(log_data) > 0:
		for e in log_data:
			if len(e) > 1:
				e = e.split(",")

				if log_start == 0:
					log_start = float(e[0])/1000000000.00
				else:
					log_end = float(e[0])/1000000000.00

	# print("PATH: ", path)
	# print("LOG TS:", log_start, log_end, log_end - log_start, "\n")


	data = open(path+RTCSTATS, 'r').read().split("\n")
	# print("LINES:", len(data))
	data_dict = {}

	ts_start = 0

	tags_list = list(TAGS.keys())

	# latest packet loss
	previous_loss = -1
	correct_loss = 0

	loss_d = {}
	for kk in ['audio', 'video']:
		loss_d[kk] = {}
		loss_d[kk]['previous_loss'] = -1
		loss_d[kk]['correct_loss'] = -1

	N = len(data)
	progress = 0
	progress_threshold = int(N*0.25)+1

	for line in data:
		tmp_line = line.split(",")
		ts_mili = float(tmp_line[1])/1000.00
		if ts_start == 0:
			ts_start = ts_mili

		process = False

		if log_start > 0 and log_start <= ts_mili and log_end >= ts_mili:
			process = True

		first_bracket = -10
		last_bracket = -10
		if process == True:
			for i, ent in enumerate(line):
				if ent == "{" and first_bracket == -10:
					first_bracket = i
				if ent == "}":
					last_bracket = i
					dict_line = json.loads(line[first_bracket:last_bracket+1])
					first_bracket = -10

					media_type = ""

					l_type = ""
					l_id = ""
					for lk in list(dict_line.keys()):
						if lk == "type":
							l_type = dict_line[lk]
						if lk == "type" and dict_line[lk] not in list(data_dict.keys()):
							data_dict[l_type] = {}
						

						if lk == "id":
							l_id = dict_line[lk]
						if lk == "id" and dict_line[lk] not in list(data_dict[l_type].keys()):
							data_dict[l_type][l_id] = {}

						if lk == "mediaType":
							media_type = dict_line[lk]
						

						#### Latest version for packet loss adjustment based on duplicates and out of order
						# Packetslost check is added because of negative values
						# https://groups.google.com/g/discuss-webrtc/c/YXs7nG6FD48?pli=1
						# RFC 3550

						if lk not in ["type", "id"]:
							if lk == "packetsLost" and media_type in ['audio', 'video']:
								if lk not in list(data_dict[l_type][l_id].keys()):																					
									if dict_line[lk] < 0:
										loss_d[media_type]['correct_loss'] = 0
										loss_d[media_type]['previous_loss'] = 0
										data_dict[l_type][l_id][lk] = [loss_d[media_type]['correct_loss']]
									else:				
										loss_d[media_type]['correct_loss'] = dict_line[lk]
										loss_d[media_type]['previous_loss'] = dict_line[lk]																													
										data_dict[l_type][l_id][lk] = [loss_d[media_type]['correct_loss']]
								else:
									if dict_line[lk] < 0:
										data_dict[l_type][l_id][lk].append(loss_d[media_type]['correct_loss'])
										loss_d[media_type]['previous_loss'] = dict_line[lk]

									else:
										if loss_d[media_type]['previous_loss'] < 0 and loss_d[media_type]['previous_loss'] < dict_line[lk]:
											loss_d[media_type]['correct_loss'] += dict_line[lk] - loss_d[media_type]['previous_loss']

										elif loss_d[media_type]['previous_loss'] >= 0 and loss_d[media_type]['previous_loss'] < dict_line[lk]:																			
											loss_d[media_type]['correct_loss'] += dict_line[lk] - loss_d[media_type]['previous_loss']
											
										loss_d[media_type]['previous_loss'] = dict_line[lk]
										data_dict[l_type][l_id][lk].append(loss_d[media_type]['correct_loss'])
							else:
								if lk not in list(data_dict[l_type][l_id].keys()):																										
									data_dict[l_type][l_id][lk] = [dict_line[lk]]
								else:
									data_dict[l_type][l_id][lk].append(dict_line[lk])

		# Progress tracking
		progress += 1
		if progress % progress_threshold == 0:
			print("Parsed {}%".format(int(progress*100.0/N)))

	writeDict(path+"parsed_rtcStatsCollector.json", data_dict)

	print("Parsed {}%".format(int(progress*100.0/N)))
	
	# Generate RTT summary
	rtt_key = "currentRoundTripTime"
	types_list = list(data_dict.keys())
	summary_dict = {}
	rtt_l = []
	ts_l = []
	found = 0
	
	for type_ in types_list:
		for id_ in list(data_dict[type_].keys()):
			if rtt_key in list(data_dict[type_][id_].keys()):
				rtt_l = data_dict[type_][id_][rtt_key]
				ts_l  = data_dict[type_][id_]["timestamp"]
				found = 1
				break
		if found == 1:
			break

	for i, val in enumerate(rtt_l):
		rtt_l[i] = val*1000
		ts_l[i]  = ts_l[i]/1000000.0

	summary_dict = {"rtts": rtt_l,
					"ts": ts_l,
					"mean": mean(rtt_l),
					"stdev": stdev(rtt_l),
					"median": median(rtt_l),
					"min": min(rtt_l),
					"max": max(rtt_l)}

	writeDict(path+"current_rtt.json", summary_dict)

	# Generate summary packet loss stats
	type_ = "inbound-rtp"
	search_key = "RTCInboundRTPVideoStream"
	
	summary_dict = {}
	packetsLost_l = []
	packetsReceived_l = []
	ts_l = []
	found = 0
	
	
	for id_ in list(data_dict[type_].keys()):
		if id_.find(search_key) >= 0:
			if "packetsReceived" in list(data_dict[type_][id_].keys()):
				packetsReceived_l = data_dict[type_][id_]["packetsReceived"]
				packetsLost_l = data_dict[type_][id_]["packetsLost"]
				ts_l  = data_dict[type_][id_]["timestamp"]
				found = 1
				break

	for i, val in enumerate(ts_l):
		ts_l[i]  = ts_l[i]/1000000.0
	
	summary_dict = {"packetsReceived": packetsReceived_l,
					"ts": ts_l,
					"packetsLost": packetsLost_l}

	writeDict(path+"packet_loss_stats.json", summary_dict)



#################################################
######## END: CHROMIUM LOGS PROCESSING ##########
#################################################






#################################################
######## START: GAME RECORDING PROCESSING #######
#################################################


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


# OCR corrections
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




def process_game_recording(path, param_dict):	

	print("Processing game video in: {}".format(path))

	cancel_iteration = 0

	path, platform, game = path[0], path[1], path[2] 
	

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
			cmd = "ffmpeg -i "+path+video_orig+" -filter:v "+"'"+param_dict["video_crop_param"][game+"_"+platform]+"' "+path+"video_cropped.mkv"
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
			model = tf.keras.models.load_model(param_dict["models"][game])
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


#################################################
######## END: GAME RECORDING PROCESSING #######
#################################################

def get_data_directories(path):
	raw_data_path_list = open(path, "r").read().split("\n")[1:]

	data_path_list = []

	for entry in raw_data_path_list:
		if len(entry) > 2:
			entry = entry.split(",")
			data_path_list.append((entry[0], entry[1], entry[2]))

	return data_path_list


if __name__ == "__main__":	

	# Param and path dictionary
	pp_path = "./params.json"
	param_dict = readDict(pp_path)

	data_path_list = get_data_directories(param_dict["data_directories"])

	print(data_path_list)

	for path in data_path_list:
		process_videoReceiveStream_log(path[0])
		process_rtcStatsCollector_log(path[0])
		process_game_recording(path, param_dict)


	