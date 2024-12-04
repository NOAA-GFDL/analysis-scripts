from pytest import raises

from analysis_scripts import AnalysisScript


def test_no_init():
    #The constructor is not overridden.
    with raises(NotImplementedError):
        class FakeAnalysisScript(AnalysisScript):
            pass
        _ = FakeAnalysisScript()


def test_no_requires():
    #The requires function is not overridden.
    with raises(NotImplementedError):
        class FakeAnalysisScript(AnalysisScript):
            def __init__(self):
                pass
        _ = FakeAnalysisScript().requires()


def test_no_run_analysis():
    #The requires function is not overridden.
    with raises(NotImplementedError):
        class FakeAnalysisScript(AnalysisScript):
            def __init__(self):
                pass
        _ = FakeAnalysisScript().run_analysis("fake catalog", "fake png directory")
