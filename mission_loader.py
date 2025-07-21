"""This loads the waypoints from misson_loader.py"""

def load_waypoints(filepath):
    waypoints = []
    # loop through data in filepath (expected txt)
    with open(filepath, 'r') as txt:
        for line in txt:
            if (line.strip()[0:1] == '#' or line.isspace()): #ignores comments
                continue

            print("Waypoint Loaded:  " + line)
            waypoints.append(Location(line.split()))

    return waypoints
        

class Location:
        def __init__(self, coords):
            self.x = coords[0]
            self.y = coords[1]
            self.z = coords[2]

        def getEast(self):
            return int(self.x)
        
        def getNorth(self):
            return int(self.y)
        
        def getDown(self):
            return int(self.z)
             




