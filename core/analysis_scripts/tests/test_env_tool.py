from pathlib import Path
from platform import python_version_tuple
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory

from analysis_scripts import VirtualEnvManager
import pytest


def install_helper(tmp):
    tmp_path = Path(tmp)
    env_path = tmp_path / "env"
    env = VirtualEnvManager(env_path)
    env.create_env()
    name = "freanalysis_clouds"
    url = "https://github.com/noaa-gfdl/analysis-scripts.git"
    run(["git", "clone", url, str(tmp_path / "scripts")])
    output = env.install_package(str(tmp_path / "scripts" / "core" / "analysis_scripts"))
    output = env.install_package(str(tmp_path / "scripts" / "core" / "figure_tools"))
    output = env.install_package(str(tmp_path / "scripts" / "user-analysis-scripts" / name))
    return tmp_path, env_path, env, name


def test_create_env():
    with TemporaryDirectory() as tmp:
        env_path = Path(tmp) / "env"
        env = VirtualEnvManager(env_path)
        env.create_env()
        assert env_path.is_dir()
        test_string = "hello, world"
        assert env._execute([f'echo "{test_string}"',])[0] == test_string


def test_install_plugin():
    with TemporaryDirectory() as tmp:
        tmp_path, env_path, env, name = install_helper(tmp)
        version = ".".join(python_version_tuple()[:2])
        plugin_path = env_path / "lib" / f"python{version}" / "site-packages" / name
        assert plugin_path.is_dir()


def test_list_plugins():
    with TemporaryDirectory() as tmp:
        tmp_path, env_path, env, name = install_helper(tmp)
        plugins = env.list_plugins()
        assert plugins[0] == name


def test_run_plugin():
    with TemporaryDirectory() as tmp:
        tmp_path, env_path, env, name = install_helper(tmp)
        catalog = tmp_path / "fake-catalog"
        with pytest.raises(CalledProcessError) as err:
            env.run_analysis_plugin(name, str(catalog), ".", config={"a": "b"})
        for line in err._excinfo[1].output.decode("utf-8").split("\n"):
            if f"No such file or directory: '{str(catalog)}'" in line:
                return
        assert False
