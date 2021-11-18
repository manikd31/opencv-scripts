# OpenCV Scripts

Demo scripts to use for OpenCV projects.

### Table of Contents

- [Requirements and Installation](#requirements-and-installation)
  - [Cloning the repository](#cloning-the-repository)
  - [Installing required dependencies](#installing-required-dependencies)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Video Recording](#video-recording)
  - [Downsizing Video](#downsizing-video)
- [Data Augmentation](#data-augmentation)
  - [Horizontal Flipping](#horizontal-flipping)
  - [Grayscale Conversion](#grayscale-conversion)
  - [Color Inversion](#color-inversion)
  - [Video Blurring](#video-blurring)


#### Helper scripts:
- `record_video.py` : record videos using terminal and save to desired location in local system
- `downsize_video.py` : downsample a video with fps, for eg. recorded at 24 fps but downsample at 4 fps
- `test_output.py` : view the tentative output window for testing
- `process_output.py` : post-process input video stream and get live predictions
- `train_model.py` : train a model on mnist dataset and save it to use with test_output.py
- `augment_dataset.py` : script to process all raw videos and create an augmented data-set from the selected data augmentation methods


#### Dataset Augmentation:
- `flip_video.py` : horizontally flip recorded videos
- `convert_to_gray.py` : convert colored videos to grayscale
- `invert_color.py` : invert image colors instead of converting to grayscale
- `blur_video.py` : add gaussian/averaging blur to videos


#### TODO:
- [x] create the model to train using PyTorch
- [x] finalize data-set to use
- [x] add padding for shorter videos, or clip frames for longer videos, to train on in case number of input frames is fixed
- [x] create a new script to train and test model outputs
- [x] create a new output window for live testing
- [x] complete report by November 19th


#### Project Outline:
- May 2021 - [Tentative outline](https://docs.google.com/document/d/1sXTo-BjUdvTLN2oQKA-ix1LHM9sqz-XGWphIZPI0ots/edit?usp=sharing)
- Aug 2021 - [Progress and updated outline](https://docs.google.com/document/d/1Lqoa6uQgTHosYO7uk4eMCXWYMVb1Am1_jhMtE1oeJIc/edit?usp=sharing)
- Nov 2021 - [Final Report](https://www.overleaf.com/project/6182e36c2736e72c23b1342c)


#### Project Slides Deck:
- May 2021 - [Tentative outline](https://docs.google.com/document/d/1sXTo-BjUdvTLN2oQKA-ix1LHM9sqz-XGWphIZPI0ots/edit?usp=sharing)
- 13 May 2021 - [Introductory presentation](https://docs.google.com/presentation/d/1oDfragLFvmWzsUEXBTLvAuij-GW0XwMH_SSIyqX6OqE/edit?usp=sharing)
- 22 Jun 2021 - [Project Overview]()
- 22 Jul 2021 - [Progress and updates](https://docs.google.com/presentation/d/1PjKQRSTTjoYRZZOgmXeid-PW3HIyBOyh8sNw_OZjoU8/edit?usp=sharing)
- 10 Sep 2021 - [Updated outline and progress](https://docs.google.com/presentation/d/15rXKTdLrlvkxmiaJCz0HH59UR8_FoUvMuG5g9bL54IQ/edit?usp=sharing)
- 08 Oct 2021 - [Progress Updates](https://docs.google.com/presentation/d/1lDVqSbILRHq1Q6wEgJD8x5HiSXUuBDnv8lTo3K8qCME/edit?usp=sharing)
- 29 Oct 2021 - [Progress Updates](https://docs.google.com/presentation/d/18JAQ8uvuaF--sisqcqrYt9JtSETj3Fel04PmZldMkvc/edit?usp=sharing)
- 19 Nov 2021 - [Final Presentation](https://docs.google.com/presentation/d/1tBevJdcTyUB3V7iAo2042F5-Gu-0YKPzbUMACSga2mg/edit?usp=sharing)

---

## Requirements and Installation

The following steps are confirmed to work on Windows 10 and macOS.

### Step 1
### Cloning the repository

The first step is to clone this repository into a desired local directory, and switch to the project:
    
    git clone https://github.com/manikd31/opencv-scripts.git
    cd opencv-scripts

### Step 2
### Installing required dependencies

Once cloned, install the dependencies specified in the file `requirements.txt` within a virtual environment, preferably using [miniconda](https://docs.conda.io/en/latest/miniconda.html). To create the virtual environment, use the command:

    conda create -y -n opencv-scripts
    conda activate opencv-scripts

And then, install the dependencies using:

    pip install -r requirements.txt

---

## Getting Started

The first step to using any of the scripts is to populate/update the `constants.py` file with the relevant default values used across the project. The most relevant ones will be:

    TEST_PATH_IN = r"C:/Users/user/Desktop"
    TEST_PATH_OUT = r"C:/Users/user/Desktop"
    TEST_FILE_NAME = "video_name.mp4"

---

## Usage

To begin using the scripts, follow the commands mentioned below:

### Video Recording

Use this script to record several videos in your desired directory just with the help of a few key presses.
- Run the script using the command:

      python record_video.py

- When prompted about the video resolution, select the one you wish to use _(select 480p for low-res 640x480 videos)_

      Select the video resolution:
       > 480p
         720p
         1080p

- Next, specify the path to save the recorded videos to (if the directory doesn't exist, the program will create one)

      Enter the path to save the videos to:     C:/Users/user/Desktop

- And finally, enter the name of the video (with or without the extension .MP4)

      Enter the video name:      video_name.mp4

When recording, the videos will be saved with a number at the end, for example, the first 2 videos with the name `video_name.mp4` will become `video_name_0.mp4` and `video_name_1.mp4` to avoid overwriting files with same names.

To manipulate the video recording mechanism, there are key shortcuts on the screen. The display also shows if a video is being recorded or not, and how long the video has been recorded so far. These keypresses are as follows:
- Press `R` to start recording a video if not currently recording.
- Press `E` to end the current video recording and save it to the directory.
- Press `Q` to terminate the script and get back to the terminal.

<br />

### Downsizing Video

---

## Data Augmentation
Use these data augmentation methods on raw videos to create a variety of different styles of videos to enhance the dataset.

### Horizontal Flipping

<br />

### Grayscale Conversion

<br />

### Color Inversion

<br />

### Video Blurring

---
