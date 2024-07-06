# Agora-Python-SDK installer
from urllib.request import urlretrieve
import platform
import shutil
import zipfile
import site
import sys
import os

# compatible with Windows and macOS
# try to install it manually from https://docs.agora.io/en/sdks
# Requirements
# - Python 3.6+
# - Xcode (macOS)
# - Visual Studio 2017+ with C++14+ (Windows)
#   ~ MSVC
#   ~ ATL
#   ~ Compilation SDK

agora_github = 'https://github.com/AgoraIO-Community/Agora-Python-SDK/archive/refs/heads/master.zip'
agora_path = 'Agora-Python-SDK' # do not change
sdk_path = 'Agora_Native_SDK'
zip_path = f'{sdk_path}.zip'
agora_modules = {'agorartc.py'}
############
sitepackages = site.getsitepackages()[-1]
############

windows_url = 'http://download.agora.io/sdk/release/Agora_Native_SDK_for_Windows_v3_1_2_FULL.zip'
mac_url = 'http://download.agora.io/sdk/release/Agora_Native_SDK_for_Mac_v3_1_2_FULL.zip'
linux_url = ''


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    sys.stderr.write('\r~ downloading %d KBs' % (readsofar // 1024))
    sys.stderr.flush()
    if totalsize > 0 and readsofar >= totalsize:
        sys.stderr.write('\n')

def shell_commands():
    files = set(os.listdir(agora_path)).union({'build'})
    code = os.system(f'cd {agora_path} && {sys.executable} setup.py build_ext --inplace')
    if code != 0:
        sys.exit(code)
    agora_modules.update(set(os.listdir(agora_path)) - files)
    print('modules:', agora_modules)
    shutil.copytree(agora_path, sitepackages, ignore=lambda x, y: set(y).difference(agora_modules), dirs_exist_ok=True)

def installer_for_linux():
    raise NotImplementedError

def installer_for_windows():
    if not os.path.exists(zip_path):
        print('~ downloading %r.' % windows_url)
        urlretrieve(windows_url, zip_path, reporthook)
    if not os.path.exists(sdk_path):
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(sdk_path)
    lib = {
        '32bit': f'{sdk_path}/Agora_Native_SDK_for_Windows_FULL/libs/x86',
        '64bit': f'{sdk_path}/Agora_Native_SDK_for_Windows_FULL/libs/x86_64'
    }.get(platform.architecture()[0]).replace('/', '\\')
    for module in os.listdir(lib):
        agora_modules.add(module)
        shutil.copy(os.path.join(lib, module), agora_path)


def installer_for_darwin():
    if not os.path.exists(zip_path):
        print('~ downloading %r.' % mac_url)
        urlretrieve(mac_url, zip_path, reporthook)
    if not os.path.exists(sdk_path):
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(sdk_path)
    lib = f'{sdk_path}/Agora_Native_SDK_for_Mac_FULL/libs'
    for module in os.listdir(lib):
        agora_modules.add(module)
    shutil.copytree(lib, agora_path, dirs_exist_ok=True)

def check_requirements():
    # c++ 14
    ...

def prepare_installation():
    if not os.path.exists(f'{agora_path}.zip'):
        print('~ downloading', f'{agora_github}...')
        urlretrieve(agora_github, f'{agora_path}.zip', reporthook)
    if not os.path.exists(agora_path):
        with zipfile.ZipFile(f'{agora_path}.zip') as zf:
            zf.extractall(agora_path)
        print('~ %r dir was created.' % agora_path)
        path = os.path.join(agora_path, f"{agora_path}-master")
        shutil.copytree(path, agora_path, dirs_exist_ok=True)
        shutil.rmtree(path)

def remove_intallation_files():
    os.remove(zip_path)
    os.remove(f'{agora_path}.zip')
    shutil.rmtree(agora_path)
    shutil.rmtree(sdk_path)
    print('agorartc installed!')
    sys.exit(0)


installer = {
    'Windows': installer_for_windows,
    #'Linux': installer_for_linux,
    'Darwin': installer_for_darwin
}.get(platform.system())

if installer is None:
    raise SystemError('agora-python-sdk is not compatible with %r operating system.' % platform.system())


def main():
    check_requirements()
    prepare_installation()
    installer()
    shell_commands()
    remove_intallation_files()


if __name__ == '__main__':
    main()
