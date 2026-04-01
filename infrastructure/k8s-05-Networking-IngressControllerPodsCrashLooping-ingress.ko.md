---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressControllerPodsCrashLooping-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingresscontrollerpodscrashlooping
- k8s-ingress
- k8s-namespace
- k8s-pod
- kubernetes
- networking
- performance
---

---
title: Ingress Controller Pods CrashLooping - Ingress
weight: 256
categories:
  - kubernetes
  - ingress
---

# IngressControllerPodsCrashLooping-ingress - Ingress Controller Pod 반복 크래시

## 의미

Ingress Controller Pod가 반복적으로 크래시하고 재시작하고 있으며(KubePodCrashLooping 알림 발생), 설정 오류로 시작이 불가하거나, 잘못된 Ingress 리소스가 Controller 장애를 유발하거나, 리소스 제약으로 크래시가 발생하거나, Controller가 필요한 리소스에 접근할 수 없는 것이 원인입니다. kubectl에서 Ingress Controller Pod가 CrashLoopBackOff 상태를 보이고, Ingress Controller 로그에 시작 실패 또는 설정 오류가 표시되며, Pod 재시작 횟수가 지속적으로 증가합니다. 이는 네트워크 계층에 영향을 미치며 Ingress 리소스를 통한 트래픽 라우팅을 방해하고, 일반적으로 설정 오류, 잘못된 Ingress 리소스 또는 리소스 제약이 원인입니다. 애플리케이션이 사용자에게 접근 불가능해지며 오류가 발생할 수 있습니다.

## 영향

Ingress Controller 사용 불가, 모든 Ingress 리소스의 트래픽 라우팅 중단, 외부 트래픽이 애플리케이션에 도달 불가, Ingress Endpoint에서 오류 반환, 클러스터 외부에서 애플리케이션 접근 불가, KubePodCrashLooping 알림 발생, Ingress Controller 로그에 시작 실패 표시, 클러스터 Ingress 기능 완전 중단. Ingress Controller Pod가 무기한 CrashLoopBackOff 상태 유지, Ingress Controller 로그에 시작 실패 표시, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능, 클러스터 Ingress 기능 완전 중단.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe pod <controller-pod-name> -n <namespace>`를 사용하여 Ingress Controller Pod를 상세 조회하고, Pod 재시작 횟수, 컨테이너 종료 사유, 상태를 검사하여 크래시 루프를 확인하고 재시작 원인을 파악합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<controller-pod-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Failed`, `CrashLoopBackOff` 또는 설정/시작 오류를 나타내는 메시지에 초점을 맞춰 Ingress Controller 관련 이벤트를 필터링합니다.

3. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, Controller가 시작할 수 없는 이유를 설명하는 설정 오류, 시작 실패 또는 크래시 메시지를 필터링합니다.

4. `<namespace>` Namespace에서 Ingress Controller Deployment 또는 DaemonSet을 조회하고, 설정, 환경 변수, 리소스 제한을 검토하여 설정 문제가 크래시를 유발하는지 확인합니다.

5. 클러스터의 모든 Ingress 리소스를 조회하고, Controller 크래시를 유발할 수 있는 잘못되거나 잘못 구성된 Ingress 리소스를 확인합니다.

6. Ingress Controller Pod 리소스 사용량 메트릭을 확인하여 리소스 제약 또는 OOM 상태가 크래시를 유발하는지 확인합니다.

## 진단

플레이북 섹션에서 수집한 Pod 상세 조회 출력과 이벤트를 분석하는 것부터 시작합니다. 컨테이너 종료 사유, 재시작 횟수, Controller 로그가 주요 진단 신호를 제공합니다.

**이벤트에서 컨테이너 종료 사유로 OOMKilled가 표시되는 경우:**
- Ingress Controller의 메모리가 부족합니다. Deployment의 메모리 제한을 확인하고 Controller 메모리 사용 패턴과 비교합니다. 메모리 제한을 늘리거나, 클러스터에 많은 라우트가 있는 경우 Ingress 리소스 수를 줄입니다.

**로그에서 설정 파싱 오류 또는 잘못된 어노테이션 경고가 표시되는 경우:**
- Ingress 리소스에 잘못된 설정이 있습니다. 모든 Ingress 리소스 목록에서 구문 오류, 지원되지 않는 어노테이션 또는 잘못된 백엔드 참조를 검토합니다. 문제가 있는 Ingress 리소스를 수정하거나 제거합니다.

**로그에서 TLS Secret을 찾을 수 없거나 인증서 로딩 오류가 표시되는 경우:**
- 참조된 TLS Secret이 누락되었거나 유효하지 않습니다. Ingress TLS 섹션에서 Secret 참조를 확인합니다. Secret이 Ingress와 동일한 Namespace에 존재하고 유효한 `tls.crt` 및 `tls.key` 데이터를 포함하는지 확인합니다.

**로그에서 시작 실패 또는 포트 수신 오류가 표시되는 경우:**
- Controller가 필요한 포트에 바인딩할 수 없습니다. 노드에서 다른 프로세스가 포트 80/443을 사용하고 있는지(hostNetwork 모드의 경우) 또는 Service 포트 설정이 충돌하는지 확인합니다.

**이벤트에서 ImagePullBackOff 또는 ErrImagePull이 표시되는 경우:**
- Controller 이미지를 가져올 수 없습니다. 이미지 이름과 태그가 올바른지 확인합니다. 프라이빗 레지스트리를 사용하는 경우 레지스트리 인증을 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. 크래시 타임스탬프와 Deployment 리비전 변경을 비교하여 Deployment 업데이트 후 크래시가 시작되었는지 확인합니다.
2. 모든 Namespace의 Ingress 생성 타임스탬프를 검사하여 크래시가 새 Ingress 리소스 생성과 일치하는지 확인합니다.
3. Controller Namespace의 삭제 이벤트를 검토하여 특정 ConfigMap 또는 Secret이 삭제되었는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** Ingress Controller 설정을 수정하여 디버그 로깅을 활성화한 후 크래시를 재현하여 상세한 오류 정보를 캡처합니다. Controller 버전이 Kubernetes 버전과 호환되는지 확인합니다.
