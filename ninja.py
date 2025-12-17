import os, sys
from pathlib import Path
import stat

sys.path.insert(0, str(Path(os.path.abspath(os.path.dirname(__file__))).parent.parent.parent.parent / "build_scripts"))
from scripts.shared import *

def main():
	build_config_tp = config.build_config_tp
	deps_dir = config.deps_dir
	generator = config.generator
	chdir_mkdir(deps_dir)
	
	# ninja
	os.chdir(deps_dir)
	ninja_root = deps_dir +"/ninja"
	if platform == "linux":
		ninja_executable_name = "ninja"
	else:
		ninja_executable_name = "ninja.exe"
	if not Path(ninja_root).is_dir():
		mkdir("ninja",cd=True)
		print_msg("Downloading ninja...")
		os.chdir(ninja_root)
		if platform == "linux":
			http_extract("https://github.com/ninja-build/ninja/releases/download/v1.11.1/ninja-linux.zip")
			st = os.stat('ninja')
			os.chmod('ninja', st.st_mode | stat.S_IEXEC)
		else:
			http_extract("https://github.com/ninja-build/ninja/releases/download/v1.11.1/ninja-win.zip")

if __name__ == "__main__":
	main()
