import os

path_l = ["C:/chromium_dataset/",
		  "C:/chromium/",
		  "C:/chromium/src/",
		  "C:/chromium/src/out/",
		  "C:/decaf/",
		  "C:/decaf/tempData/",
		  "C:/decaf/dataset/",
		  "C:/decaf/dataset/gfn",
		  "C:/decaf/dataset/stadia",
		  "C:/decaf/dataset/luna"
]

for p in path_l:
	if not os.path.exists(p):
		os.mkdir(p)
		print("Directory created: ", p)