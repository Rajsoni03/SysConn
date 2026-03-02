import os
import docker
from pathlib import Path
from docker.types import Mount, DriverConfig
from config.settings import DOCKER_SDK_DOCKERFILE_PATH, DOCKER_SDK_IMAGE


try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"[ Warning ] Docker not available: {e}")
    docker_client = None

class SDKBuilderService:
    def __init__(self, data: dict, shared_data: dict):
        self.data = data
        self.shared_data = shared_data

    def validate(self) -> bool:
        # Params Check
        required_params = ['build_number', "platform"]
        for param in required_params:
            if param not in self.data:
                self.shared_data['msg'] = f"Missing required parameter: {param}"
                print(self.shared_data['msg'])
                return False

        # Basic validation to check if Docker is available
        if docker_client is None:
            self.shared_data['msg'] = "Docker is not available. Please ensure Docker is installed and running."
            print(self.shared_data['msg'])
            return False
        
        # Check if Dockerfile path exists
        if not DOCKER_SDK_DOCKERFILE_PATH.exists():
            self.shared_data['msg'] = f"Dockerfile not found at {DOCKER_SDK_DOCKERFILE_PATH}"
            print(self.shared_data['msg'])
            return False
        
        # Check if same name container is already running
        try:
            docker_container_name = f"sdk_builder_{self.data['platform']}_{self.data['build_number']}"
            existing_container = docker_client.containers.get(docker_container_name)
            if existing_container.status == "running":
                self.shared_data['msg'] = f"A container named '{docker_container_name}' is already running. Please stop it before starting a new one."
                print(self.shared_data['msg'])
                return False
        except docker.errors.NotFound:
            pass  # No existing container, safe to proceed
        
        return True

    def docker_build(self, force_rebuild=False, no_cache=False) -> bool:
        
        # check docker image is available or not
        if not force_rebuild:
            try:
                docker_client.images.get("sdk_image")
                print("SDK Docker image already exists.")
                return True
            except docker.errors.ImageNotFound:
                print("SDK Docker image not found. Building a new one...")
        else:
            print("Force rebuild enabled. Building SDK Docker image...")
        
        # delete existing volume if force_rebuild is True to ensure a clean build environment
        if force_rebuild:
            try:                
                volume = docker_client.volumes.get("sdk_artifacts")
                volume.remove(force=True)
                print("Existing Docker volume 'sdk_artifacts' removed.")
            except docker.errors.NotFound:
                print("No existing Docker volume 'sdk_artifacts' found. Continuing with build.")
            except Exception as e:
                print(f"Warning: Failed to remove existing Docker volume: {e}")
                print("Continuing with build process...")

        # get host user id
        try:
            host_uid = os.getuid()
        except Exception as e:
            host_uid = 1000

        # Build Docker image and stream logs live
        try:
            build_output = docker.APIClient().build(
                path=str(DOCKER_SDK_DOCKERFILE_PATH),
                tag=DOCKER_SDK_IMAGE,
                rm=True,
                buildargs={
                    "HOST_UID": str(host_uid)
                },
                decode=True,
                nocache=no_cache
            )
            for chunk in build_output:
                if 'stream' in chunk:
                    print(chunk['stream'], end='')
                elif 'error' in chunk:
                    print(chunk['error'])
            
            # check if image is built successfully
            try:
                docker_client.images.get(DOCKER_SDK_IMAGE)
                print("SDK Docker image built successfully.")
            except docker.errors.ImageNotFound:
                self.shared_data['msg'] = "Failed to build SDK Docker image."
                print(self.shared_data['msg'])
                return False
            return True
        except Exception as e:
            self.shared_data['msg'] = f"Failed to build SDK Docker image: {e}"
            print(self.shared_data['msg'])
            return False

    def docker_run(self, container_name="sdk_builder_container", cmd_args=[]) -> bool:
        # check if image is available
        try:
            docker_client.images.get(DOCKER_SDK_IMAGE)
            print("SDK Docker image found. Running the container...")
        except docker.errors.ImageNotFound:
            self.shared_data['msg'] = "SDK Docker image not found. Please build it first."
            print(self.shared_data['msg'])
            return False

        # Example NFS mount using docker.types.Mount
        nfs_server = "raj.dhcp.ti.com"
        nfs_share = "/home/raj/nas/sdk_artifacts"

        mounts = [
                Mount(
                    target="/nas",
                    source="sdk_artifacts",
                    type="volume",
                    driver_config=DriverConfig(
                        name="local",
                        options={
                            "type": "nfs",
                            "device": f":{nfs_share}",
                            "o": f"addr={nfs_server},vers=4,soft"
                        }
                    )
                )
        ]

        # Run the container and stream logs live
        try:
            container = docker_client.containers.run(
                DOCKER_SDK_IMAGE,
                command=cmd_args,
                tty=True,
                name=container_name,
                detach=True,
                mounts=mounts
            )
            print(f"SDK Docker container started with ID: {container.id}")
            print("--- Live container logs ---")
            for log in container.logs(stream=True, follow=True):
                print(log.decode('utf-8'), end='')
            print("--- Container finished ---")
            # Remove container after logs are streamed
            try:
                container.remove()
                print(f"Container {container.id} removed.")
            except Exception as e:
                print(f"Warning: Failed to remove container: {e}")
            return True
        except Exception as e:
            self.shared_data['msg'] = f"Failed to run SDK Docker container: {e}"
            print(self.shared_data['msg'])
            return False
        

if __name__ == "__main__":
    # Example usage
    data = {}
    shared_data = {}
    sdk_builder = SDKBuilderService(data, shared_data)
    build_success = sdk_builder.docker_build(force_rebuild=True, no_cache=False)
    
    if build_success:    
        run_success = False
        # Example command-line arguments for entrypoint script
        cmd_args = [
            "--INDIA_MIRROR=true",
            "--VERSION=01_00_00",
            "--TAG=",
            "--EXPORT_FS=true",
            "--PLATFORM=j721s2"
        ]

        run_success = sdk_builder.docker_run("sdk_builder_j721s2", cmd_args) 
         
    print(f"SDK Build Success: {build_success}, SDK Run Success: {run_success}")