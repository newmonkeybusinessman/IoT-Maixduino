# Introduction

Internet of Things on Maixduino board.


# Prerequisites

#### Node JS packages (***server***)
```
npm install express
```

#### Python packages (***board control***)
```
pip install -r requirements.txt
```

#### Image + detection model
> Download image from:
https://dl.sipeed.com/shareURL/MAIX/MaixPy/release/master/maixpy_v0.6.2_85_g23d09fbcc \
(e.g. **maixpy_v0.6.2_85_g23d09fbcc_with_lvgl.bin**)

> Download detection model from: https://dl.sipeed.com/shareURL/MAIX/MaixPy/model \
(select:  **face_model_at_0x300000.kfpkg**)

# Tasks

### Goals
- [x] setup detection model on the board to get number of human faces visible in the camera sensor
  - [x] setup communication server to be running on the host machine
  - [x] setup communication client to be running on maixduino board
  - [x] create logic to run detection face model
- [ ] ...


# Run face detection
### Setup

#### Prepare image
Create **flash-list.json** file with below contents:
```
{
  "version": "0.1.0",
  "files": [
    {
      "address": 0,
      "bin": "maixpy_v0.6.2_85_g23d09fbcc_with_lvgl.bin",
      "sha256Prefix": true
    },
    {
      "address": 0x300000,
      "bin": "facedetect.kmodel",
      "sha256Prefix": false
    }
  ]
}

```
> Note: different method to add face model to the board is to put it onto external SD storage

> Note: pay attention to the image size - currently available images don't execeed 0x150000
(half of 0x300000), however, it might change considering there hasn't been yet released even
version 1.0 of the S/W for maixduino


Create folder **maixpy_v0.6.2_85_g23d09fbcc_with_lvgl** with below structure:
```
maixpy_v0.6.2_85_g23d09fbcc_with_lvgl
|
+----facedetect.kmodel
|
+----flash-list.json
|
+----maixpy_v0.6.2_85_g23d09fbcc_with_lvgl.bin

```


```
zip -rj maixpy_v0.6.2_85_g23d09fbcc_with_lvgl.kfpkg maixpy_v0.6.2_85_g23d09fbcc_with_lvgl
```

#### Flash image
To flash the image use **kflash** tool.
```
kflash --port /dev/ttyUSB0 -b 1500000 --Slow --Board maixduino maixpy_v0.6.2_85_g23d09fbcc_with_lvgl.kfpkg
```
> Note: a different port might be used

#### Check connection with the board
After flashing you should be able to establish connection with the board.
```
mpremote ls
```
> lists contents from board's fs root


### Run
#### Run host server
```
node server/server.js
google-chrome server/index.html
```

#### Start sensor data acquistion
```
mpremote run scripts/maixduino_client.py
```

# Additional information + references

The project is primarily done based on micropython - MaixPY module (board control + board client).
API links:
1. multimedia
- https://wiki.sipeed.com/soft/maixpy/en/api_reference/machine_vision/sensor.html
- https://wiki.sipeed.com/soft/maixpy/en/api_reference/machine_vision/image/image.html
- https://wiki.sipeed.com/soft/maixpy/en/api_reference/machine_vision/lcd.html
2. communication
- https://wiki.sipeed.com/soft/maixpy/en/api_reference/builtin_py/fm.html
3. detection
- https://wiki.sipeed.com/soft/maixpy/en/api_reference/Maix/kpu.html

Additionally, host server is created in Node JS.


Maixduino board: https://wiki.sipeed.com/hardware/en/maix/maixpy_develop_kit_board/maix_duino.html


> To work with the board extra MaixPY IDE might be used:
https://dl.sipeed.com/shareURL/MAIX/MaixPy/ide/v0.2.5


# Tips + useful info

1. | **Scripts execution** | For the time of 2023/24 some scripts are not being executed or are
not being executed the way they should using **ampy** tool. If facing some Python weird issues
try using **mpremote** or **MaixIDE**.

2. | **Memory Reflash** | Depending on version of the binary available some older `0.3^` and newer
`0.6^` uses different default scripts that are getting executed. (plus available maixduino S/W's
FS distinguish between '/' and '//' - two files '/flash/boot.py' and '/flash//boot.py' can coexist
and yet one of them cannot be accessed). In such cases - of using multiple images over many tries
or simply somehow creating some unreachable files in the FS just **reflash the entire
flash memory**.
