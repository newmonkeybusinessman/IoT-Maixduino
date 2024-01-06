# maixpy
import sensor, image, lcd
from Maix import GPIO
from fpioa_manager import *
# model detection
import KPU
# python std
import socket
import network
import utime
import json
from time import sleep


def log(*args, msg=None):
    if VERBOSITY:
        if msg is not None:
            print(msg, *args)
        else:
            print(*args)

def get_camera_sensor_handle():
    lcd.init(freq=CONNECTION_SPEED)
    sensor.reset()
    # NOTE: running istantly with `sensor.run(0)` may fail!
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000) # wait to take effects
    log("Camera setup done")
    return sensor

class DetectionModel:

    MODEL_PHYS_ADDR = 0x300000
    # values from: http://www.86x.org/cn-maixpy/cn.maixpy.sipeed.com/dev/en/libs/Maix/kpu.html
    MODEL_ANCHORS = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375,
                     9.01025)
    THRESHOLD = 0.5
    NMS_VALUE = 0.3
    ANCHOR_NUM = 5

    @staticmethod
    def load():
        modelObj = KPU.load(DetectionModel.MODEL_PHYS_ADDR)
        yolo2_model = KPU.init_yolo2(modelObj,
                                     DetectionModel.THRESHOLD,
                                     DetectionModel.NMS_VALUE,
                                     DetectionModel.ANCHOR_NUM,
                                     DetectionModel.MODEL_ANCHORS)
        log("Detection model loaded successfully")
        return yolo2_model, modelObj

def setup_network_connection_handle():

    # setup network card manually
    # INFO: https://wiki.sipeed.com/soft/maixpy/en/api_reference/builtin_py/fm.html (3.4.1 Instructions)
    # Based on the template: https://github.com/sipeed/MaixPy_scripts/blob/master/network/demo_esp32_read_adc.py
    fm.register(25,fm.fpioa.GPIOHS10)
    fm.register(8,fm.fpioa.GPIOHS11)
    fm.register(9,fm.fpioa.GPIOHS12)
    fm.register(28,fm.fpioa.GPIOHS13)
    fm.register(26,fm.fpioa.GPIOHS14)
    fm.register(27,fm.fpioa.GPIOHS15)

    nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12,
    mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)

    wifi = nic.scan()

    nic.isconnected()
    nic.connect(SSID, PASS)
    nic.isconnected()

    sock = socket.socket()
    sock.connect((SERVER_ADDR, PORT))
    log("Wifi handle created successfully")
    return sock

def send_face_count(sock, faceCount):
    data = {'headsCount': faceCount}
    json_data = json.dumps(data)
    request = (
        "POST /headsCount HTTP/1.1\r\n" +\
        "Host:" + SERVER_ADDR + ":" + str(PORT) +\
        "Host: localhost:3000\r\n" +\
        "Content-Type: application/json\r\n" +\
        "Content-Length: " + str(len(json_data)) + "\r\n" +\
        "\r\n" +\
        str(json_data) + "\r\n"
    )
    sock.send(request.encode('utf-8'))

def main():

    sensor = get_camera_sensor_handle()
    sock = setup_network_connection_handle()
    yolo2_model, modelObj = DetectionModel.load()
    log("Scaning started...")
    faceCount = 0

    # TODO: add break logic
    while True:
        img = sensor.snapshot()
        faces = KPU.run_yolo2(modelObj, img)
        if faces:
            faceCount = len(faces)
            for face in faces:
                yolo2_model = img.draw_rectangle(face.rect())
        else:
            faceCount = 0
        # TODO: add some input args to use display (default: turn off)
        lcd.display(img)

        send_face_count(sock, faceCount)

        sleep(PROBE_RATE)
        log(faceCount, msg="Current face count: ")

    # cleanup
    sock.close()
    nic.ifconfig()


if __name__ == "__main__":

    # H/W
    CONNECTION_SPEED = 15000000 # bits/s
    # wifi
    SSID = "Mi 9 SE"
    PASS = "3141592653"
    SERVER_ADDR = "192.168.163.69"
    PORT= 3000

    PROBE_RATE = 0.016
    VERBOSITY = True


    main()

