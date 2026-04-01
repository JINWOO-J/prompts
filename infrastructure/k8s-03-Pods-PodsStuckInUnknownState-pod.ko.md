---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckInUnknownState-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
- podsstuckinunknownstate
---

---
title: Pods Stuck In Unknown State - Pod
weight: 296
categories:
  - kubernetes
  - pod
---

# PodsStuckInUnknownState-pod — Pod Unknown 상태 고착

## 의미

Pods are reported in the Unknown phase (potentially triggering KubePodNotReady alerts)  control plane has lost contact with the kubelet on the node hosting them, so their real runtime state cannot be accurately determined. Pods show Unknown phase in kubectl, nodes show NotReady condition, and kubelet logs may show connection timeout errors or API server communication failures. 이는 node communication failures, kubelet issues, or network partition problems preventing status updates; applications running on affected nodes may experience errors or become unreachable.

## 영향

Pod status cannot be determined; pods may be running but appear unavailable; services may lose endpoints; applications may be inaccessible; cluster state becomes inconsistent; KubePodNotReady 알림 발생; Pod가 Unknown state; kubelet communication failures occur; node status becomes unreliable. Pods show Unknown phase indefinitely; nodes show NotReady condition; kubelet logs show connection timeout errors; applications running on affected nodes may experience errors or become unreachable.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 파악합니다 which node the pod is running on and verify pod's node allocation and status.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 pod-related events that may indicate communication or node issues.

3. List pods across all namespaces with status phase Unknown 파악합니다 pods stuck in Unknown state.

4. 모든 노드를 나열하고 and check node status.

5. Retrieve node <node-name> and check node conditions 확인합니다 if node can communicate with API server.

6. Check kubelet service status and logs on affected node via Pod Exec tool or SSH for last 100 entries if node access is available.

7. From a pod on another reachable node, execute network connectivity tests to the unreachable node IP to test network connectivity.

8. From a pod on the affected node, verify API server connectivity to <api-server-ip> on port 6443.

9. Pod를 나열하고 namespace kube-system and filter for CNI plugin pods 확인합니다 CNI status.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 when and why communication with the pod was lost. Events may show the last known state before the pod became Unknown.

2. If node status shows NotReady condition (플레이북 4-5), the kubelet on the node has lost communication with the API server. This is the primary cause of Unknown pod state. The pod may still be running on the node but its status cannot be reported.

3. If kubelet service is not running or shows errors (플레이북 6), restart the kubelet service on the affected node. Check kubelet logs for certificate expiration, API server connectivity issues, or resource exhaustion.

4. If network connectivity tests fail (플레이북 7-8), there is a network partition between the node and control plane. 일반적인 원인:
   - Network infrastructure failures (switches, routers)
   - Firewall rules blocking API server port 6443
   - Cloud provider network issues
   - Node network interface problems

5. If CNI plugin pods are failing (플레이북 9), pod networking on the node is broken. This can prevent kubelet from communicating with the API server if it routes through the pod network.

6. If all checks pass but pods remain Unknown, the issue may be intermittent connectivity. Check for packet loss or high latency between the node and API server.

**If the node is confirmed unreachable**: Consider draining the node and investigating physical/virtual machine health. If the node cannot be recovered, delete it from the cluster. Pods on the Unknown node will be rescheduled to healthy nodes after the node is removed or the pod-eviction-timeout is exceeded.
