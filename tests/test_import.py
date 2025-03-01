def test_import():
    import feedrattler  # noqa: F401
    import feedrattler.cli  # noqa: F401
    import feedrattler.convert  # noqa: F401
    import feedrattler.utils  # noqa: F401


def test_version():
    import feedrattler

    print(feedrattler.__version__)
