# kubewatch-python

A kubewatch-like application written in Python with Slack support.
Can be deployed with the Helm chart in the charts/ subfolder.


## Features

* Python asyncio
* Slack _"ChatOps"_ alerts
* Prometheus Metrics endpoint
* Helm Chart


## Requirements

* Python >= 3.7


### pip

* [asyncio](https://pypi.org/project/asyncio/)
* [requests](https://pypi.org/project/requests/)
* [kubernetes_asyncio](https://pypi.org/project/kubernetes_asyncio/)
* [prometheus_client](https://pypi.org/project/prometheus_client/)


### ENVVARs

* `SLACK_WEBHOOK` _(Slack Webook URL)_
* `CLUSTER` _(cluster name to show in Slack messages)_
* Custom Slack emoji `:k8s:` (Kubernetes icon)

You can configure the below resources via envvars with the following convention:

* Prefixed with *ENABLE_*
* Plural form of K8s resource
* Value: *true* or *false*

#### Example

**ENABLE_DAEMONSETS** or **ENABLE_INGRESSES**


## Watchable Resources

* ClusterRole
* ClusterRoleBinding
* ConfigMap _(namespaced, defaults to *default* namespace)_
* CronJob
* DaemonSet
* Deployment
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


## Prometheus

The Prometheus metrics endpoint is available at Port *8000*.

In addition to the basic Python metrics, there are these two which can be scraped:

* success_webhooks = Counter of how many times the Slack Webhook was successfully triggered
* failed_webhooks = Counter of how many times the Slack Webhook failed


## Notes

The first run will give you some history of events
