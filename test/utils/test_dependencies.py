from utils.dependencies import CheckJwt

def test_check_jwt():
    assert CheckJwt() is not None