# Fake P3D classes. We don't really need to use the real classes as all we need are the values stored in the data struct.
# At its base they are just ordered triples/quads

print("imported pandaModules")
class Point3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class VBase3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class Vec3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class Vec4:

    def __init__(self, x, y, z, h):
        self.x = x
        self.y = y
        self.z = z
        self.h = h
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ", " + str(self.h) + ")"