# Freefly-Drone-Software-Challenge
## Foam Printer PX4 Module -- Python 

### 1. Setup Instructions (On Ubuntu, WSL)

1. Clone PX4-Autopilot:
```bash
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
```

2. Run the **ubuntu.sh** with no arguments (in a bash shell) to install everything:

```bash
./PX4-Autopilot/Tools/setup/ubuntu.sh
```

3. Add the folder with all the code into `src`. Below will make the folder as well as create the files necessary. You may already have the files and just add them manually instead of creating new. This folder will hold all the python code for the Drone Foam Printer.

```bash
cd ~/PX4-Autopilot/src
mkdir freefly_code
cd freefly_code

echo> mission_loader.py
echo> main.py
echo> pattern.txt
```

- The `pattern.txt` file is in the format of  X Y Z coordinates (in meters relative to home) X -> East, Y -> North, Z -> Down. An example is given below:
```txt
# X Y Z coordinates (in meters relative to home) +X -> East, +Y -> North, +Z -> Down
# draws a square
0 0 -5
5 0 -5
5 5 -5
0 5 -5
0 0 -5

```
- Comments can be added to the txt file by appending it with a `#`. These lines will not impact the program.

4. Make sure you have python installed. Check with `python3 --version` . Download `mavsdk` (you will need a python virtual environment):

```bash
python3 -m venv venv
source venv/bin/activate
pip install mavsdk
```

5. Download `pymap3d` (this is for code converting meters to latitude/longitude)

```bash
pip install pymap3d
```

5. Now start the simulator (a separate window should pop up):

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

6. Run `main.py` in `~PX4-Autopilot/src/freefly_code` in a separate terminal.

```bash
cd ~PX4-Autopilot/src/freefly_code
python3 main.py
```

### 3. Screen Capture Video
A screen capture of my module controlling the drone is provided: 

### 4. Log
The log can be accessed online here: https://logs.px4.io/plot_app?log=5b2815de-1597-438c-bee4-fada2dfc86cf
And downloaded here: 

This image from those logs shows the drone is flying to different waypoints correctly.
![[Pasted image 20250720192518.png]]


Likewise, the fact that the altitude was not change after the initial going up to 5m and landing is confirmed: ![[Pasted image 20250720192616.png]]


### 5. Considerations made in design



