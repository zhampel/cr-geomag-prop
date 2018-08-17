
import crprop


def test_version_exists():
    assert hasattr(crprop, '__version__')


def test_particle_utils_exists():
    assert hasattr(crprop, 'particle_utils')


def test_particle_utils_load_json_file_exists():
    assert hasattr(crprop, 'load_json_file')


def test_particle_utils_get_particle_props_exists():
    assert hasattr(crprop, 'get_particle_props')


def test_particle_utils_initial_buffers_exists():
    assert hasattr(crprop, 'initial_buffers')


def test_coord_utils_exists():
    assert hasattr(crprop, 'coord_utils')


def test_coord_utils_rotation_matrix_exists():
    assert hasattr(crprop, 'rotation_matrix')


def test_coord_utils_rotate_about_axis_exists():
    assert hasattr(crprop, 'rotate_about_axis')


def test_coord_utils_sph2cart_exists():
    assert hasattr(crprop, 'sph2cart')


def test_coord_utils_geodetic_to_geocentric_exists():
    assert hasattr(crprop, 'geodetic_to_geocentric')
