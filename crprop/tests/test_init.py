
import crprop


def test_version_exists():
    assert hasattr(crprop, '__version__')


def test_particle_utils_exists():
    assert hasattr(crprop, 'particle_utils')


def test_particle_utils_rotation_matrix_exists():
    assert hasattr(crprop, 'rotation_matrix')


def test_particle_utils_rotate_about_axis_exists():
    assert hasattr(crprop, 'rotate_about_axis')


def test_particle_utils_sph2cart_exists():
    assert hasattr(crprop, 'sph2cart')


def test_particle_utils_initial_buffers_exists():
    assert hasattr(crprop, 'initial_buffers')
