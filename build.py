from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin('pypi:pybuilder_aws_plugin')
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "random_pairs"
default_task = "publish"


@init
def set_properties(project):
    project.set_property("dir_source_main_python", "src/main")
    project.set_property("dir_source_unittest_python", "src/tests")
