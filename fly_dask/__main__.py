# %%

from dask.distributed import Client
from dotenv import load_dotenv
from fly_dask import FlyMachineCluster
from fly_dask.sdk.constants import FlyRegion, MachineSize
import dask.array as da
import os

load_dotenv()

FLY_TOKEN = os.environ["FLY_TOKEN"]
if not FLY_TOKEN:
    raise ValueError("FLY_TOKEN is required")

cluster = FlyMachineCluster(
    "packyak-test",
    api_token=FLY_TOKEN,
    n_workers=1,
    cpus=8,
    memory_mb=16 * 1024,
    vm_size=MachineSize.PERFORMANCE_16X,
    image="registry.fly.io/packyak-test:test",
    region=FlyRegion.IAD,
)
client = Client(cluster)
print(f"Dashboard: {cluster.dashboard_link}")


# %%
arr = da.random.random((1000, 1000), chunks=(100, 100))
mean = arr.mean().compute()

print(mean)

# %%

client.close()
cluster.close()
