# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import subprocess
import platform
import os
import os.path
import stat
from distutils.spawn import find_executable

from .common import CommonEnvironment
from ..package_info import PackageInfo, FileInfo


class RpmEnvironment(CommonEnvironment):
    executable = 'rpm'

    @staticmethod
    def get_list():
        command_args = ['rpm', '-qa', '--queryformat', '%{name}\t%{version}-%{release}\n']
        data = subprocess.check_output(command_args)
        line_list = data.split('\n')
        result = []

        for line in line_list:
            split_line = filter(len, line.split())
            if len(split_line) == 2:
                info = PackageInfo()
                info.package = split_line[0]
                info.version = split_line[1]
                result.append(info)

        return result

    @staticmethod
    def is_file(path):
        if path[0] != '/':
            return False

        try:
            mode = os.stat(path).st_mode
        except OSError:
            return False

        if stat.S_ISDIR(mode):
            return False

        return True

    @staticmethod
    def get_files_for_package(package_name):
        command_args = ['rpm', '-ql', package_name]
        data = subprocess.check_output(command_args)
        lines = data.rstrip().split('\n')
        files = filter(RpmEnvironment.is_file, lines)
        return [FileInfo(path) for path in files]

    @staticmethod
    def get_os_string():
        dist = platform.dist()
        return dist[0] + '_' + dist[1]

    @staticmethod
    def is_installed():
        return find_executable(RpmEnvironment.executable)
