import pytest

#from clikit.io import NullIO
from clikit.api.io.flags import DEBUG
from clikit.io import ConsoleIO
import pdb
import inspect
from poetry.core.packages.project_package import ProjectPackage
import sys
# print(sys.path)
# print(inspect.getmodule(ProjectPackage))
#pdb.set_trace()
from poetry.puzzle.provider import Provider as BaseProvider
from poetry.repositories import Pool
from poetry.repositories import Repository

from poetry.core.packages import Package
from poetry.mixology.failure import SolveFailure
# import poetry.mixology.version_solver as versionsolver
from poetry.mixology.version_solver import VersionSolver
from poetry.packages import DependencyPackage

def get_package(name, version):
    return Package(name, version)


def add_to_repo(repository, name, version, deps=None, python=None):
    package = Package(name, version)
    if python:
        package.python_versions = python

    if deps:
        for dep_name, dep_constraint in deps.items():
            package.add_dependency(dep_name, dep_constraint)

    repository.add_package(package)


def check_solver_result(
    root, provider, result=None, error=None, tries=None, locked=None, use_latest=None
):
    if locked is not None:
        locked = {k: DependencyPackage(l.to_dependency(), l) for k, l in locked.items()}

    #solver = versionsolver.VersionSolver(root, provider, locked=locked, use_latest=use_latest)
    solver = VersionSolver(root, provider, locked=locked, use_latest=use_latest)

    try:
        solution = solver.solve()
    except SolveFailure as e:
        if error:
            assert str(e) == error

            if tries is not None:
                assert solver.solution.attempted_solutions == tries

            return

        raise

    packages = {}
    for package in solution.packages:
        packages[package.name] = str(package.version)

    assert result == packages

    if tries is not None:
        assert solution.attempted_solutions == tries

class Provider(BaseProvider):
    def set_package_python_versions(self, python_versions):
        self._package.python_versions = python_versions
        self._python_constraint = self._package.python_constraint

def repo():
    return Repository()

def pool(repo):
    pool = Pool()
    pool.add_repository(repo)

    return pool

def root():
    return ProjectPackage("myapp", "0.0.0")

def provider(pool, root):
    outputstream = ConsoleIO()
    outputstream.output.set_verbosity(DEBUG)
    return Provider(root, pool, outputstream)

root = root()
root.add_dependency("a", "1.0.0")
root.add_dependency("b", "1.0.0")

repo = repo()
add_to_repo(repo, "a", "1.0.0", deps={"aa": "!=1.0.0", "ab": "1.0.0"})
add_to_repo(repo, "b", "1.0.0", deps={"ba": "1.0.0", "bb": "1.0.0"})
add_to_repo(repo, "aa", "1.0.0")
add_to_repo(repo, "aa", "2.0.0")
add_to_repo(repo, "ab", "1.0.0")
add_to_repo(repo, "ba", "1.0.0")
add_to_repo(repo, "bb", "1.0.0")

provider = provider(pool(repo), root)
# check_solver_result(
#     root,
#     provider,
#     {
#         "a": "1.0.0",
#         "aa": "1.0.0",
#         "aa": "2.0.0",
#         "ab": "1.0.0",
#         "b": "1.0.0",
#         "ba": "1.0.0",
#         "bb": "1.0.0",
#     },
# )


s = VersionSolver(root, provider)
s._init()
next = s._choose_package_version()
s._propagate(next)
print("clear")
s._clear()
#s._add_incompatibility(Incompatibility([Term(root_dependency, False)], RootCause()))
# s.solve()
#s._propagate(s._root.name)