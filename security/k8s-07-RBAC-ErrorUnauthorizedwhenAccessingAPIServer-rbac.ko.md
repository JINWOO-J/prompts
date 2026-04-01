---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/07-RBAC/ErrorUnauthorizedwhenAccessingAPIServer-rbac.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- errorunauthorizedwhenaccessingapiserver
- k8s-rbac
- k8s-service
- kubernetes
- performance
- rbac
- security
- sts
---

---
title: Error Unauthorized when Accessing API Server - RBAC
weight: 266
categories:
  - kubernetes
  - rbac
---

# API 서버 접근 시 Unauthorized 오류 — ErrorUnauthorizedwhenAccessingAPIServer-rbac

## 의미

API 서버 요청이 Unauthorized(401) 오류를 반환합니다(KubeAPIErrorsHigh 또는 KubeClientErrors 알림 발생). 원인으로는 인증 토큰 만료, 무효, 누락, kubeconfig 자격 증명 오류, 인증서 기반 인증 실패 등이 있습니다. API 요청이 401 상태 코드를 반환하고, 인증 토큰이 만료 상태를 표시할 수 있으며, 클라이언트 인증서가 만료 오류를 표시할 수 있습니다. 이는 인증 및 인가 플레인에 영향을 미치며 클러스터 접근을 차단합니다. 일반적으로 만료된 자격 증명, 인증서 만료, kubeconfig 설정 오류가 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

kubectl 명령 Unauthorized 오류 실패, API 서버 접근 거부, 클러스터 작업 차단, KubeAPIErrorsHigh 알림 발생, KubeClientErrors 알림 발생, API 서버 401 상태 코드 반환, 인증 실패로 모든 클러스터 접근 차단, 서비스 계정 인증 불가, 애플리케이션 API 서버 연결 실패. API 요청이 무기한 401 상태 코드 반환. 인증 토큰 만료 상태 표시 가능. Kubernetes API를 사용하는 애플리케이션에서 오류나 성능 저하 발생 가능. 클러스터 작업이 차단됩니다.

## 플레이북

1. `kubectl auth can-i --list`로 기본 API 접근을 테스트하여 401 Unauthorized 오류를 확인합니다 - 401로 실패하면 인증이 깨진 것입니다(인가가 아님).

2. `kubectl config current-context`와 `kubectl config view --minify`로 현재 컨텍스트와 자격 증명을 확인하여 kubeconfig가 올바른 클러스터와 사용자를 가리키는지 검증합니다.

3. `kubectl auth whoami`(K8s 1.27+)로 ID가 인식되는지 확인합니다 - 여기서 401 오류가 발생하면 인증 토큰/인증서가 유효하지 않은 것이 확인됩니다.

4. 토큰 기반 인증의 경우 JWT를 디코딩하여 토큰 만료를 확인합니다: `kubectl config view --raw -o jsonpath='{.users[0].user.token}' | cut -d'.' -f2 | base64 -d | jq '.exp'`로 현재 시간과 비교합니다.

5. 인증서 기반 인증의 경우 인증서 만료를 확인합니다: `kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d | openssl x509 -noout -dates`.

6. Pod 내부의 서비스 계정 인증의 경우 토큰이 마운트되었는지 확인합니다: `cat /var/run/secrets/kubernetes.io/serviceaccount/token`으로 ServiceAccount가 여전히 존재하는지 확인합니다.

7. API 서버 로그에서 인증 실패를 확인합니다: `kubectl logs -n kube-system -l component=kube-apiserver --tail=100 | grep -i "401\|unauthorized\|authentication"`으로 실패하는 인증 방법을 식별합니다.

## 진단

1. Unauthorized 오류 타임스탬프와 인증 토큰 만료 타임스탬프를 비교하고, Unauthorized 오류 5분 이내에 토큰이 만료되었는지 확인합니다.

2. Unauthorized 오류 타임스탬프와 kubeconfig 파일 수정 타임스탬프를 비교하고, Unauthorized 오류 30분 이내에 자격 증명 변경이 발생했는지 확인합니다.

3. Unauthorized 오류 타임스탬프와 클라이언트 인증서 만료 타임스탬프를 비교하고, Unauthorized 오류 1시간 이내에 인증서가 만료되었는지 확인합니다.

4. Unauthorized 오류 타임스탬프와 서비스 계정 토큰 시크릿 삭제 타임스탬프를 비교하고, Unauthorized 오류 30분 이내에 토큰 시크릿이 제거되었는지 확인합니다.

5. Unauthorized 오류 타임스탬프와 API 서버 인증 구성 수정 타임스탬프를 비교하고, Unauthorized 오류 30분 이내에 인증 설정이 변경되었는지 확인합니다.

6. Unauthorized 오류 타임스탬프와 클러스터 업그레이드 또는 인증서 교체 타임스탬프를 비교하고, Unauthorized 오류 1시간 이내에 인증 메커니즘에 영향을 미치는 인프라 변경이 발생했는지 확인합니다.

**지정된 시간 범위 내에서 상관관계가 발견되지 않는 경우**: 검색 범위를 확장하고(5분→10분, 30분→1시간, 인증서 만료의 경우 1시간→24시간), 점진적 인증 문제에 대한 API 서버 로그를 검토하고, 간헐적 토큰 갱신 문제를 확인하고, 인증 구성이 시간이 지남에 따라 드리프트되었는지 조사하고, 인증서가 점진적으로 만료에 접근했는지 확인하고, 토큰 검증에 영향을 미치는 API 서버 또는 인증 제공자 문제를 확인합니다. Unauthorized 오류는 즉각적인 변경이 아닌 점진적인 인증 자격 증명 만료나 구성 드리프트로 인해 발생할 수 있습니다.
