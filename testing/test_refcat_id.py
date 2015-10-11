from astropy.io import fits
import pytest

from ngts_transmission.watching import get_refcat_id, NoAutoguider


@pytest.fixture
def ref_id():
    return 10101


@pytest.fixture
def with_key(tmpdir, ref_id):
    fname = str(tmpdir.join('test.fits'))
    phdu = fits.PrimaryHDU()
    phdu.header['AGREFIMG'] = ref_id
    phdu.writeto(fname)
    return fname


@pytest.fixture
def without_key(tmpdir):
    fname = str(tmpdir.join('test.fits'))
    phdu = fits.PrimaryHDU()
    assert 'AGREFIMG' not in phdu.header
    phdu.writeto(fname)
    return fname


def test_get_refcat_id(with_key, ref_id):
    ref_image_id = get_refcat_id(with_key)
    assert ref_image_id == ref_id


def test_get_refcat_id_throws_correct_exception_when_key_missing(without_key):
    with pytest.raises(NoAutoguider) as err:
        get_refcat_id(without_key)

    assert 'not autoguided' in str(err).lower()
