from aiida import orm


def test_bader():
    bader_code = orm.load_code("bader@localhost")
