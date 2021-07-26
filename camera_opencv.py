import argparse
import cv2


def get_gstreamer_pipeline(sensor_id, height, width, framerate=25):
    gs_pipeline = 'nvarguscamerasrc sensor-id={} ! ' \
                  'video/x-raw(memory:NVMM), width=(int){}, height=(int){},' \
                  'format=(string)NV12, framerate=(fraction){}/1 ! nvvidconv ! ' \
                  'video/x-raw, format=(string)BGRx ! ' \
                  'videoconvert ! ' \
                  'video/x-raw, format=(string)BGR ! appsink'.format(sensor_id,
                                                                     width,
                                                                     height,
                                                                     framerate)
    return gs_pipeline


def show_camera(args):
    gstreamer_pipeline = get_gstreamer_pipeline(args.sensor_id, args.height, args.width, args.fps)
    print("GStreamer pipeline:", gstreamer_pipeline)

    # Pass the Gstreamer pipeline to OpenCV VideoCapture to start recording the video.
    cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            ret_val, img = cap.read()
            cv2.imshow("CSI Camera", img)

            # Stop execution pressing q
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show in screen CSI camera using GStreamer and OpenCV')
    parser.add_argument('--sensor_id', dest='sensor_id', type=int, default=0,
                        help='CSI interface id on the Jetson')
    parser.add_argument('--height', dest='height', type=int, default=360,
                        help='Height of the captured video')
    parser.add_argument('--width', dest='width', type=int, default=640,
                        help='width of the captured video')
    parser.add_argument('--fps', dest='fps', type=int, default=25,
                        help='FPS of captured video')
    args = parser.parse_args()
    show_camera(args)
