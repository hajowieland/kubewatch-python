# kubewatch-python

A kubewatch-like app written in Python with Slack support.


## Requirements


* Python >= 3.3
* pip: [asyncio](https://pypi.org/project/asyncio/), [requests](https://pypi.org/project/requests/), [kubernetes_asyncio](https://pypi.org/project/kubernetes_asyncio/)
* ENVVARs:
  * `SLACK_WEBHOOK` _(Slack Webook URL)_
  * `CLUSTER` _(cluster name to show in Slack messages)_
* Custom Slack emoji `:k8s:` (Kubernetes icon)


## Watched Resources

* ClusterRole
* ClusterRoleBinding
* ConfigMap _(namespaced, defaults to *default* namespace)_
* CronJob
* DaemonSet
* Deployment
* // Endpoint
* Ingress
* Job
* LimitRange
* NetworkPolicy
* Node
* PersistentVolume
* PersistentVolumeClaim
* Pod
* PodDisruptionBudget
* PodTemplate
* PodSecurityPolicy
* ReplicaSet
* ResourceQuota
* Role
* RoleBinding
* Secret
* Service
* ServiceAccount
* StatefulSet


## Notes

The first run will give you some history of events