from cx_Freeze import setup, Executable

executables = [Executable('чернь проекта.py',
targetName='dokitale.exe',
base='Win32GUI',
icon='icon.ico')]


includes = ['pygame', 'sys', 'os', 'random', 'math']

zip_include_packages = ['pygame', 'sys', 'os', 'random', 'math']

include_files = ['data']

options = {
'build_exe': {
'include_msvcr': True,
'includes': includes,
'zip_include_packages': zip_include_packages,
'build_exe': 'build_windows',
'include_files': include_files,
}
}

setup(name='чернь проекта.py',
version='0.0.1',
description='Артём гей',
executables=executables,
options=options)