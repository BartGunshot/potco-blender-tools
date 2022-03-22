# Fake P3D classes. We don't really need to use the real classes as all we need are the values stored in the data struct.
# At its base they are just ordered triples/quads

class Vec3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class Vec4(Vec3):

    def __init__(self, x, y, z, h):
        Vec3.__init__(self, x, y, z)
        self.h = h
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ", " + str(self.h) + ")"

# Aliases
VBase3 = Vec3
Point3 = Vec3
