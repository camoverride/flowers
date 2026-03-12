# Flowers

Display flowers 🌺


## Setup

- Get monitor dimensions with `xrandr | grep '*'`. Make sure they match the dimensions in `run_display.py`


- `git clone git@github.com:camoverride/flowers.git`
- `cd flowers`
<!-- - `python -m venv --system-site-packages .venv (system-site-packages so we get the picamera package.) -->
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `sudo apt-get install unclutter`


## Test

<!-- - `export DISPLAY=:0` -->
<!-- - `WAYLAND_DISPLAY=wayland-0 wlr-randr --output HDMI-A-1 --transform 270` -->
- `python run_display.py`


## Run in Production

Start a service with *systemd*. This will start the program when the computer starts and revive it when it dies. This is expected to run on a Raspberry Pi 5:

- `mkdir -p ~/.config/systemd/user`
- `cat display.service > ~/.config/systemd/user/display.service`

Start the service using the commands below:

- `systemctl --user daemon-reload`
- `systemctl --user enable display.service`
- `systemctl --user start display.service`

Start it on boot:

- `sudo loginctl enable-linger $(whoami)`

Get the logs:

- `journalctl --user -u display.service`
