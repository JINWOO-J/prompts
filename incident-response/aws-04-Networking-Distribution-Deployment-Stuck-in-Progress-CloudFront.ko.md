---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Distribution-Deployment-Stuck-in-Progress-CloudFront.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudfront
- cloudwatch
- deployment
- distribution
- incident-response
- k8s-deployment
- k8s-service
- networking
- performance
- progress
- sts
- stuck
---

# CloudFront Distribution Deployment Stuck in Progress - CloudFront 배포 배포 진행 중 멈춤

## 의미

CloudFront 배포 배포가 진행 중 멈추는 현상(배포 지연 또는 CloudFrontDeploymentStuck 경보 트리거)은 배포 구성에 오류가 있거나, 오리진 서버에 접근할 수 없거나, SSL 인증서 검증이 실패하거나, 배포 상태가 진행 중을 표시하거나, CloudFront 서비스가 배포 중 오류를 만나거나, CloudFront 배포 구성 검증이 실패할 때 발생합니다.
 CloudFront 배포 배포가 지연되고, 배포 변경이 적용되지 않으며, CDN 구성 업데이트가 차단됩니다. 이는 콘텐츠 전달 및 CDN 계층에 영향을 미치며 구성 업데이트를 차단합니다. 일반적으로 구성 검증 오류, 오리진 연결 문제 또는 인증서 문제가 원인입니다.

## 영향

CloudFront 배포 배포가 지연됩니다. 배포 변경이 적용되지 않습니다. CDN 구성 업데이트가 차단됩니다. 배포 자동화가 중단됩니다. 배포 상태가 진행 중으로 유지됩니다. 새 구성이 활성화되지 않습니다. 배포 프로세스를 완료할 수 없습니다.

## 플레이북

1. CloudFront 배포 `<distribution-id>`가 존재하고 리전 `<region>`의 CloudFront AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 CloudFront 배포 `<distribution-id>`를 조회하여 배포 상태, 배포 상태, 구성 오류를 점검하고, 배포 상태를 검증합니다.
3. CloudFront 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 배포 `<distribution-id>` 관련 배포 실패 이벤트나 오류 패턴을 필터링하여 배포 오류 세부 정보를 확인합니다.
4. CloudFront 배포 `<distribution-id>`의 CloudWatch 지표(4xxErrorRate, 5xxErrorRate)를 최근 24시간 동안 조회하여 배포 관련 오류 패턴을 파악하고, 오류 지표를 분석합니다.
5. 배포 `<distribution-id>`의 CloudFront 배포 구성 변경을 나열하고 배포 상태, 오류 메시지, 배포 타임스탬프를 확인하여 배포 이력을 분석합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 배포 `<distribution-id>` 관련 CloudFront 배포 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.
7. CloudFront 배포 `<distribution-id>`의 오리진 구성을 조회하여 오리진 서버 접근성을 확인하고, 오리진 연결 문제가 배포에 영향을 미치는지 점검합니다.
8. CloudFront 배포 `<distribution-id>`의 SSL 인증서 구성을 조회하여 인증서 유효성을 확인하고, 인증서 문제가 배포를 방해하는지 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 `<distribution-id>` 관련 CloudFront 배포 구성 검증 오류를 필터링하여 검증 오류를 확인합니다.

## 진단

1. CloudFront 배포의 CloudWatch 지표(플레이북 4단계)를 분석하여 배포 관련 오류 패턴을 파악합니다. 배포 시도 중 오류율이 증가했다면 오리진 연결 또는 구성 문제가 성공적인 배포를 방해하고 있을 수 있습니다.

2. CloudFront 배포 상태(플레이북 2단계)를 검토하여 현재 배포 상태를 확인하고 구성 오류를 파악합니다. 상태가 단순 변경에 대해 30분 이상 "InProgress"를 표시하면 구성 검증 실패로 배포가 멈춰 있을 수 있습니다.

3. CloudFront 이벤트 및 CloudTrail 이벤트가 포함된 CloudWatch Logs(플레이북 3단계 및 6단계)를 확인하여 구체적인 배포 실패 또는 검증 오류 메시지를 파악합니다.

4. 오리진 서버 구성 및 접근성(플레이북 7��계)을 확인하여 CloudFront가 오리진에 접근할 수 있는지 확인합니다. 오리진 서버에 접근할 수 없거나 오류를 반환하면 배포가 오리진 연결 검증을 시도하면서 멈출 수 있습니다.

5. SSL 인증서 구성(플레이북 8단계)을 확인하여 인증서가 유효하고 올바르게 구성되어 있는지 검증합니다. ACM 인증서가 발급되지 않았거나, 만료되었거나, 배포의 대체 도메인 이름과 일치하지 않으면 배포가 실패합니다.

6. 배포 구성 변경(플레이북 5단계)을 검토하여 현재 배포를 트리거한 변경 사항을 파악합니다.

7. 1시간 이상 멈춘 배포의 경우 CloudFront 배포 구성 크기 제한이나 복잡한 오리진 접근 구성(OAI/OAC) 문제를 확인합니다.

상관관계를 찾을 수 없는 경우: 기간을 48시간으로 확장하고, 배포 구성 검증 및 오리진 서버 연결을 포함한 대안적 증거 소스를 검토합니다.