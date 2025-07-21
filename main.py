
import asyncio
import pymap3d as pm
import geopy.distance
from mavsdk import System, mission, action
from mission_loader import load_waypoints


def localOffsetToGps(startLat, startLon, startAlt, north_m, east_m, down_m):
    lat, lon, alt = pm.enu2geodetic(
        east_m, north_m, -down_m,  # note: ENU ordering!
        startLat, startLon, startAlt
        
    )
    return lat, lon, alt
    

battery_low = False
too_far = False
too_high = False
drone = System() # drone object

async def monitor_battery():
    global battery_low
    global drone
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 25 or battery.time_remaining_s < 70:
            print("[Battery Monitor] Low battery detected: " + str(battery.remaining_percent) + "remaining")
            battery_low = True
            break
        # print("Current battery:" + str(battery.remaining_percent))
        await asyncio.sleep(3)  # check every second

async def is_within_geofence(start_lat, start_lon, max_radius_m):
    global too_far
    global drone
    async for position in drone.telemetry.position():
        distance = geopy.distance.distance((start_lat, start_lon), (position.latitude_deg, position.longitude_deg)).meters
        if (distance > max_radius_m): 
            print("Flown outside of allowed range")
            too_far = True
            break # only get the first value
       
        await asyncio.sleep(3)  # check every second

async def is_too_high():
    global too_high
    global drone
    async for pos_vel in drone.telemetry.position_velocity_ned():
        ned = pos_vel.position
        if (-ned.down_m >= 122): # 122 meters is 400 feet (FAA limits)
            too_high = True
            break

        await asyncio.sleep(3)  # check every second

async def run():
    global drone
    await drone.connect(system_address="udp://:14540") # async, so need to wait
    print("Loading Waypoints from file...")
    waypoints = load_waypoints(filepath="pattern.txt")


    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Arming...")
    try: 
        await drone.action.arm()
    except action.ActionError as e:
        print(f"Error: {e}")
        print("Cannot arm. Check that the drone has a home position and is healthy.")
        return


    async for position in drone.telemetry.position():
        start_latitude_deg = position.latitude_deg
        start_longitude_deg = position.longitude_deg
        start_absolute_alt = position.absolute_altitude_m
        break # only get the first value

    mission_items = []

    for i, waypoint in enumerate(waypoints):  # waypoint = [north, east, down] are positive values
        lat, lon, alt = localOffsetToGps(
            start_latitude_deg,
            start_longitude_deg,
            start_absolute_alt,
            waypoint.getNorth(), waypoint.getEast(), waypoint.getDown()
        )
        
        mission_items.append(mission.MissionItem(
            latitude_deg=lat,
            longitude_deg=lon,
            relative_altitude_m=alt - start_absolute_alt, 
            speed_m_s=3.0,
            is_fly_through=i != 0,
            gimbal_pitch_deg=0.0,
            gimbal_yaw_deg=0.0,
            camera_action=mission.MissionItem.CameraAction.NONE,
            loiter_time_s=0.0,
            camera_photo_interval_s=0.0,
            acceptance_radius_m=0.1,
            yaw_deg=0.0,
            camera_photo_distance_m=0.0,
            vehicle_action=mission.MissionItem.VehicleAction.NONE
        ))


    await drone.mission.upload_mission(mission.MissionPlan(mission_items=mission_items))

    

    
    battery_task = asyncio.ensure_future(monitor_battery()) # runs in parallel to teh run()
    geo_limit_task = asyncio.ensure_future(is_within_geofence(start_lat=start_latitude_deg, start_lon=start_longitude_deg, max_radius_m=500))
    height_limit_task = asyncio.ensure_future(is_too_high())

    print("Flying to target points...")

    try:
        await drone.mission.start_mission()
    except mission.MissionError as e:
        print(f"Error: {e}")

    async for missions in drone.mission.mission_progress():
         print(f"Number of missions (points) completed: {(int(missions.current) + 1)} / {int(missions.total)}")
         if (missions.current + 1 == missions.total):
            print("Mission Completed! Landing in 5 seconds.")
            battery_task.cancel()
            geo_limit_task.cancel()
            height_limit_task.cancel()
            break
         
         if battery_low:
            print("Mission Aborted due to low battery. Returning to launch...")
            await drone.mission.pause_mission()
            await drone.action.return_to_launch()
            battery_task.cancel()
            geo_limit_task.cancel()
            height_limit_task.cancel()
            break
         
         if too_far:
            print("Mission Aborted due to going outside of allowed range. Returning to launch...")
            await drone.mission.pause_mission()
            await drone.action.return_to_launch()
            battery_task.cancel()
            geo_limit_task.cancel()
            height_limit_task.cancel()
            break
         
         if too_high:
            print("Mission Aborted due to going too high. Returning to launch...")
            await drone.mission.pause_mission()
            await drone.action.return_to_launch()
            battery_task.cancel()
            geo_limit_task.cancel()
            height_limit_task.cancel()
            break
             
         
    
    geo_limit_task.cancel()
    await asyncio.sleep(5) # stay up for 5 seconds longer after mission is done

    print("Landing...")
    await drone.action.land()

    # Wait for landing to complete
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("Drone has landed.")
            break
        await asyncio.sleep(1)

    print("Disarming...")
    try: 
        await drone.action.disarm()
        print("Drone has disarmed")
    except action.ActionError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())

