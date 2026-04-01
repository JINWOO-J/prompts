---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodIPNotReachable-network.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- dns
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- network
- networking
- podipnotreachable
- pods
- sts
---

---
title: Pod IP Not Reachable - Network
weight: 224
categories:
  - kubernetes
  - network
---

# PodIPNotReachable-network — Pod IP 도달 불가

## 의미

Pod IP 주소에 도달할 수 없습니다(KubeNetworkPluginError or KubePodNotReady 알림 발생)  network plugin (CNI) pods are not functioning in kube-system namespace, pod networking is misconfigured, routes are not properly configured on nodes, or nodes cannot communicate due to network infrastructure issues. Pods have IP addresses assigned but connectivity tests fail, CNI plugin pods show failures in kube-system namespace, and pod events show FailedCreatePodSandbox or network configuration errors. 이는 네트워크 플레인에 영향을 미치며, pod-to-pod communication, 일반적으로 CNI plugin failures or network misconfiguration; applications cannot communicate across pods.

## 영향

Pods cannot communicate with each other; pod IP addresses are unreachable; network connectivity between pods fails; service endpoints may be unreachable; KubeNetworkPluginError alerts fire when network plugin fails to configure pod networking; KubePodNotReady alerts fire when pods cannot establish network connectivity; cluster networking is broken; pod-to-pod communication is blocked; applications cannot communicate across pods; service DNS resolves but connections fail. Pods have IP addresses assigned but connectivity tests fail indefinitely; CNI plugin pods show failures; applications cannot communicate across pods and may show errors; service endpoints may be unreachable.

## 플레이북

1. Pod를 describe하고 `<pod-name>` Namespace `<namespace>` to retrieve detailed information including IP address, network configuration, and conditions.

2. Pod의 이벤트를 조회하고 `<pod-name>` Namespace `<namespace>` 타임스탬프 순으로 정렬하여 파악합니다 network-related issues and sandbox creation failures.

3. Pod를 나열하고 the `kube-system` namespace and check network plugin pod status (e.g., Calico, Flannel, Cilium) 확인합니다 if the network plugin is running and healthy.

4. From another pod, execute ping or curl to the pod `<pod-name>` IP address to test connectivity and verify if the pod IP is reachable.

5. Retrieve logs from network plugin pods in the `kube-system` namespace and filter for networking errors, route configuration issues, or connectivity problems.

6. Check node network interfaces and routes 확인합니다 if node networking is correctly configured for pod communication.

## 진단

1. Pod 이벤트를 분석하여 Playbook 파악합니다 FailedCreatePodSandbox or network configuration errors. 이벤트에서 sandbox creation failures, the CNI plugin failed to configure networking for the pod.

2. 이벤트에서 CNI failures, check network plugin pod status in kube-system 플레이북 data. If CNI pods (Calico, Flannel, Cilium) show CrashLoopBackOff, NotReady, or recent restarts, the network plugin is not functioning correctly.

3. If CNI pods are healthy, verify pod IP assignment and Ready condition 플레이북 data. If pod has IP but is not Ready, the issue may be application-level rather than network-level.

4. If pod is Ready with IP assigned, check NetworkPolicy rules 플레이북 for policies blocking ingress traffic to the pod. If restrictive policies exist without proper allow rules, traffic is blocked at the policy level.

5. If NetworkPolicy is not blocking, review connectivity test results 플레이북. If ping fails but pod is running, check node routing tables and network interface configuration for route misconfiguration.

6. If routing appears correct, check CNI plugin logs 플레이북 for IP allocation errors, IPAM failures, or route programming issues that may indicate underlying network infrastructure problems.

**If no network configuration issue is found**: Review node network interface status, check for MTU mismatches between nodes, verify if cloud provider networking (VPC routes, security groups) is correctly configured, and examine if recent cluster or node updates affected network configuration.

