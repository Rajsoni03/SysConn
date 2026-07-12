import psutil
import docker
from flask_restful import Resource


def _docker_stats():
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        running = sum(1 for c in containers if c.status == "running")
        return {
            "total": len(containers),
            "running": running,
            "stopped": len(containers) - running,
        }
    except Exception:
        return {"error": "Docker unavailable"}


class SystemStats(Resource):
    def get(self):
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "cpu": {
                "percent": cpu,
                "count": psutil.cpu_count(logical=True),
                "count_physical": psutil.cpu_count(logical=False),
            },
            "memory": {
                "total_mb": round(mem.total / 1024 ** 2, 1),
                "used_mb": round(mem.used / 1024 ** 2, 1),
                "available_mb": round(mem.available / 1024 ** 2, 1),
                "percent": mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / 1024 ** 3, 2),
                "used_gb": round(disk.used / 1024 ** 3, 2),
                "free_gb": round(disk.free / 1024 ** 3, 2),
                "percent": disk.percent,
            },
            "docker": _docker_stats(),
        }, 200
