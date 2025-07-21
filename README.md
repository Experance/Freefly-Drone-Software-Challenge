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

5. Download `pymap3d` (this is for code converting meters to latitude/longitude) and `geopy` (for measuring distance between coords)

```bash
pip install pymap3d
pip install geopy
```

6. Now start the simulator (a separate window should pop up):

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

7. Run `main.py` in `~PX4-Autopilot/src/freefly_code` in a separate terminal.

```bash
cd ~PX4-Autopilot/src/freefly_code
python3 main.py
```

### 3. Screen Capture Video
A screen capture of my module controlling the drone can be found at this link: https://youtu.be/1DCSr6_9OyE.

### 4. Log
The log can be accessed online here: https://logs.px4.io/plot_app?log=5b2815de-1597-438c-bee4-fada2dfc86cf
and downloaded [here](log_6_2025-7-20-18-49-21.ulg)

This image from those logs shows the drone is flying to different waypoints correctly.
<img width="1343" height="885" alt="Pasted image 20250720192518" src="https://github.com/user-attachments/assets/6829dec5-0a14-45bd-9caf-0631b1c3eddf" />


Likewise, the fact that the altitude was not change after the initial going up to 5m and landing is confirmed by the following image: 
<img width="1306" height="696" alt="Pasted image 20250720192616" src="https://github.com/user-attachments/assets/c307b39a-91d3-404e-8a2d-52dd9b92ca5d" />


### 5. Considerations made in design
##### Failsafes
One of the major considerations I made while writing the module was for failsafes. What happens if battery starts running low and a user doesn't notice? What happens if the drone is flying too high and the user doesn't notice? These are all things that can easily be solved by failsafes.

Things that had failsafes:
- No flying above 400 feet (122 meters) so as to not break FAA drone altitude requirements
- No flying more than 500 meters away in a direction parallel to the earth (X or Y direction)
- When a Battery falls to 25%

For all the failsafes, the current mission would be paused and the drone would return to launch, land, and disarm.

##### Waypoint Delay
Another consideration I made had to do with waiting or going through the waypoints that had been set. What I decided on was that for the first waypoint, the drone would pause for a moment, since it would be the start of the foam dispensing. But then in subsequent waypoints that the drone went through, it would pass through, and not go to a complete stop (though it did still slow down some).

##### Compatibility
- Works with PX4-compatible drones (as long as mavsdk compatible and provide battery and position telemetry)
- Waypoints can be generated from CAD tools or exported, and due to the simplicity of the txt file, it will be very easy to create various paths that are desired

##### From Sim to Real Drone
Before going to a real drone, there needs to be more vigorous testing done on edge cases -- what happens when you get close to the limits set? What happens if you reach a certain battery level? What about the impact of temperature? All of these are major factors that are easy to forget about when in a simulator that could impact things like battery life, drone safety, and more.

Another major aspect to work on would be to start with very slow speeds when on a real drone. When in a simulator, speeds can certainly be set higher to see the impacts, but back in the real-world, it's important to start slow in the case that something goes wrong. In the same vein, in the sim, it is unnecessary to confirm the hardware is properly working and connected, but when on a real drone, it should be double checked that the battery is properly snug and plugged in, there are no lose parts, and so on.

##### Future Work
Some cool features that could be added in the future could be using the drone with a camera and having obstacle avoidance. Something else that could be done is doing multi-drone snchronized foam printing, kind of like how there are sychronized drone shows. These are various projects that could expand the capabilities of the current process.
