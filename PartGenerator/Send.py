import matplotlib.pyplot as plt

from onshapeInterface import ProcessUrl, PartStudios, BlobElement
import json
from PartGenerator import Request
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import Math3d as math3d
import numpy as np

def check_triad_in_hole(triad, cylinder):
    for point in triad:
        in_c = math3d.is_within_cylinder(cylinder, point, 1e-2)
        if not in_c:
            return False
    return True

if __name__ == "__main__":
    # Generate the geometry & build into json
    builder = Request.RequestBuilder()

    prism1 = Request.Prism("1", Request.BooleanType.ADD)
    prism1.origin = [0,0,0]
    prism1.dimensions = [100, 200, 300]
    builder.add_request(prism1)

    prism2 = Request.Prism("2", Request.BooleanType.SUBTRACT)
    prism2.origin = [90,50,150]
    prism2.dimensions = [100, 200, 300]
    builder.add_request(prism2)

    sphere1 = Request.Sphere("1", boolean_type=Request.BooleanType.SUBTRACT, diameter=100, origin=[100, 0, 0])
    builder.add_request(sphere1)

    # # #
    hole1 = Request.Hole("1", Request.BooleanType.SUBTRACT)
    hole1.origin = [-300,75,280]
    hole1.axis = [1,0,0]
    hole1.diameter = 30
    hole1.depth = 600
    builder.add_request(hole1)
    # # #
    hole2 = Request.Hole("2", Request.BooleanType.SUBTRACT)
    hole2.origin = [-40,100,200]
    hole2.axis = [1,0,0]
    hole2.diameter = 50
    hole2.depth = 300
    builder.add_request(hole2)

    json_debug_url = ProcessUrl.OnshapeUrl("https://cad.onshape.com/documents/c3b4576ef97b70b3e09ba2f0/w/75bec76c270d0cb4899d9ce4/e/1e160786c96002332ab0abbf")
    json_url = ProcessUrl.OnshapeUrl("https://cad.onshape.com/documents/c3b4576ef97b70b3e09ba2f0/w/75bec76c270d0cb4899d9ce4/e/da7f3abe19b2d9b235ec0ffe")
    part_url = ProcessUrl.OnshapeUrl("https://cad.onshape.com/documents/c3b4576ef97b70b3e09ba2f0/w/75bec76c270d0cb4899d9ce4/e/2a5362fe0e6cb33b327a98de")

    # Send the json
    name = "aaa"
    json = json.dumps(builder.full_request)
    uploadBlobElement = BlobElement.UploadBlobElement(json_url)
    uploadBlobElement.file = json
    uploadBlobElement.encodedFilename = name + ".json"
    uploadBlobElement.update_file()

    # Readable format within onshape
    uploadBlobElement = BlobElement.UploadBlobElement(json_debug_url)
    uploadBlobElement.encodedFilename = name + "_json.txt"
    uploadBlobElement.file = json
    uploadBlobElement.update_file()

    # Rereieve the stl
    getStl = PartStudios.GetStl(part_url)
    getStl.send_request()
    getStl.get_response("received.stl")

    # Plot
    figure = pyplot.figure()
    axes = figure.add_subplot(projection='3d')

    your_mesh = mesh.Mesh.from_file('received.stl')
    points = your_mesh.points
    x, y, z = (your_mesh.x, your_mesh.y, your_mesh.z)
    vectors = your_mesh.vectors

    hole_vectors = []
    other_vectors = []
    for triad in vectors:
        in_c1 = check_triad_in_hole(triad, hole1)
        in_c2 = check_triad_in_hole(triad, hole2)
        if in_c2 or in_c1:
            hole_vectors.append(triad)
        else:
            other_vectors.append(triad)
    hole_vectors = np.array(hole_vectors)
    other_vectors = np.array(other_vectors)

    # plt.scatter(x, y, z)
    poly_holes = mplot3d.art3d.Poly3DCollection(hole_vectors)
    poly_holes.set_facecolor((0, 0.5, 0.50, 0.95))
    axes.add_collection3d(poly_holes)

    poly_other = mplot3d.art3d.Poly3DCollection(other_vectors)
    poly_other.set_facecolor((0.5, 0.5, 0, 0.30))
    axes.add_collection3d(poly_other)
    # axes.add_collection3d(mplot3d.art3d.Poly3DCollection(other_vectors))

    scale = your_mesh.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)
    # axes.autoscale(True)

    pyplot.show()