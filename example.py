import os
from dotenv import load_dotenv

from fly_dask.machine import FlyMachineCluster
from fly_dask.sdk.constants import FlyRegion, MachineSize

# Load environment variables
load_dotenv()

fly_token = os.getenv("FLY_TOKEN")
if fly_token is None:
    raise ValueError("FLY_TOKEN must be provided")

cluster = FlyMachineCluster(
    api_token=fly_token,
    app_name="fly-dask",
    region=FlyRegion.IAD,
    vm_size=MachineSize.DEDICATED_CPU_2X,
    image="flyio/dask:latest",
    memory_mb=2048,
    cpus=2,
    debug=True,
)

