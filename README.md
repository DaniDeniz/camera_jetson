# Camera Jetson
Guide for retrieving images from CSI cameras using GStreamer on Jetson devices

The official documentation about using GStreamer on Jetson devices can be found [here](https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%20Linux%20Driver%20Package%20Development%20Guide/accelerated_gstreamer.html). 

## Installation
Firstly, install GStreamer and its dependencies on the Jetson.

```bash
sudo add-apt-repository universe
sudo add-apt-repository multiverse
sudo apt-get update
sudo apt-get install gstreamer1.0-tools gstreamer1.0-alsa \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav
sudo apt-get install libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libgstreamer-plugins-good1.0-dev \
  libgstreamer-plugins-bad1.0-dev
```

## What is GStreamer?

Once this is installed, we can start working with GStreamer. GStreamer is a library for managing media. 

We can use GStreamer on the linux terminal with the following command: *gst-launch-1.0*.

GStreamer manages media using pipelines. The elements of the pipeline are splitted by ! 

It is recommended to read/watch the following tutorials about how gstreamer works on the Jetson.
* [Official documentation](https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%20Linux%20Driver%20Package%20Development%20Guide/accelerated_gstreamer.html)
* [Paul McWhorter: Understanding GStreamer for absolute beginners](https://www.youtube.com/watch?v=_yU1kfcC6rY) Long video, but very well explained.
* [Jetson Hacks](https://www.jetsonhacks.com/2019/04/02/jetson-nano-raspberry-pi-camera/) - Blog

## Read images from CSI cameras
Now, we will go directly to the pipelines needed to obtain the video from CSI cameras on Jetson devices.

### CSI cameras from Linux
We start running GStreamer on the linux terminal.

```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! "video/x-raw(memory:NVMM), width=(int)640, height=(int)360, format=(string)NV12, framerate=(fraction)25/1" !  nvvidconv ! "video/x-raw, format=(string)BGRx" ! nvvidconv ! omxh264enc ! "video/x-h264,stream-format=(string)byte-stream" ! h264parse ! qtmux ! filesink location=test.mp4
```
* **nvarguscamerasrc**: NVIDIA plugin for reading CSI cameras
  * sensor-id: It is the id of the CSI interface
* **video/x-raw(memory:NVMM)** This part of the pipeline set how the video received from the camera is configured
  * width, height
  * format: NV12 # CSI cameras usually outputs the frames in this format
  * framerate: desired framerate, it is always set as a fraction, for example for getting 30 fps, you should set 30/1 frames
* **nvvidconv**: Nvidia video format and scaling module for processing the video
* **video/x-raw, format=(string)BGRx**: Setting this configuration after **nvvidconv** tells the **nvvidconv** what conversion needs to carry out.
  * This converts the video from NV12 to BGRx (x is a dummy channel)
* **omxh264enc**: This is h264 hardware video encoder, this is useful when saving the recorded video into a file or if we send it over the network.
* **video/x-h264,stream-format=(string)byte-stream**: Now, this tells GStreamer that the video is in h264 format.
* **qtmux**: Merges audio and video data
* **filesink location=test.mp4**: The pipelines always need to end with a sink. In this case, a file sink means that the video will
be saved into a file.
  
After running the previous command for a couple of seconds, a test.mp4 should be created with the video recording.

Other example is showing directly on screen what is the camera seeing. The main change that we need to do to the pipeline is the sink.

```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)640, height=(int)360'  ! nvvidconv flip-method=0 ! autovideoconvert ! xvimagesink 
```
* **nvvidconv flip-method=0**: If you need to rotate or flip the image, you can change the flip-method ([documentation](https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%20Linux%20Driver%20Package%20Development%20Guide/accelerated_gstreamer.html#wwpID0E0VH0HA))
* **autovideoconvert**: Automatically converts the video to what it needs the following element in the pipeline
* **xvimagesink**: It is a sink that shows the video on a screen.

### CSI cameras on Python / C++
OpenCV supports GStreamer, for this reason we could build a similar pipeline to the previous showed and get the images to process them on a Python or C++ script.

An **IMPORTANT** prerequisite is to build OpenCV with GSTREAMER support. Regularly, the default installation does not have this support. For this reason, you need to build OpenCV from source. 

I recommend you to install the following libraries and follow this [guide](https://galaktyk.medium.com/how-to-build-opencv-with-gstreamer-b11668fa09c). Anyway, you can first run the code before checking if it you need to build OpenCV from source or not.

```bash
sudo apt-get install -y  libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libjpeg-dev libavresample-dev; sudo apt autoremove -y 
sudo apt-get install -y libwebp-dev libtiff-dev; sudo apt autoremove -y
sudo apt-get install libgtk2.0-dev pkc-config -y
```
Additionally, it is also recommended to create a python virtual environment and install numpy==1.19.1 before building OpenCV. Then, build OpenCV following the previous guide using this new environment.
The pipeline for OpenCV will be the following:
```python
gs_pipeline = 'nvarguscamerasrc sensor-id=0 ! ' \
              'video/x-raw(memory:NVMM), width=(int)640, height=(int)360,' \
              'format=(string)NV12, framerate=(fraction)25/1 ! nvvidconv ! ' \
              'video/x-raw, format=(string)BGRx ! ' \
              'videoconvert ! ' \
              'video/x-raw, format=(string)BGR ! appsink'
```

In short, the pipeline is very similiar, we only add the **videoconvert** element to convert the images to BGR format, which is format preferred by OpenCV. 
And finally, the sink is an **appsink**

For further details run and check the [camera_opencv.py](camera_opencv.py) file.

Running this, you should watch the video from the camera on your screen display.

```bash
python camera_opencv.py --sensor_id 0 --width 1920 --height 1080 --fps 25
```