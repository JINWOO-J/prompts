---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/10-Monitoring-Autoscaling/AutoscalerScalingTooSlowly-autoscaler.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- autoscal
- autoscaler
- autoscalerscalingtooslowly
- autoscaling
- capacity
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- monitoring
- scaling
---

---
title: Autoscaler Scaling Too Slowly - 오토스케일러 스케일링 지연
weight: 281
categories:
  - kubernetes
  - autoscaler
---

# AutoscalerScalingTooSlowly-autoscaler

## 의미

클러스터 오토스케일러가 워크로드 수요에 비해 노드 용량을 너무 느리게 조정하고 있습니다(KubePodPending 알림 트리거 가능). Pending Pod나 높은 사용률이 더 많은 용량의 필요성을 명확히 나타내는데도 노드 스케일아웃과 스케일인이 실시간 부하에 뒤처집니다.

## 영향

Pod가 예상보다 오래 Pending 상태 유지, Deployment 스케일링 느림, 애플리케이션 시작 지연, 트래픽 급증 시 서비스 용량 부족 가능, KubePodPending 알림 발생, 오토스케일러 스케일링 속도 불충분, 노드 프로비저닝 지연, 워크로드 수요가 가용 용량 초과.

## 플레이북

1. `kube-system` namespace에서 클러스터 오토스케일러 Deployment를 describe하여 상태, 구성, 스케일링 동작을 확인합니다.
2. `kube-system` namespace의 이벤트를 타임스탬프 순으로 조회하여 오토스케일러 스케일링 이벤트와 스로틀링 지표를 식별합니다.
3. `kube-system` namespace에서 클러스터 오토스케일러 ConfigMap을 조회하고 scale-down-delay-after-add, max-node-provision-time, max-nodes-per-time 등 스케일링 속도 파라미터를 확인합니다.
4. `kube-system` namespace의 클러스터 오토스케일러 Pod 로그를 조회하고 스케일링 속도 메시지 또는 스로틀링 지표를 필터링합니다.
5. 모든 노드를 나열하고 현재 노드 수와 최대 허용 노드를 포함한 노드 풀 구성과 용량 제한을 확인합니다.
6. 모든 namespace에서 스케일링이 필요한 Pending 상태의 Pod를 나열하고 Pending 기간을 기록합니다.

## 진단

1. 플레이북의 클러스터 오토스케일러 이벤트와 로그를 분석하여 스케일링 속도 제약을 식별합니다. 스로틀링 메시지, 속도 제한, 지연을 보여주는 이벤트가 스케일링 속도에 영향을 미치는 특정 병목을 나타냅니다.

2. 오토스케일러 구성에 보수적인 스케일링 파라미터가 표시되면, 이는 의도적으로 스케일링 속도를 제한합니다. 플레이북의 scale-down-delay-after-add, scan-interval, max-node-provision-time 설정을 확인합니다. 기본값이 빠른 스케일링 워크로드에 너무 보수적일 수 있습니다.

3. 이벤트가 노드 프로비저닝 지연(스케일업 결정과 노드 Ready 사이의 긴 시간)을 나타내면, 클라우드 프로바이더 프로비저닝 시간이 병목입니다. 오토스케일러 로그에서 노드 시작 시간을 확인합니다.

4. Pending Pod가 예상보다 오래 대기 중이면, Pending 기간을 오토스케일러 스캔 간격과 비교합니다. 오토스케일러는 각 스캔 간격(기본 10초)마다 Pending Pod를 평가합니다.

5. 오토스케일러 로그에 스케일업 결정이 이루어졌지만 노드가 Ready 상태가 되는 데 오래 걸리는 것으로 표시되면, 노드 시작 순서를 확인합니다. 노드는 상태 확인을 통과하고, 클러스터에 등록하고, 시스템 Pod가 스케줄링된 후에야 워크로드를 수용합니다.

6. 스케일링이 느려 보이지만 오토스케일러가 스케일업 작업당 최대 노드에 있으면, expander 구성을 확인합니다. 보수적으로 구성된 경우 오토스케일러가 한 번에 하나의 노드만 스케일링할 수 있습니다.

7. 클라우드 프로바이더 속도 제한이 발생하면, 오토스케일러 로그에 API 스로틀링 또는 재시도 메시지가 표시됩니다. 더 높은 API 제한을 요청하거나 API 호출을 줄이도록 오토스케일러 구성을 최적화하는 것을 고려합니다.
