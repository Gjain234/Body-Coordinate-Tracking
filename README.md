# Pose-Detect
This app uses the CMU OpenPose demo to allow users to capture themselves making a certain pose, and then give instructions on how to recreate that pose.

## Instructions to Run:

1. In the Constants.py file, fill out appropriate directories for your openpose install and openpose.bin executable. Also fill out the directory you want your json files written to. If you want to see real images of yourself instead of stick figures, you will need to also need to add the directory name for where openpose can write the image files while running the app. If you want to save the annotated images, set that flag to true and set the directory for that as well. 

2. Also set if you want the Camera to be flipped or not. A flipped camera will function as a mirror, while the regular setting will show an image like a photo taken of you.

3. Make sure you have a webcam plugged in, and from inside the PoseDetect directory, run the command:
python app.py

4. Press 'c' to capture a certain pose, and 'q' to quit the program. Make sure to press them while the screen is selected. You can press 'c' and capture a new pose any time. After quitting you will get a visual for the amount of error you had in your pose matching over time.

## Extra Notes

- The app deletes all previous files in the json and image directories in order to avoid confusion with file numbers and openpose overwriting data in json files.


## Demo

### Stick Figure Version

![000000000177](https://user-images.githubusercontent.com/25145128/43658034-76409af8-970c-11e8-966e-a55d85357a2e.png)

### Image Write Version

![000000000027 2](https://user-images.githubusercontent.com/25145128/43657908-f7a843d0-970b-11e8-9cb7-7d90935a6f01.png)
