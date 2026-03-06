from fastapi import FastAPI
import uvicorn
from kubernetes import client, config
import os

app = FastAPI(title='Lobster K8s Copilot API')

# Load K8s config
try:
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()
except Exception as e:
    print(f'Warning: Could not load K8s config: {e}')

@app.get('/')
async def root():
    return {'message': 'Lobster K8s Copilot API is running'}

@app.get('/api/v1/cluster/status')
async def get_cluster_status():
    return {'status': 'connected', 'clusters': ['local-dev']}

@app.get('/api/v1/cluster/pods')
async def list_pods():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pod_list = []
    for i in pods.items:
        pod_list.append({
            'name': i.metadata.name,
            'namespace': i.metadata.namespace,
            'status': i.status.phase,
            'ip': i.status.pod_ip
        })
    return {'pods': pod_list}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
