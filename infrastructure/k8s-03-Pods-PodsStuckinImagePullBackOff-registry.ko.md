---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckinImagePullBackOff-registry.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-secret
- k8s-service
- kubernetes
- pods
- podsstuckinimagepullbackoff
- registry
---

---
title: Pods Stuck in ImagePullBackOff - Registry
weight: 271
categories:
  - kubernetes
  - registry
---

# PodsStuckinImagePullBackOff-registry — Pod ImagePullBackOff 상태 고착

## 의미

Kubelet is repeatedly failing to pull a container image from the registry (triggering ImagePullBackOff or ErrImagePull pod states)  image reference is invalid, credentials are wrong, image pull secrets are missing or expired, or the registry or network path to it is unavailable. Pods show ImagePullBackOff or ErrImagePull state in kubectl, pod events show Failed or ErrImagePull errors, and container waiting state reason indicates image pull failures. 이는 워크로드 플레인에 영향을 미치며, container startup, 일반적으로 invalid image references, missing or expired image pull secrets, or registry connectivity issues; 애플리케이션을 시작할 수 없습니다.

## 영향

Pods cannot start; deployments remain at 0 replicas; 롤링 업데이트 실패; applications fail to deploy; services become unavailable; new workloads cannot be created; pods stuck in ImagePullBackOff state; image pull errors occur; container registry connectivity issues; KubePodPending alerts may fire due to image pull failures. Pods show ImagePullBackOff or ErrImagePull state indefinitely; pod events show Failed or ErrImagePull errors; 애플리케이션을 시작할 수 없습니다 and may show errors; deployments remain at 0 replicas.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 container waiting state reason and message fields 확인합니다 ImagePullBackOff or ErrImagePull and capture the exact error - look in Events section for "Failed to pull image" with the specific reason (auth error, not found, timeout).

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 확인합니다 the sequence of image pull errors, focon events with reasons such as Failed and messages containing "pull" or ErrImagePull.

3.  Deployment <deployment-name> Namespace <namespace> and verify that each container's image field (registry, repository, tag, or digest) is correct and exists in the target registry.

4. Check the pod spec for imagePullSecrets for pod <pod-name> Namespace <namespace>, then retrieve and validate those Secret objects 확인합니다 they exist and contain valid credentials for the registry.

5. Verify network connectivity and basic reachability to the container registry endpoint <registry-url> from a test pod in the cluster.

6. On the node where the pod is scheduled, verify disk space availability in the image storage directories to ensure there is enough space to pull the image.

## 진단

1. Pod 이벤트를 분석하여 Playbook 파악합니다 the specific image pull error type. Events showing "Failed to pull image" with "unauthorized" indicate authentication issues. Events showing "manifest unknown" or "not found" indicate the image or tag does not exist. Events showing "timeout" or "i/o timeout" indicate network connectivity problems.

2. 이벤트에서 authentication failure, verify imagePullSecrets 플레이북 validation results. Confirm the Secret exists, is correctly referenced in the pod spec, and contains valid base64-encoded credentials. 확인합니다: the credentials have expired or been rotated.

3. 이벤트에서 image not found, use the image name 플레이북 deployment inspection 확인합니다 correctness. 확인합니다: the registry hostname is correct, the repository path exists, and the tag or digest is valid. Verify the image was not recently deleted or if the tag was moved.

4. 이벤트에서 network issues, use the Playbook connectivity test results 판단합니다 if the registry is reachable from cluster nodes. Check for DNS resolution failures, firewall rules blocking registry ports (typically 443), or NetworkPolicies restricting egress.

5. 이벤트에서 rate limiting or quota exhaustion, check if the registry enforces pull limits. For public registries like Docker Hub, configure imagePullSecrets with authenticated credentials to increase rate limits.

6. 이벤트에서 node-level issues, verify disk space availability 플레이북 node checks. 확인합니다: the node has sufficient space in /var/lib/docker or /var/lib/containerd for image layers.

**명확한 원인을 파악하지 못한 경우 from events**: 확인합니다: multiple pods on the same node are failing (indicating node-specific issue), verify registry TLS certificates are trusted by the container runtime, examine if a proxy or service mesh is intercepting registry traffic, and review if the image requires specific platform architecture (amd64 vs arm64).

