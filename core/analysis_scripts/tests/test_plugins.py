from pytest import raises

from analysis_scripts import available_plugins, plugin_requirements, run_plugin, \
                             UnknownPluginError


def test_no_plugins():
    """No valid plugins are installed."""
    assert available_plugins() == []


def test_invalid_plugin_requirements():
    """An invalid plugin name is passed in to plugin_requirements."""
    with raises(UnknownPluginError):
        _ = plugin_requirements("fake_plugin")


def test_invalid_run_plugin():
    """An invalid plugin name is passed in to run_plugin."""
    with raises(UnknownPluginError):
        _ = run_plugin("fake_plugin", "fake_catalog.json", "fake_png_directory")
