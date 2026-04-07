from app.exceptions.business import BusinessException, AuthException, NotFoundException


def test_business_exception_fields():
    exc = BusinessException(code=123, message="oops")
    assert exc.code == 123
    assert exc.message == "oops"


def test_business_exception_subclasses():
    assert isinstance(AuthException(40100, "no login"), BusinessException)
    assert isinstance(NotFoundException(40400, "not found"), BusinessException)
