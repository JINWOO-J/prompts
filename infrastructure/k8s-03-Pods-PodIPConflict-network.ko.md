---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodIPConflict-network.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- network
- networking
- podipconflict
- pods
---

---
title: Pod IP Conflict - Network
weight: 251
categories:
  - kubernetes
  - network
---

# PodIPConflict-network — Pod IP 충돌

## 의미

여러 Pod에 동일한 IP 주소가 할당되었습니다(KubeNetworkPluginError or KubePodNotReady 알림 발생)  CNI plugin (Calico, Flannel, Cilium) is misconfigured, pod CIDR ranges overlap between nodes, the network plugin pods are experiencing issues in kube-system namespace, or IP address allocation from the IP pool is failing. Pods show duplicate IP addresses, CNI plugin pods show IP allocation errors in kube-system namespace, and pod events show FailedCreatePodSandbox or IP allocation failures. 이는 네트워크 플레인에 영향을 미치며, network connectivity problems and routing failures, 일반적으로 CNI plugin misconfiguration or IP pool exhaustion; applications cannot communicate correctly.

## 영향

Pods have duplicate IP addresses; network routing fails; Pod 통신 불가 correctly; IP conflicts cause connectivity issues; CNI plugin allocation errors occur in pod events; KubeNetworkPluginError alerts fire when CNI plugin fails to allocate unique IPs; KubePodNotReady alerts fire when pods cannot establish network connectivity; pod networking is broken; service endpoints may point to wrong pods; cluster networking is unstable; pod-to-pod communication fails. Pods show duplicate IP addresses indefinitely; CNI plugin pods show IP allocation errors; applications cannot communicate correctly and may show errors; network routing fails and pod-to-pod communication fails.

## 플레이북

1. Pod를 describe하고 `<pod-name>` Namespace `<namespace>` with IP conflict to retrieve detailed information including network configuration and IP assignment.

2. Pod의 이벤트를 조회하고 `<pod-name>` Namespace `<namespace>` 타임스탬프 순으로 정렬하여 파악합니다 IP allocation failures and network-related issues.

3. List all pods across all namespaces and retrieve their IP addresses 파악합니다 pods with duplicate IP addresses.

4. Pod를 나열하고 the `kube-system` namespace and check CNI plugin pod status (e.g., Calico, Flannel, Cilium) 확인합니다 if the network plugin is running and functioning.

5. Retrieve logs from CNI plugin pods in the `kube-system` namespace and filter for IP allocation errors, conflicts, or CIDR issues.

6. Check cluster pod CIDR configuration 확인합니다 if CIDR ranges are correctly configured and do not overlap.

## 진단

1. Pod 이벤트를 분석하여 Playbook 파악합니다 FailedCreatePodSandbox or IP allocation failure errors. 이벤트에서 IP allocation conflicts or IPAM errors, note the specific error message indicating the conflict source.

2. 이벤트에서 IP conflicts, check the list of all pod IPs 플레이북 파악합니다 pods with duplicate IP addresses. If multiple pods share the same IP, identify which pods are affected and their respective nodes.

3. If duplicate IPs are confirmed, check CNI plugin pod status in kube-system 플레이북. If CNI pods show failures, restarts, or NotReady state, the network plugin IPAM is not functioning correctly.

4. If CNI pods are healthy, review CNI plugin logs 플레이북 for IPAM errors, IP pool exhaustion, or CIDR overlap warnings. If logs show IP pool exhaustion, the allocated CIDR range has no available addresses.

5. If IPAM is functioning, check cluster pod CIDR configuration 플레이북. If CIDR ranges overlap between nodes or conflict with node CIDRs, IP allocation produces duplicates.

6. If CIDR configuration is correct, verify recent node additions 플레이북 events. If new nodes were added without proper CIDR allocation, node CIDR ranges may overlap with existing nodes.

**If no IPAM configuration issue is found**: Review CNI plugin version compatibility, check if manual IP assignments conflict with IPAM allocations, verify if multiple CNI plugins are installed caconflicts, and examine if CNI plugin database or state store is corrupted.

