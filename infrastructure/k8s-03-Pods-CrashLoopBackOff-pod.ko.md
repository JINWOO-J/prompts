---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/CrashLoopBackOff-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- crashloopbackoff
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- pods
---

---
title: CrashLoopBackOff - Pod
weight: 201
categories:
  - kubernetes
  - pod
---

# CrashLoopBackOff-pod — Pod CrashLoopBackOff 상태

## 의미

Pod Container가 시작 직후 반복적으로 오류와 함께 종료되어, Kubernetes가 백오프하며 CrashLoopBackOff 상태로 재시작합니다(KubePodCrashLooping 알림 발생). 안정적인 Running 상태에 도달하지 못합니다. 이는 애플리케이션 구성 오류, 리소스 제약, 의존성 실패 또는 Container 이미지 문제로 인해 Pod가 정상적으로 시작되지 못함을 나타냅니다.

## 영향

애플리케이션 Pod 시작 실패; 서비스 불가용; Deployment가 원하는 Replica 수를 달성하지 못함; 애플리케이션 다운타임 발생; 의존 서비스 실패 가능;
 KubePodCrashLooping 알림 발생; Pod가 CrashLoopBackOff 상태로 유지; Container가 반복적으로 종료; 애플리케이션 오류로 Pod 안정성 확보 불가; Replica 수가 원하는 상태와 불일치.

## 플레이북

### AI Agent용 (NLP)

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 Pod 상태, 재시작 횟수, 종료 사유(OOMKilled, Error 등), 최근 이벤트를 확인합니다. 이를 통해 Pod 크래시 원인을 즉시 파악할 수 있습니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 실패 시퀀스와 타임스탬프를 확인합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container 상태에서 종료 사유를 확인합니다. OOMKilled인 경우 메모리 limit 문제입니다.

4. Namespace `<namespace>`에서 Pod `<pod-name>`의 이전(크래시된) Container 로그를 조회하여 크래시 전 상황을 확인합니다.

5. Namespace `<namespace>`에서 Deployment `<deployment-name>`을 describe하여 Container 이미지, 리소스 limit, 환경 변수, Liveness/Readiness Probe 구성을 확인합니다.

6. Namespace `<namespace>`에서 Deployment `<deployment-name>`의 롤아웃 이력을 조회하여 최근 배포 이후 문제가 시작되었는지 확인합니다.

### DevOps/SRE용 (CLI)

1. Pod 상태, 재시작 횟수, 이벤트 확인:
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   ```

2. 타임스탬프 순으로 이벤트 조회:
   ```bash
   kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name> --sort-by='.lastTimestamp'
   ```

3. Container 종료 사유 확인:
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.status.containerStatuses[*].lastState.terminated}'
   ```

4. 이전 크래시된 Container의 로그 조회:
   ```bash
   kubectl logs <pod-name> -n <namespace> --previous
   ```

5. Deployment 구성 확인:
   ```bash
   kubectl describe deployment <deployment-name> -n <namespace>
   kubectl get deployment <deployment-name> -n <namespace> -o yaml
   ```

6. 롤아웃 이력 확인:
   ```bash
   kubectl rollout history deployment/<deployment-name> -n <namespace>
   ```

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 주요 실패 원인을 파악합니다. "BackOff"와 "CrashLoopBackOff"를 포함하는 이벤트는 Container 크래시를 나타냅니다. "Back-off restarting failed container" 이벤트는 크래시 루프 패턴을 확인합니다.

2. 종료 사유가 "OOMKilled"인 경우(플레이북 3단계), 메모리 고갈이 원인입니다. Container가 메모리 limit을 초과하여 커널에 의해 종료되었습니다. 메모리 limit을 증가시키거나 애플리케이션의 메모리 누수를 조사합니다.

3. 종료 사유가 "Error"이고 0이 아닌 종료 코드인 경우, 이전 크래시 인스턴스의 Container 로그(플레이북 4단계)를 분석하여 크래시를 유발하는 애플리케이션 수준 오류를 파악합니다. 일반적인 원인:
   - 종료 코드 1: 애플리케이션 오류 또는 처리되지 않은 예외
   - 종료 코드 137: SIGKILL (OOMKilled 또는 수동 종료)
   - 종료 코드 139: SIGSEGV (세그멘테이션 폴트)
   - 종료 코드 143: SIGTERM (정상 종료 실패)

4. Pod 이벤트에 "ImagePullBackOff" 또는 "ErrImagePull"이 표시되면, Container 이미지를 풀링할 수 없습니다. 이미지 이름, 태그, 레지스트리 접근성, imagePullSecrets 구성을 확인합니다.

5. Pod 이벤트에 "CreateContainerConfigError"가 표시되면, Pod 사양에서 누락된 ConfigMap, Secret 또는 환경 변수 참조를 확인합니다.

6. 이벤트에서 최근 배포 변경이 확인되면(플레이북 6단계), 크래시 시작 시점과 배포 롤아웃 타임스탬프를 상관 분석하여 코드 또는 구성 변경이 근본 원인인지 파악합니다.

7. 이벤트와 로그가 결론을 내리기 어려운 경우, 크래시 패턴을 리소스 사용량 메트릭과 비교하여 점진적 리소스 고갈이나 의존성 실패를 파악합니다.

**Pod 이벤트에서 명확한 근본 원인을 파악하지 못한 경우**: 스택 트레이스나 오류 패턴에 대한 애플리케이션 로그 검토, Liveness Probe 잘못된 구성 확인(너무 공격적인 타임아웃), 외부 의존성(데이터베이스, API) 접근 가능 여부 확인, 시작 시간이 initialDelaySeconds를 초과하는지 점검, 환경 변수나 마운트된 볼륨의 구성 문제를 확인합니다.
