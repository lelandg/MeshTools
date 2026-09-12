"""Regression coverage for solidification using real Trimesh geometry."""
import unittest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import open3d
import trimesh

from MeshTools.mesh_tools import MeshTools
from MeshTools.mesh_manipulation import MeshManipulation
from MeshTools.viewport_3d import ThreeDViewport


def square():
    return trimesh.Trimesh(
        vertices=[[0, 0, 1], [2, 0, 1], [2, 2, 1], [0, 2, 1]],
        faces=[[0, 1, 2], [0, 2, 3]],
        vertex_colors=[[255, 0, 0, 255], [0, 255, 0, 255],
                       [0, 0, 255, 255], [255, 255, 0, 255]],
        process=False,
    )


def ring():
    vertices = [[-2, -2, 1], [2, -2, 1], [2, 2, 1], [-2, 2, 1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]
    faces = []
    for a in range(4):
        b = (a + 1) % 4
        faces.extend([[a, b, b + 4], [a, b + 4, a + 4]])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


class MeshTopologyTests(unittest.TestCase):
    def assert_closed(self, mesh):
        self.assertTrue(mesh.is_watertight)
        self.assertTrue(mesh.is_winding_consistent)
        self.assertTrue(np.all(np.bincount(mesh.edges_unique_inverse) == 2))
        self.assertTrue(np.all(mesh.unique_faces()))
        self.assertTrue(np.all(mesh.area_faces > 0))

    def test_square_flat_back(self):
        original = square()
        result = MeshTools(original, verbose=False).solidify_mesh_with_flat_back(
            flat_back_depth=0.0)
        self.assert_closed(result)
        self.assertEqual(len(result.faces), 12)
        self.assertAlmostEqual(result.volume, 4)
        np.testing.assert_array_equal(original.vertices, square().vertices)
        for vertex, color in zip(result.vertices, result.visual.vertex_colors):
            index = np.where(np.all(original.vertices[:, :2] == vertex[:2], axis=1))[0][0]
            np.testing.assert_array_equal(color, original.visual.vertex_colors[index])

    def test_square_mirror(self):
        original = square()
        result = MeshTools(original, verbose=False).add_mirror_mesh(original)
        self.assert_closed(result)
        self.assertEqual(len(result.faces), 12)
        self.assertAlmostEqual(result.volume, 8)

    def test_hole_boundary_stays_open_through_solid(self):
        for operation in ('flat', 'mirror'):
            with self.subTest(operation=operation):
                original = ring()
                tool = MeshTools(original, verbose=False)
                result = (tool.solidify_mesh_with_flat_back(flat_back_depth=0)
                          if operation == 'flat' else tool.add_mirror_mesh(original))
                self.assert_closed(result)
                self.assertEqual(len(result.faces), 32)
                self.assertEqual(result.euler_number, 0)
                self.assertAlmostEqual(result.volume, 12 if operation == 'flat' else 24)

    def test_closed_mesh_has_no_boundary_walls(self):
        original = trimesh.creation.box()
        original.apply_translation([0, 0, 2])
        tool = MeshTools(original, verbose=False)
        flat = tool.solidify_mesh_with_flat_back()
        self.assert_closed(flat)
        np.testing.assert_array_equal(flat.vertices, original.vertices)
        np.testing.assert_array_equal(flat.faces, original.faces)
        mirrored = tool.add_mirror_mesh(original)
        self.assert_closed(mirrored)
        self.assertEqual(len(mirrored.faces), 2 * len(original.faces))
        self.assertAlmostEqual(mirrored.volume, 2 * original.volume)

    def test_boundary_touching_back_plane_has_no_degenerate_walls(self):
        for operation in ('flat', 'mirror'):
            with self.subTest(operation=operation):
                original = square()
                original.vertices[:2, 2] = 0
                tool = MeshTools(original, verbose=False)
                result = (tool.solidify_mesh_with_flat_back(flat_back_depth=0)
                          if operation == 'flat' else tool.add_mirror_mesh(original))
                self.assert_closed(result)
                self.assertGreater(result.volume, 0)

    def test_fix_mesh_removes_duplicate_face_mask(self):
        original = trimesh.creation.box()
        original.faces = np.vstack([original.faces, original.faces[0]])
        result = MeshTools(original, verbose=False).fix_mesh()
        self.assertEqual(len(result.faces), 12)
        self.assert_closed(result)


class ViewportMeshTests(unittest.TestCase):
    @patch('MeshTools.viewport_3d.MeasurementGrid')
    def test_load_mesh_rebinds_rotation_to_current_mesh(self, grid):
        viewport = ThreeDViewport.__new__(ThreeDViewport)
        viewport.viewer = MagicMock()
        viewport.background_color = [0.2, 0.2, 0.2]
        viewport.mesh_manipulator = MeshManipulation(viewport.viewer, None)
        first = open3d.geometry.TriangleMesh.create_box()
        second = open3d.geometry.TriangleMesh.create_box().translate([10, 0, 0])
        with patch('builtins.print'):
            for mesh in (first, second):
                viewport.load_mesh(mesh)
                self.assertIs(viewport.mesh_manipulator.mesh, mesh)
                before = np.asarray(mesh.vertices).copy()
                viewport.rotate_left(45)
                self.assertFalse(np.allclose(before, np.asarray(mesh.vertices)))
                np.testing.assert_allclose(
                    viewport.mesh_manipulator.mesh_center, mesh.get_center())

    def test_invalid_replacement_preserves_previous_mesh_and_raises(self):
        viewport = ThreeDViewport.__new__(ThreeDViewport)
        viewport.viewer = MagicMock()
        previous = open3d.geometry.TriangleMesh.create_box()
        viewport.mesh = previous
        viewport.custom_labels = ['previous']
        viewport.mesh_file = 'previous.ply'
        with self.assertRaises(ValueError), self.assertLogs('MeshTools.viewport_3d', level='ERROR'):
            viewport.load_mesh(open3d.geometry.TriangleMesh())
        self.assertIs(viewport.mesh, previous)
        self.assertEqual(viewport.custom_labels, ['previous'])
        self.assertEqual(viewport.mesh_file, 'previous.ply')

    def test_stl_export_round_trip(self):
        viewport = ThreeDViewport.__new__(ThreeDViewport)
        viewport.mesh = open3d.geometry.TriangleMesh.create_box()
        with tempfile.TemporaryDirectory() as directory, patch('builtins.print'):
            path = Path(directory) / 'box.stl'
            viewport.export_mesh_as_stl(str(path))
            result = open3d.io.read_triangle_mesh(str(path))
            self.assertFalse(result.is_empty())
            self.assertEqual(len(result.triangles), 12)

    def test_export_failure_reaches_caller(self):
        viewport = ThreeDViewport.__new__(ThreeDViewport)
        viewport.mesh = open3d.geometry.TriangleMesh.create_box()
        for method in (viewport.export_mesh_as_obj, viewport.export_mesh_as_stl):
            with self.subTest(method=method.__name__):
                with patch('MeshTools.viewport_3d.open3d.io.write_triangle_mesh', return_value=False):
                    with self.assertRaises(OSError), self.assertLogs('MeshTools.viewport_3d', level='ERROR'):
                        method('failed.stl')

    def test_empty_export_reaches_caller(self):
        viewport = ThreeDViewport.__new__(ThreeDViewport)
        viewport.mesh = None
        with self.assertRaises(ValueError), self.assertLogs('MeshTools.viewport_3d', level='ERROR'):
            viewport.export_mesh_as_obj('empty.obj')


if __name__ == '__main__':
    unittest.main()
