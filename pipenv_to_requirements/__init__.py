# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

# pylint: disable=undefined-variable
if sys.version_info < (3, 0):

    def isstr(astring):
        return isinstance(astring, basestring)
else:

    def isstr(astring):
        return isinstance(astring, str)


# pylint: enable=undefined-variable

# pylint: disable=wrong-import-position
from pipenv.project import Project

# pylint: enable=wrong-import-position


def clean_version(pkg_name, pkg_info):
    if isstr(pkg_info):
        if pkg_info.strip() == "*":
            return pkg_name
        return "{}{}".format(pkg_name, pkg_info)
    if not pkg_info:
        return pkg_name
    version = pkg_info.get("version", "").strip()
    editable = pkg_info.get("editable", False)
    markers = pkg_info.get("markers", "").strip()
    extras = pkg_info.get("extras", [])
    git = pkg_info.get("git", "").strip()
    path = pkg_info.get("path", "").strip()
    if not editable:
        rstr = pkg_name
        if version and version != "*":
            rstr += version
    elif git:
        rstr = "-e git+" + git + "#egg=" + pkg_name
    else:
        rstr = "-e " + path
    if extras:
        rstr += "[{}]".format(', '.join([s.strip() for s in extras]))
    if markers:
        rstr += " ; " + markers
    return rstr


def formatPipenvEntryForRequirements(pkg_name, pkg_info):
    return clean_version(pkg_name, pkg_info["version"].strip()
                         if "version" in pkg_info else pkg_info)


def parse_pip_file(pipfile, section):
    return [clean_version(n, i) for n, i in pipfile.get(section, {}).items()]


def main():

    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: ")
        print("  pipenv-to-requirements [-f|--freeze]")
        print()
        print("Options:")
        print("  -f --freeze    Generate requirements*.txt with frozen versions")
        sys.exit(0)

    if "-f" in sys.argv or "--freeze" in sys.argv:
        pipfile = Project().lockfile_content
    else:
        # pylint: disable=protected-access
        pipfile = Project()._lockfile
        # pylint: enable=protected-access

    def_req = parse_pip_file(pipfile, "default")
    dev_req = parse_pip_file(pipfile, "develop")

    # Create pip-compatible dependency list
    def_req = [
        formatPipenvEntryForRequirements(n, i) for n, i in pipfile.get("default", {}).items()
    ]
    dev_req = [
        formatPipenvEntryForRequirements(n, i) for n, i in pipfile.get("develop", {}).items()
    ]

    intro = [
        "################################################################################",
        "# This requirements files has been automatically generated from `Pipfile` with",
        '# `pipenv-to-requirements`', '#', '#',
        '# This has been done to maintain backward compatibility with tools and services',
        '# that do not support `Pipfile` yet.', '#',
        "# Do NOT edit it directly, use `pipenv install [-d]` to modify `Pipfile` and",
        "# `Pipfile.lock` and then regenerate `requirements*.txt`.",
        "################################################################################", ""
    ]

    if def_req:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(intro + sorted(def_req)) + "\n")
        print("generated: requirements.txt")

    if dev_req:
        with open("requirements-dev.txt", "w") as f:
            f.write("\n".join(intro + sorted(dev_req)) + "\n")
        print("generated: requirements-dev.txt")
