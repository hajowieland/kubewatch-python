#!/usr/bin/env python3

### TODO:
#
# - Watch only specific events (Pod only for RestartPhase, deletion, etc)
# - Add Resource specific details (like PodIP, etc.)
# - Get API and version and to not hardcode
# - List resources to monitor in a map to enable/disable specific ones
# - only list configmaps of specific namespaces
###


import os
import sys
import requests
import asyncio
from kubernetes_asyncio import client, config, watch
from prometheus_client import start_http_server, Counter

try:  
    webhook_url = os.environ["SLACK_WEBHOOK"]
    clustername = os.environ["CLUSTER"]
except KeyError: 
    print("Please set the required environment variables")
    sys.exit(1)

# Build taskmap of all resources configuration from envvars
taskmap = {}
try:
    taskmap['clusterroles'] = os.getenv('ENABLE_CLUSTERROLES', 'false')
    taskmap['clusterrolebindings'] = os.getenv('ENABLE_CLUSTERROLEBINDINGS', 'false')
    taskmap['configmaps'] = os.getenv('ENABLE_CONFIGMAPS', 'false')
    taskmap['cronjobs'] = os.getenv('ENABLE_CRONJOBS', 'false')
    taskmap['daemonsets'] = os.getenv('ENABLE_DAEMONSETS', 'true')
    taskmap['deployments'] = os.getenv('ENABLE_DEPLOYMENTS', 'true')
    taskmap['ingresses'] = os.getenv('ENABLE_INGRESSES', 'true')
    taskmap['jobs'] = os.getenv('ENABLE_JOBS', 'false')
    taskmap['limitranges'] = os.getenv('ENABLE_LIMITRANGES', 'false')
    taskmap['networkpolicies'] = os.getenv('ENABLE_NETWORKPOLICIES', 'false')
    taskmap['nodes'] = os.getenv('ENABLE_NODES', 'true')
    taskmap['pods'] = os.getenv('ENABLE_PODS', 'true')
    taskmap['podsecuritypolicies'] = os.getenv('ENABLE_PODSECURITYPOLICIES', 'false')
    taskmap['poddisruptionbudgets'] = os.getenv('ENABLE_PODDISRUPTIONBUDGETS', 'false')
    taskmap['podtemplates'] = os.getenv('ENABLE_PODTEMPLATES', 'false')
    taskmap['persistenvolumes'] = os.getenv('ENABLE_PERSISTENTVOLUMES', 'false')
    taskmap['persistentvolumeclaims'] = os.getenv('ENABLE_PERSISTENTVOLUMECLAIMS', 'false')
    taskmap['replicasets'] = os.getenv('ENABLE_REPLICASETS', 'false')
    taskmap['resoucequotas'] = os.getenv('ENABLE_RESOURCEQUOTAS', 'false')
    taskmap['roles'] = os.getenv('ENABLE_ROLES', 'false')
    taskmap['rolebindings'] = os.getenv('ENABLE_ROLEBINDINGS', 'false')
    taskmap['services'] = os.getenv('ENABLE_SERVICE', 'true')
    taskmap['serviceaccounts'] = os.getenv('ENABLE_SERVICEACCOUNTS', 'false')
    taskmap['secrets'] = os.getenv('ENABLE_SECRETS', 'false')
    taskmap['statefulsets'] = os.getenv('ENABLE_STATEFULSETS', 'false')
except KeyError:
    print("Plese set environment variables")
    sys.exit(1)

# Build tasklist of only the enabled resources
tasklist = []
for key, value in taskmap.items():
    if value == 'true':
        tasklist.append(key)
    else:
        continue

# Prometheus Counter
success_webhooks = Counter('success_webhooks', 'Counter of how many times the Slack Webhook was successfully triggered')
failed_webhooks = Counter('failed_webhooks', 'Counter of how many times the Slack Webhook failed')


