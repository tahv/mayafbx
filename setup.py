import setuptools
import ast


def get_version(filepath):
    with open(filepath, "r") as openfile:
        root = ast.parse(openfile.read())
    version = None
    for statement in root.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    return ast.literal_eval(statement.value)
    assert version, "Could not determine version"
    return version


with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="mayafbx",
    version=get_version("mayafbx/__init__.py"),
    description="Python wrapper for the FBX plugin of Autodesk Maya.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thibaud Gambier",
    license="MIT",
    url="https://github.com/tahv/mayafbx",
    packages=setuptools.find_packages(include=['mayafbx'])
)
