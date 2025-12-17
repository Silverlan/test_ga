import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(os.path.abspath(os.path.dirname(__file__))).parent.parent.parent.parent / "build_scripts"))
from scripts.shared import *

def main():
	from third_party import ninja
	ninja.main()

	build_config_tp = config.build_config_tp
	deps_dir = config.deps_dir
	generator = config.generator
	no_confirm = True # config.no_confirm
	no_sudo = True # config.no_sudo
	chdir_mkdir(deps_dir)

	# Custom env with ninja
	env = os.environ.copy()
	ninja_dir = str(Path(deps_dir) / "ninja")
	env["PATH"] = ninja_dir + os.pathsep + env.get("PATH", "")
	
	# Download
	os.chdir(deps_dir)
	commit_sha = "505c697d0abef5da2ff3be35aa4ea3687597c3e9" # v1.4.1
	gns_root = os.getcwd() +"/GameNetworkingSockets"
	#if not check_repository_commit(gns_root, commit_sha, "GameNetworkingSockets"): 
	if not Path(gns_root).is_dir():
		print_msg("GameNetworkingSockets not found. Downloading...")
		git_clone("https://github.com/ValveSoftware/GameNetworkingSockets.git")
		os.chdir("GameNetworkingSockets")
		reset_to_commit(commit_sha)

		os.chdir("../")
	os.chdir("GameNetworkingSockets")

	print_msg("Applying patch...")
	subprocess.run(["git","apply",os.path.dirname(os.path.abspath(__file__)) +"/GameNetworkingSockets.patch"],check=False,shell=True)

	if platform == "win32":
		gns_vcpkg_root = gns_root +"/vcpkg"
		if not Path(gns_vcpkg_root).is_dir():
			print_msg("vcpkg not found, downloading...")
			git_clone("https://github.com/Microsoft/vcpkg.git")

		os.chdir(gns_vcpkg_root)
		reset_to_commit("84bab45d415d22042bd0b9081aea57f362da3f35")
		os.chdir("..")
		subprocess.run([gns_vcpkg_root +"/bootstrap-vcpkg.bat","-disableMetrics"],check=True,shell=True)
		subprocess.run([gns_vcpkg_root +"/vcpkg","install","--triplet=x64-windows"],check=True,shell=True)

		# Build
		print_msg("Building GameNetworkingSockets...")
		mkdir("build",cd=True)
		cmake_configure_def_toolset("..","Ninja",["-DBUILD_EXAMPLES=OFF", "-DBUILD_TESTS=OFF", "-DUSE_STEAMWEBRTC=ON"], env=env)
		cmake_build("Release", env=env)
		os.chdir(deps_dir)
	else:
		print_msg("Installing required GameNetworkingSockets packages...")
		commands = [
			"apt install libssl-dev",
			"apt install libprotobuf-dev protobuf-compiler"
		]
		#if(not no_sudo):
		#	install_system_packages(commands, no_confirm)

		print_msg("Building GameNetworkingSockets...")
		mkdir("build",cd=True)
		subprocess.run(["cmake","-G","Ninja",".."], check=True, env=env)
		subprocess.run(["ninja"], check=True, env=env)

	copy_prebuilt_binaries(gns_root +"/build/src/", "GameNetworkingSockets")
	copy_prebuilt_binaries(gns_root +"/build/bin/", "GameNetworkingSockets")
	copy_prebuilt_headers(gns_root +"/include/", "GameNetworkingSockets")

if __name__ == "__main__":
	main()
