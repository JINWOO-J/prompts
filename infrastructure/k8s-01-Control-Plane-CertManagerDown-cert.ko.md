---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertManagerDown-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- cert
- certmanagerdown
- compliance
- control
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- plane
- rds
- security
- sts
---

---
title: Cert Manager Down - cert-manager 다운
weight: 42
categories: [kubernetes, cert-manager]
---

# CertManagerDown

## 의미

cert-manager Controller가 실행되지 않거나 정상이 아닌 상태이며(CertManagerDown 알림 트리거), cert-manager Pod가 크래시하거나, 스케줄링되지 않거나, 헬스 체크에 응답하지 않습니다. cert-manager Deployment에서 준비된 레플리카가 0개이고, 인증서 작업이 처리되지 않으며, 새 인증서 발급과 갱신이 차단됩니다. 클러스터의 모든 인증서 관리에 영향을 미칩니다. 새 인증서를 발급할 수 없고, 갱신이 이루어지지 않으며, 인증서 인프라가 비기능 상태입니다.

## 영향

CertManagerDown 알림이 발생합니다. 새 인증서를 발급할 수 없고, 인증서 갱신이 중단됩니다. 대기 중인 인증서 요청이 처리되지 않으며, 인증서가 필요한 새 Deployment가 차단됩니다. 만료되는 인증서가 갱신되지 않아 인증서 만료 시 HTTPS 중단이 발생합니다. 컴플라이언스 요구사항이 위험에 처하고 보안 상태가 저하됩니다.

## 플레이북

1. cert-manager 네임스페이스에서 cert-manager Deployment를 조회하고 레플리카 상태를 확인합니다.

2. cert-manager Controller Pod 상태, 재시작 횟수 및 이벤트를 확인합니다.

3. cert-manager Controller 로그에서 시작 실패 또는 런타임 오류를 조회합니다.

4. cert-manager Webhook Deployment가 정상인지 확인합니다(cert-manager 작동에 필수).

5. Pod 스케줄링을 방해하는 리소스 제약(CPU, 메모리, 노드 가용성)을 확인합니다.

6. cert-manager CRD가 올바르게 설치되어 있고 손상되지 않았는지 검증합니다.

7. 다른 Operator 또는 Admission Webhook과의 충돌을 확인합니다.

## 진단

Controller Pod 상태를 분석하고 Pod가 CrashLooping, Pending 또는 누락 상태인지 식별합니다. Pod 상태와 이벤트를 근거로 사용합니다.

cert-manager 작동에 메모리 제한이 너무 낮음을 나타내는 OOMKilled 이벤트를 확인합니다. 컨테이너 상태와 메모리 메트릭을 근거로 사용합니다.

cert-manager가 Webhook 없이는 작동할 수 없으므로 Webhook 서비스에 접근 가능한지 검증합니다. Webhook Pod 상태와 서비스 엔드포인트를 근거로 사용합니다.

cert-manager 업그레이드 후 Controller 실패를 유발할 수 있는 CRD 버전 불일치를 확인합니다. CRD 버전과 Controller 호환성을 근거로 사용합니다.

Controller 로그에서 특정 오류 패턴(API 접근 거부, 리더 선출 실패, Watch 오류)을 분석합니다. 로그 분석을 근거로 사용합니다.

지정된 시간 범위 내에서 연관 관계를 찾을 수 없는 경우: cert-manager Pod를 재시작하고, RBAC 권한이 올바른지 검증하며, API Server 연결성을 확인하고, CRD가 손상된 경우 cert-manager를 재설치하며, 리더 선출 Lease가 고착되지 않았는지 확인합니다.
