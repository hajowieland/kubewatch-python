#!/usr/bin/env python3

import os
import sys
#import tempfile
import requests
import json
#from kubernetes import client, config, watch
#from kubernetes.client import configuration
from pick import pick
import asyncio
from kubernetes_asyncio import client, config, watch
#from kubernetes.client import configuration

# import slackclient
# client = slackclient.SlackClient(token='<token>')
# client.api_call(
#     'chat.postMessage',
#     channel='<channel-id>',
#     as_user=True,
#     attachments=[{'text': 'test3'}]
# )
try:  
   webhook_url = os.environ["SLACK_WEBHOOK"]
   clustername = os.environ["CLUSTER"]
except KeyError: 
   print("Please set the environment variables")
   sys.exit(1)

    
async def slack(eventtype,eventkind,eventname,eventns, **kwargs):

    eventnodename = kwargs.get('eventnodename', None)
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



async def daemonset():
    v1ext = client.ExtensionsV1beta1Api()
    async with watch.Watch().stream(v1ext.list_daemon_set_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def pod():
    v1 = client.CoreV1Api()

    async with watch.Watch().stream(v1.list_pod_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].spec.node_name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace,eventnodename=event['object'].spec.node_name)


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


async def deployment():
    v1ext = client.ExtensionsV1beta1Api()

    async with watch.Watch().stream(v1ext.list_deployment_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


async def ingress():
    v1ext = client.ExtensionsV1beta1Api()

    async with watch.Watch().stream(v1ext.list_ingress_for_all_namespaces) as stream:
        async for event in stream:
            print("Event: %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name))
            await slack(eventtype=event['type'],eventkind=event['object'].kind,eventname=event['object'].metadata.name,eventns=event['object'].metadata.namespace)


    # ioloop = asyncio.get_event_loop()

    # ioloop.create_task(daemonset())
    # ioloop.create_task(pods())

    # ioloop.run_forever()


    #for event in w.stream(v1.list_namespace, _request_timeout=60):
    # for event in w.stream(v1.list_event_for_all_namespaces, _request_timeout=60):
    #     print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    #     eventype = event['type']
    #     eventobject = event['object'].metadata.name
    #     eventns = event['object'].metadata.namespace




        
        


    #slack_data = json.loads(json_data)





    ## Example #1:
    # config.load_kube_config()

    # v1 = client.CoreV1Api()
    # print("Listing Pods with their IPs:")
    # ret = v1.list_pod_for_all_namespaces(watch=False)
    # for i in ret.items:
    #     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


    # count = 10
    # w = watch.Watch()
    # for event in w.stream(v1.list_namespace, _request_timeout=60):
    #     print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    #     count -= 1
    #     if not count:
    #         w.stop()

    # print("Ended.")

    # print("Supported APIs (* is preferred version):")
    # print("%-40s %s" %
    #       ("core", ",".join(client.CoreApi().get_api_versions().versions)))
    # for api in client.ApisApi().get_api_versions().groups:
    #     versions = []
    #     for v in api.versions:
    #         name = ""
    #         if v.version == api.preferred_version.version and len(
    #                 api.versions) > 1:
    #             name += "*"
    #         name += v.version
    #         versions.append(name)
    #     print("%-40s %s" % (api.name, ",".join(versions)))

    ## Example #4:
    # contexts, active_context = config.list_kube_config_contexts()
    # if not contexts:
    #     print("Cannot find any context in kube-config file.")
    #     return
    # contexts = [context['name'] for context in contexts]
    # active_index = contexts.index(active_context['name'])
    # option, _ = pick(contexts, title="Pick the context to load",
    #                  default_index=active_index)
    # # Configs can be set in Configuration class directly or using helper
    # # utility
    # config.load_kube_config(context=option)

    # print("Active host is %s" % configuration.Configuration().host)

    # v1 = client.CoreV1Api()
    # print("Listing pods with their IPs:")
    # ret = v1.list_pod_for_all_namespaces(watch=False)
    # for item in ret.items:
    #     print(
    #         "%s\t%s\t%s" %
    #         (item.status.pod_ip,
    #          item.metadata.namespace,
    #          item.metadata.name))


    




def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(config.load_kube_config())
    tasks = [
        asyncio.ensure_future(daemonset()),
        asyncio.ensure_future(pod()),
        asyncio.ensure_future(secret()),
        asyncio.ensure_future(service()),
        asyncio.ensure_future(serviceaccount()),
        asyncio.ensure_future(deployment()),
        asyncio.ensure_future(ingress()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == '__main__':
    main()