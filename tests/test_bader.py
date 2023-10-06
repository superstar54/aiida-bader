from aiida import orm, load_profile

load_profile()


def test_bader():
    bader_code = orm.load_code("bader@localhost")
