---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodFailsLivenessProbe-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- monitoring
- performance
- podfailslivenessprobe
- pods
---

---
title: Pod Fails Liveness Probe - Pod
weight: 253
categories:
  - kubernetes
  - pod
---

# PodFailsLivenessProbe-pod — Liveness Probe 실패

## 의미

Pod가 Liveness Probe 검사에 실패하고 있습니다(KubePodCrashLooping 또는 KubePodNotReady 등의 알림 발생). 애플리케이션이 Liveness 엔드포인트에서 응답하지 않거나, 크래시 또는 행이 발생했거나,
 Probe 구성이 잘못되었거나, 네트워크 문제로 Probe 실행이 불가합니다. kubectl에서 Pod가 CrashLoopBackOff 상태를 보이고, Pod 이벤트에 "liveness probe failed" 메시지와 함께 Unhealthy 오류가 표시되며, 애플리케이션 로그에 크래시, 행 또는 Health check 엔드포인트 실패가 표시됩니다. Liveness Probe가 반복적으로 실패하면 kubelet이 Container를 재시작합니다. 이는 워크로드 플레인에 영향을 미치며, 애플리케이션 크래시, 잘못 구성된 Probe 또는 네트워크 문제로 인해 Pod가 안정적 상태를 유지하지 못하는 애플리케이션 상태 문제를 나타냅니다.

## 영향

KubePodCrashLooping 알림 발생; kubelet에 의해 Container가 반복적으로 재시작됨; Pod가 CrashLoopBackOff 상태에 진입; 애플리케이션이 안정적 상태를 유지하지 못함; Pod가 리소스를 소비하지만 서비스를 제공하지 않음; 재시작 횟수 급증; 재시작 시 애플리케이션 데이터 손실 가능; Pod 상태에 Liveness Probe 실패와 재시작 표시.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 재시작 횟수, 마지막 종료 사유, "Liveness probe failed"를 포함하는 Events와 구체적인 실패 메시지(HTTP 상태, connection refused, timeout)를 확인합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 Unhealthy 사유로 필터링하여 Liveness Probe 실패 타임스탬프와 메시지를 확인합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`의 Liveness Probe 구성(path, port, timeoutSeconds, periodSeconds, failureThreshold)을 조회합니다.

4. Pod `<pod-name>` 내부에서 Liveness Probe 엔드포인트로 요청을 실행하여 엔드포인트가 응답하는지 확인합니다.

5. Namespace `<namespace>`에서 Pod `<pod-name>`의 로그를 이전 Container 인스턴스를 포함하여 조회하고 재시작 전 상황을 확인합니다.

6. Namespace `<namespace>`에서 Pod `<pod-name>`의 마지막 종료 사유를 확인합니다. OOMKilled인 경우 애플리케이션이 메모리 부족입니다.

7. Namespace `<namespace>`에서 Deployment `<deployment-name>`을 describe하여 Probe 구성을 검토하고 initialDelaySeconds가 애플리케이션 시작에 충분한지 확인합니다.

8. Namespace `<namespace>`에서 Pod `<pod-name>`의 리소스 사용량 메트릭을 조회하여 CPU/메모리가 limit에 도달하여 애플리케이션이 응답하지 못하는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 Liveness Probe 실패를 파악합니다. "Liveness probe failed"와 함께 "Unhealthy"를 포함하는 이벤트에 구체적인 실패 사유가 포함됩니다. Readiness Probe와 달리 Liveness Probe 실패는 Container 재시작을 트리거합니다.

2. 마지막 종료 사유가 "OOMKilled"인 경우(플레이북 6단계), Liveness Probe 실패 전에 애플리케이션이 메모리 부족이었습니다. 메모리 문제를 먼저 해결합니다. Liveness Probe 실패는 원인이 아닌 증상입니다.

3. 이벤트에서 Probe에 대해 "connection refused" 또는 "timeout"이 표시되면:
   - Probe 실행 전에 애플리케이션이 크래시되거나 행됨
   - 크래시 사유에 대한 이전 Container 로그 확인(플레이북 5단계)
   - 애플리케이션이 SIGTERM을 정상적으로 처리하고 복구하는지 확인

4. 이벤트에서 HTTP 오류 코드가 표시되면, 애플리케이션이 응답하지만 비정상입니다:
   - Probe 실패 타임스탬프의 애플리케이션 로그에서 오류 확인
   - 애플리케이션 수준 Health check 로직 조사
   - 의존성(데이터베이스, 캐시, API)이 정상인지 확인

5. 리소스 사용량이 limit에 도달한 경우(플레이북 8단계), 애플리케이션이 Probe에 응답하기에 너무 느릴 수 있습니다:
   - CPU Throttling이 느린 응답 시간을 유발 - CPU limit 증가
   - 메모리 압박이 GC 일시 중지를 유발 - 메모리 limit 증가
   - 임시 조치로 Probe timeoutSeconds 증가 고려

6. Probe 구성이 공격적인 설정인 경우(플레이북 3단계), 조정합니다:
   - timeoutSeconds가 애플리케이션 응답 시간에 비해 너무 짧음
   - periodSeconds가 너무 빈번하여 Probe 오버헤드 유발
   - failureThreshold가 너무 낮아 일시적 문제에 재시작 유발
   - initialDelaySeconds가 애플리케이션 시작에 비해 너무 짧음

7. 수동 테스트 시 엔드포인트가 응답하지만(플레이북 4단계) 정상 운영 중 Probe가 실패하면, 부하 시 애플리케이션이 응답하지 못합니다. 성능 문제에 대한 애플리케이션 프로파일링을 수행합니다.

**Liveness Probe 실패 해결을 위해**: 응답 불가를 유발하는 근본적인 애플리케이션 문제 수정, 더 관대하도록 Probe 타이밍 조정, 제약이 있는 경우 리소스 limit 증가, Liveness 엔드포인트가 최소한의 작업만 수행하도록 보장합니다(Liveness check에서 데이터베이스 쿼리 회피).
