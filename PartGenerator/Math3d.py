import Request
import numpy as np
import matplotlib.pyplot as plt
def is_within_cylinder(cylinder: Request.Hole, point: np.array, tolerance):
    # first, check within depth. project onto central axis
    # then, check within radius. distance from projection on to central axis
    origin = np.array(cylinder.origin)
    depth = cylinder.depth
    axis = np.array(cylinder.axis)
    axis = axis / np.linalg.norm(axis)
    end = origin + depth * axis

    projection_onto_axis = np.dot(point - origin, axis) * axis + origin
    if np.dot(axis, projection_onto_axis - end) > 0 + tolerance:
        # print("end")
        return False
    if np.dot(axis, projection_onto_axis - origin) < 0 - tolerance:
        # print("orig")
        return False

    distance_from_projection = np.linalg.norm(point - projection_onto_axis)
    # print(distance_from_projection)
    if distance_from_projection > cylinder.diameter / 2.0 + tolerance:
        # print("diam")
        return False
    return True

def check_triad_in_hole(triad, cylinder):
    for point in triad:
        in_c = is_within_cylinder(cylinder, point, 1e-2)
        if not in_c:
            return False
    return True

def orientation_to_axis(orientation: np.array):
    return np.array([1,1,1])

if __name__ == "__main__":

    point = [100. ,   124.148, 193.53]
    hole2 = Request.Hole("2", Request.BooleanType.SUBTRACT)
    hole2.origin = [-40,100,200]
    hole2.axis = [1,0,0]
    hole2.diameter = 50
    hole2.depth = 300
    print(is_within_cylinder(hole2, point, 1e-5))

    # cylinder = Request.Hole("1", Request.BooleanType.ADD,
    #                         axis=[0,1,1],
    #                         diameter=40,
    #                         depth=30,
    #                         origin=[0,0,0])
    # xs = []
    # ys = []
    # zs = []
    # for x in range(-100, 100, 3):
    #     for y in range(-100, 100, 3):
    #         for z in range(-100, 100, 3):
    #             point = [x, y, z]
    #             if is_within_cylinder(cylinder, point, 1):
    #                 xs.append(x)
    #                 ys.append(y)
    #                 zs.append(z)
    # fig = plt.figure()
    # ax = fig.add_subplot(projection='3d')
    # ax.scatter(xs, ys, zs)
    # plt.show()
    # print(is_within_cylinder(cylinder, [10,10 ,199], 1e-5))