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
import json
import asyncio
from kubernetes_asyncio import client, config, watch
#from kubernetes.client import configuration

try:  
   webhook_url = os.environ["SLACK_WEBHOOK"]
   clustername = os.environ["CLUSTER"]
except KeyError: 
   print("Please set the environment variables")
   sys.exit(1)


async def slack(eventtype,eventkind,eventname,eventns, **kwargs):
    # eventnodename = kwargs.get('eventnodename', None)
    eventmap = { "ADDED": ":sparkle:", "DELETED": ":x:", "MODIFIED": ":part_alternation_mark:"}
    eventtypenew = str()
    #activehost = configuration.Configuration().host
    for event in eventmap:
        if eventtype == event:
            eventtypenew = eventmap.get(event)
    json_data = {
                        "text": ":k8s: *[" + clustername + "]*",
                        "attachments": [
                        {
                            "author_name": eventtypenew,
                            #"author_link": activehost,
                            #"author_icon": "https://i.imgur.com/HOOjN0U.png",
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
                        }
                        ]
                    }
    response = requests.post(
    webhook_url,
    json=json_data,
    headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


async def clusterrole():
    v1rbac = client.RbacAuthorizationV1Api()

    async with watch.Watch().stream(v1rbac.list_cluster_role) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def clusterrolebinding():
    v1rbac = client.RbacAuthorizationV1Api()

    async with watch.Watch().stream(v1rbac.list_cluster_role_binding) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)



async def configmap():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_namespaced_config_map('default')) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def cronjob():
    v1batch = client.BatchV1beta1Api()

    async with watch.Watch().stream(v1batch.list_cron_job_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def daemonset():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_daemon_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)

async def deployment():
    v1ext = client.ExtensionsV1beta1Api()

    async with watch.Watch().stream(v1ext.list_deployment_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


# async def endpoint():
#     v1 = client.CoreV1Api()

#     async with watch.Watch().stream(v1.list_endpoints_for_all_namespaces) as stream:
#         async for event in stream:
#             print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
#             await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def ingress():
    v1ext = client.ExtensionsV1beta1Api()

    async with watch.Watch().stream(v1ext.list_ingress_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def job():
   v1batch = client.BatchV1Api()

   async with watch.Watch().stream(v1batch.list_job_for_all_namespaces) as stream:
       async for event in stream:
           print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
           await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def limitrange():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_limit_range_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def networkpolicy():
    v1ext = client.ExtensionsV1beta1Api()

    async with watch.Watch().stream(v1ext.list_network_policy_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def node():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_node) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def pod():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_pod_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace,eventnodename=event['object'].spec.node_name)


async def poddisruptionbudget():
    v1policy = client.PolicyV1beta1Api()

    async with watch.Watch().stream(v1policy.list_pod_disruption_budget_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace,eventnodename=event['object'].spec.node_name)


async def podsecuritypolicy():
    v1policy = client.PolicyV1beta1Api()

    async with watch.Watch().stream(v1policy.list_pod_security_policy) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace,eventnodename=event['object'].spec.node_name)



async def podtemplate():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_pod_template_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace,eventnodename=event['object'].spec.node_name)


async def pv():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_persistent_volume) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def pvc():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_persistent_volume_claim_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def replicaset():
    v1apps = client.AppsV1Api()

    async with watch.Watch().stream(v1apps.list_replica_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def resourcequota():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_resource_quota_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def role():
    v1rbac = client.RbacAuthorizationV1Api()

    async with watch.Watch().stream(v1rbac.list_role_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def rolebinding():
    v1rbac = client.RbacAuthorizationV1Api()

    async with watch.Watch().stream(v1rbac.list_role_binding_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def secret():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_secret_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)
       

async def service():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_service_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def serviceaccount():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_service_account_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def statefulset():
    v1apps = client.AppsV1Api()

    async with watch.Watch().stream(v1apps.list_stateful_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


# async def event():
#     v1 = client.CoreV1Api()

#     async with watch.Watch().stream(v1.list_event_for_all_namespaces) as stream:
#         async for event in stream:
#             print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
#             await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(config.load_kube_config())
    tasks = [
        asyncio.ensure_future(clusterrole()),
        asyncio.ensure_future(clusterrolebinding()),
        asyncio.ensure_future(configmap()),
        asyncio.ensure_future(cronjob()),
        asyncio.ensure_future(daemonset()),
        asyncio.ensure_future(deployment()),
        # asyncio.ensure_future(endpoint()),
        asyncio.ensure_future(ingress()),
        asyncio.ensure_future(job()),
        asyncio.ensure_future(limitrange()),
        asyncio.ensure_future(networkpolicy()),
        asyncio.ensure_future(node()),
        asyncio.ensure_future(pod()),
        asyncio.ensure_future(poddisruptionbudget()),
        asyncio.ensure_future(podtemplate()),
        asyncio.ensure_future(podsecuritypolicy()),
        asyncio.ensure_future(pv()),
        asyncio.ensure_future(pvc()),
        asyncio.ensure_future(replicaset()),
        asyncio.ensure_future(resourcequota()),
        asyncio.ensure_future(role()),
        asyncio.ensure_future(rolebinding()),
        asyncio.ensure_future(secret()),
        asyncio.ensure_future(service()),
        asyncio.ensure_future(serviceaccount()),
        asyncio.ensure_future(statefulset()),
        # asyncio.ensure_future(event()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == '__main__':
    main()