# Slack message
async def slack(eventtype,eventkind,eventname,eventns, **kwargs):
    # eventnodename = kwargs.get('eventnodename', None)
    eventmap = { "ADDED": ":sparkle:", "DELETED": ":x:", "MODIFIED": ":part_alternation_mark:"}
    eventtypenew = str()
    # activehost = configuration.Configuration().host
    for event in eventmap:
        if eventtype == event:
            eventtypenew = eventmap.get(event)
    json_data = {
                "text": ":k8s: *[" + clustername + "]*",
                "attachments": [{
                    "author_name": eventtypenew,
                    # "author_link": activehost,
                    "author_icon": "https://i.imgur.com/HOOjN0U.png",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "fields": [
                    {
                        "title": "Event",
                        "value": eventtype,
                        "short": "true"
                    },
                    {
                        "title": "Object",
                        "value": eventkind,
                        "short": "true"
                    },
                    {
                        "title": "Name",
                        "value": eventname,
                        "short": "true"
                    },
                    {
                        "title": "Namespace",
                        "value": eventns,
                        "short": "true"
                    }
                    ]
                }]
    }
    response = requests.post(
                            webhook_url,
                            json=json_data,
                            headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        success_webhooks.inc(1)
    if response.status_code != 200:
        failed_webhooks.inc(1)
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


# Resource watch methods

async def clusterroles():
    v1rbac = client.RbacAuthorizationV1Api()
    async with watch.Watch().stream(v1rbac.list_cluster_role) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def clusterrolebindings():
    v1rbac = client.RbacAuthorizationV1Api()

    async with watch.Watch().stream(v1rbac.list_cluster_role_binding) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def configmaps():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_namespaced_config_map('default')) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def cronjobs():
    v1batch = client.BatchV1beta1Api()
    async with watch.Watch().stream(v1batch.list_cron_job_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def daemonsets():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_daemon_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def deployments():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_deployment_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


# async def endpoints():
#     v1 = client.CoreV1Api()
#     async with watch.Watch().stream(v1.list_endpoints_for_all_namespaces) as stream:
#         async for event in stream:
#             print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
#             await slack(eventtype=event['type'],
#                         eventkind=event['object'].kind,
#                         eventname=event['object'].metadata.name,
#                         eventns=event['object'].metadata.namespace)


async def ingresses():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_ingress_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def jobs():
    v1batch = client.BatchV1Api()
    async with watch.Watch().stream(v1batch.list_job_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def limitranges():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_limit_range_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def networkpolicies():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_network_policy_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def nodes():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_node) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def pods():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_pod_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (
            event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace,
                        eventnodename=event['object'].spec.node_name)


async def poddisruptionbudgets():
    v1policy = client.PolicyV1beta1Api()
    async with watch.Watch().stream(v1policy.list_pod_disruption_budget_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (
            event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace,
                        eventnodename=event['object'].spec.node_name)


async def podsecuritypolicies():
    v1policy = client.PolicyV1beta1Api()
    async with watch.Watch().stream(v1policy.list_pod_security_policy) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (
            event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace,
                        eventnodename=event['object'].spec.node_name)


async def podtemplates():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_pod_template_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (
            event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace,
                        eventnodename=event['object'].spec.node_name)


async def persistenvolumes():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_persistent_volume) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def persistentvolumeclaims():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_persistent_volume_claim_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def replicasets():
    v1apps = client.AppsV1Api()
    async with watch.Watch().stream(v1apps.list_replica_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def resourcequotas():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_resource_quota_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def roles():
    v1rbac = client.RbacAuthorizationV1Api()
    async with watch.Watch().stream(v1rbac.list_role_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def rolebindings():
    v1rbac = client.RbacAuthorizationV1Api()
    async with watch.Watch().stream(v1rbac.list_role_binding_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def secrets():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_secret_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def services():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_service_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def serviceaccounts():
    v1 = client.CoreV1Api()
    async with watch.Watch().stream(v1.list_service_account_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


async def statefulsets():
    v1apps = client.AppsV1Api()
    async with watch.Watch().stream(v1apps.list_stateful_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],
                        eventkind=event['object'].kind,
                        eventname=event['object'].metadata.name,
                        eventns=event['object'].metadata.namespace)


# async def events():
#     v1 = client.CoreV1Api()
#     async with watch.Watch().stream(v1.list_event_for_all_namespaces) as stream:
#         async for event in stream:
#             print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
#             await slack(eventtype=event['type'],
#             eventkind=event['object'].kind,
#             eventname=event['object'].metadata.name,
#             eventns=event['object'].metadata.namespace)


def main():
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(config.load_kube_config())
    config.load_incluster_config()

    # Start Prometheus HTTP Endpoint for exposing metrics
    start_http_server(8000)

    # Build tasks list of enabled resources
    tasks = []
    for resource in tasklist:
        # possibles = globals().copy()
        # possibles.update(locals())
        # method = possibles.get(resource)
        # tasks.append(asyncio.ensure_future(method()))
        task = asyncio.ensure_future(globals()[resource]())
        tasks.append(task)

    # Start the loop
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    main()
