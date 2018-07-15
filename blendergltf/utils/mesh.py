import mathutils.geometry


class AttributeData:
    def __init__(self, mesh):
        self.positions = PositionsData(mesh)
        self.normals = NormalsData(mesh)
        self.group = GroupsData(mesh)
        self.color_layers = [ColorsData(c) for c in mesh.vertex_colors]
        self.uv_layers = [UvsData(l) for l in mesh.uv_layers]
        self.triangle_sets = [
            IndicesData(mesh, i, triangulate=True) for i, _ in enumerate(mesh.materials)
        ]
        self.polygon_sets = [IndicesData(mesh, i) for i, _ in enumerate(mesh.materials)]


class CollectionData:
    def __init__(self, source, map_function):
        self.source = source
        self.iterator = (map_function(i) for i in source)

    def __len__(self):
        return len(self.source)


class PositionsData(CollectionData):
    def __init__(self, mesh):
        super().__init__(mesh.vertices, lambda v: v.co)


class GroupsData(CollectionData):
    def __init__(self, mesh):
        super().__init__(mesh.vertices, lambda v: v.groups)


class NormalsData(CollectionData):
    def __init__(self, mesh):
        mesh.calc_normals()
        super().__init__(mesh.vertices, lambda v: v.normal)


class ColorsData(CollectionData):
    #TODO: Address color space
    def __init__(self, colors):
        super().__init__(colors.data, lambda data: data.color)
        self.layer = colors


class UvsData(CollectionData):
    def __init__(self, uv_layer):
        super().__init__(uv_layer.data, lambda data: data.uv)
        self.layer = uv_layer


class IndicesData:
    def __init__(self, mesh, material_index, triangulate=False):
        self.mesh = mesh
        self.material = mesh.materials[material_index]
        self._faces = [f for f in mesh.polygons if f.material_index == material_index]
        if triangulate:
            self._len = sum([max(len(f.vertices) - 2, 1) for f in self._faces])
            self.iterator = self._create_iter()
        else:
            self._len = len(self._faces)
            self.iterator = (p for p in self._faces)

    def __len__(self):
        return self._len

    def _create_iter(self):
        for face in self._faces:
            vertices = face.vertices
            if len(vertices) < 3:
                continue
            elif len(vertices) > 3:
                coords = [self.mesh.vertices[i].co for i in vertices]
                triangles = mathutils.geometry.tessellate_polygon((coords,))
                for triangle in triangles:
                    yield [vertices[i] for i in triangle]
            else:
                yield list(vertices)


def extract_attributes(mesh):
    return AttributeData(mesh)
