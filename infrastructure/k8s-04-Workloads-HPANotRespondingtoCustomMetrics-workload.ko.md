---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/HPANotRespondingtoCustomMetrics-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- hpanotrespondingtocustommetrics
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubernetes
- performance
- scaling
- workload
- workloads
---

---
title: HPA Not Responding to Custom Metrics - Workload
weight: 277
categories:
  - kubernetes
  - workload
---

# HPA가 Custom Metrics에 응답하지 않음 (HPANotRespondingtoCustomMetrics-workload)

## 의미

HPA(Horizontal Pod Autoscaler)가 Custom Metrics에 응답하지 않는 상태입니다(KubeHPAReplicasMismatch 또는 KubeDeploymentReplicasMismatch 알림 발생).
Custom Metrics API(custom.metrics.k8s.io/v1beta1)가 설정되지 않았거나, kube-system namespace의 Metrics Adapter Pod(prometheus-adapter, custom-metrics-apiserver)가 사용 불가능하거나, 외부 소스에서 Custom Metrics가 수집되지 않거나, HPA가 Metrics Adapter에 존재하지 않는 잘못된 Custom Metric 이름을 참조하기 때문입니다. HPA에 Custom Metrics 사용 불가 Condition이 표시되고, kube-system namespace의 Custom Metrics Adapter Pod에 장애가 표시되며, HPA 상태에 FailedGetObjectMetric 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 Custom Metric 기반 스케일링을 방해합니다. 주로 Custom Metrics Adapter 장애 또는 잘못된 Metric 참조가 원인이며, 애플리케이션이 비즈니스 Metric 변화에 적응할 수 없어 오류가 발생할 수 있습니다.

## 영향

HPA가 Custom Metrics를 기반으로 스케일링할 수 없으며, Custom Metric 임계값에 관계없이 Deployment가 고정된 Replica 수를 유지합니다. 애플리케이션별 스케일링이 비활성화되고, 요청 비율이나 큐 깊이와 같은 비즈니스 Metrics를 기반으로 Pod를 스케일링할 수 없습니다. HPA 상태에 Custom Metrics 사용 불가 Condition이 표시되고, 스케일링 결정이 리소스 Metrics로만 제한됩니다. KubeHPAReplicasMismatch 및 KubeDeploymentReplicasMismatch 알림이 발생하며, Custom Metric 기반 자동 스케일링이 실패합니다.

## 플레이북

1. namespace <namespace>에서 HPA <hpa-name>을 describe하여 다음을 확인합니다:
   - 현재 Custom Metrics 대비 목표 Metrics
   - 원하는 Replica 수 대비 현재 Replica 수
   - Custom Metrics 설정
   - Custom Metrics가 사용 불가능한 이유를 보여주는 Condition
   - FailedGetObjectMetric 또는 Custom Metrics 오류를 보여주는 Event

2. namespace <namespace>에서 HPA <hpa-name>의 이벤트를 타임스탬프 순으로 조회하여 Custom Metrics 실패 순서를 확인합니다.

3. API Service를 조회하고 Metrics 관련 항목을 확인하여 Custom Metrics API(custom.metrics.k8s.io/v1beta1)가 사용 가능하고 올바르게 설정되었는지 검증합니다.

4. kube-system namespace에서 label app=prometheus-adapter(또는 app=custom-metrics-apiserver)로 Pod를 조회하고 Adapter 로그를 확인하여 Custom Metrics Adapter Pod 상태가 실행 중이고 정상인지 검증합니다.

5. kube-system namespace에서 Custom Metrics Adapter Service 및 Endpoint가 접근 가능한지 확인하고 Custom Metrics API 가용성을 테스트합니다.

6. namespace <namespace>에서 HPA <hpa-name> 설정을 조회하고 HPA 스펙에서 참조하는 Custom Metric 이름이 Custom Metrics Adapter에서 사용 가능한 Metrics와 일치하는지 확인합니다.

## 진단

1. 플레이북의 HPA 이벤트를 분석하여 Custom Metrics 관련 오류를 파악합니다. 이벤트에 FailedGetObjectMetric, "unable to get custom metric" 또는 "no such metric" 오류가 표시되면, 이벤트 타임스탬프와 오류 메시지를 사용하여 구체적인 실패를 식별합니다.

2. 이벤트가 Custom Metrics Adapter 문제를 나타내면, 플레이북 4단계의 Adapter Pod 상태를 확인합니다. HPA가 응답을 중단한 시점에 Adapter 이벤트에 CrashLoopBackOff, 재시작 또는 장애가 표시되면 Adapter가 근본 원인입니다.

3. 이벤트가 Custom Metrics API 사용 불가를 나타내면, 플레이북 3단계의 API Service 상태를 확인합니다. 실패 시점에 APIService 이벤트에 사용 불가 또는 저하 상태가 표시되면 Custom Metrics API 설정에 주의가 필요합니다.

4. 이벤트가 잘못된 Metric 이름을 나타내면, 플레이북 6단계의 HPA Metric 설정을 확인합니다. HPA가 Adapter에 존재하지 않는 Metric 이름을 참조하면 사용 가능한 Metrics와 일치하도록 Metric 이름 참조를 수정합니다.

5. 이벤트가 Prometheus 또는 외부 Metrics 소스 문제를 나타내면, 소스 가용성을 확인합니다. Custom Metrics가 사용 불가능해진 시점에 Prometheus 이벤트에 장애가 표시되면 Metrics 소스가 근본 원인입니다.

6. 이벤트가 Service 또는 Endpoint 변경을 나타내면, 플레이북 5단계의 Adapter Service를 확인합니다. Metrics가 사용 불가능해진 시점에 Service 이벤트에 수정이 표시되면 Service 설정 변경이 Metrics 가용성에 영향을 미친 것입니다.

7. 이벤트가 최근 배포 또는 업그레이드를 나타내면, 변경 타임스탬프와 실패 발생 시점을 연관시킵니다. Custom Metrics 실패 전에 Adapter 배포 이벤트 또는 클러스터 업그레이드 이벤트가 발생했다면 최근 변경이 Metrics 파이프라인을 손상시켰을 수 있습니다.

**상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(5분→10분, 30분→1시간, 1시간→2시간), Custom Metrics Adapter 로그에서 점진적 성능 저하를 검토하고, Metrics 소스와의 간헐적 연결 문제를 확인하고, Custom Metrics API 인증 또는 권한 문제가 시간이 지남에 따라 발생했는지 검사하고, Custom Metrics Adapter 리소스 제약이 점진적으로 누적되었는지 확인하고, Custom Metrics API 접근성에 영향을 미치는 DNS 또는 서비스 디스커버리 문제를 확인합니다. Custom Metrics 사용 불가는 즉각적인 변경이 아닌 점진적 인프라 저하로 인해 발생할 수 있습니다.
