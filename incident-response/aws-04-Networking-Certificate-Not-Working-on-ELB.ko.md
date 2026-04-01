---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Certificate-Not-Working-on-ELB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- acm
- certificate
- elb
- incident-response
- k8s-service
- networking
- performance
- security
- sts
- working
---

# SSL Certificate Not Working on ELB - ELB에서 SSL 인증서 미작동

## 의미

Elastic Load Balancer에서 SSL 인증서가 작동하지 않는 현상(SSL/TLS 오류 또는 ELBCertificateFailure 경보 트리거)은 인증서가 만료되었거나 유효하지 않거나, 인증서가 리스너에 연결되지 않았거나, 인증서 ARN이 잘못되었거나, 인증서 도메인이 리스너 도메인과 일치하지 않거나, 인증서 상태가 활성이 아니거나, 로드 밸런서 리스너 SSL 정책 구성이 인증서와 호환되지 않을 때 발생합니다.
 HTTPS 연결이 실패하고, SSL/TLS 핸드셰이크 오류가 발생하며, 보안 연결을 설정할 수 없습니다. 이는 보안 및 로드 밸런싱 계층에 영향을 미치며 보안 트래픽을 차단합니다. 일반적으로 인증서 구성 문제, 만료 문제 또는 SSL 정책 비호환성이 원인이며, Application Load Balancer vs Classic Load Balancer를 사용하는 경우 인증서 구성이 다를 수 있고 애플리케이션에서 SSL 연결 실패가 발생할 수 있습니다.

## 영향

HTTPS 연결이 실패합니다. SSL/TLS 핸드셰이크 오류가 발생합니다. 보안 연결을 설정할 수 없습니다. 인증서 검증 오류가 나타납니다. 사용자 대면 SSL 오류가 증가합니다. 애플리케이션 보안이 손상됩니다. 로드 밸런서가 HTTPS 트래픽을 제공할 수 없습니다. SSL 인증서 경보가 발생합니다. ELBCertificateFailure 경보가 발생할 수 있으며, Application Load Balancer vs Classic Load Balancer를 사용하는 경우 인증서 구성이 다를 수 있습니다. 실패한 HTTPS 연결로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 보안 사용자 접근이 완전히 차단될 수 있습니다.

## 플레이북

1. 로드 밸런서 `<load-balancer-arn>`이 존재하고 리전 `<region>`의 ELB AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 로드 밸런서 `<load-balancer-arn>`을 조회하여 리스너 구성, SSL 인증서 연결, 인증서 ARN을 점검하고, 인증서 연결을 검증합니다.
3. 로드 밸런서 `<load-balancer-arn>`에 연결된 ACM 인증서 `<certificate-arn>`을 조회하여 상태, 도메인 검증, 만료 날짜, 인증서 체인을 점검하고, 인증서가 활성 상태인지 검증합니다.
4. 로드 밸런서 접근 로그가 포함된 CloudWatch Logs 로그 그룹에서 SSL/TLS 오류 패턴이나 인증서 검증 실패를 필터링하여 오류 메시지 세부 정보를 확인합니다.
5. 로드 밸런서 `<load-balancer-arn>`의 CloudWatch 지표(HTTPCode_Target_4XX_Count, HTTPCode_Target_5XX_Count)를 최근 1시간 동안 조회하여 SSL 관련 오류 패턴을 파악하고, 오류 빈도를 분석합니다.
6. 리전 `<region>`의 ACM 인증서를 나열하고 로드 밸런서와 연관된 인증서의 인증서 상태, 만료 날짜, 도메인 검증을 확인하여 인증서 유효성을 검증합니다.
7. 로드 밸런서 `<load-balancer-arn>`의 리스너 SSL 정책 구성을 조회하여 인증서와의 SSL 정책 호환성을 확인하고, SSL 정책 설정을 점검합니다.
8. 로드 밸런서 `<load-balancer-arn>`의 리스너 프로토콜 구성을 조회하여 HTTPS 리스너가 올바르게 구성되어 있는지 확인하고, 리스너 구성을 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 `<load-balancer-arn>` 관련 로드 밸런서 리스너 또는 인증서 연결 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. 로드 밸런서 오류의 CloudWatch 지표(플레이북 5단계)를 분석하여 SSL 관련 오류 패턴을 파악합니다. 오류가 갑자기 증가했다면 타임스탬프를 인증서 또는 리스너 구성 변경과 상관 분석합니다. 오류가 지속적이면 인증서 구성이 지속적으로 잘못되어 있을 가능성이 높습니다.

2. ACM 인증서 상태(플레이북 3단계)를 검토하여 인증서가 활성이고 만료되지 않았는지 확인합니다. 인증서 상태가 "Expired"이면 인증서 갱신이 필요합니다. 상태가 "Pending validation"이면 도메인 검증이 완료되지 않아 인증서를 사용할 수 없습니다.

3. 로드 밸런서 접근 로그가 포함된 CloudWatch Logs(플레이북 4단계)를 확인하여 구체적인 SSL/TLS 오류 패턴을 파악합니다. 로그에서 핸드셰이크 실패가 표시되면 SSL 정책이 클라이언트 요구사항과 호환되지 않을 수 있습니다. 인증서 검증 오류가 표시되면 인증서 체인이 불완전할 수 있습니다.

4. 로드 밸런서 리스너 구성(플레이북 2단계)을 확인하여 인증서가 HTTPS 리스너에 올바르게 연결되어 있는지 확인합니다. 인증서 ARN이 누락되었거나, 잘못되었거나, 인증서가 접근되는 도메인을 포함하지 않으면 SSL 연결이 실패합니다.

5. SSL 정책 구성(플레이북 7단계)을 확인하여 정책이 필요한 TLS 버전과 암호 스위트를 지원하는지 검증합니다. SSL 정책이 너무 제한적이면 이전 클라이언트가 연결에 실패할 수 있습니다.

6. 인증서 도메인 이름(플레이북 3단계)을 검토하여 인증서가 로드 밸런서가 제공하는 모든 도메인을 포함하는지 확인합니다. 사용자가 인증서의 Subject Alternative Names(SAN)에 포함되지 않은 도메인에 접근하면 브라우저에 인증서 오류가 표시됩니다.

7. CloudTrail 이벤트(플레이북 9단계)와 SSL 오류 타임스탬프를 5분 이내로 상관 분석하여 리스너 변경이나 인증서 연결을 파악합니다. 구성 변경이 SSL 오류가 시작된 시점과 일치하면 해당 변경이 원인일 가능성이 높습니다.

상관관계를 찾을 수 없는 경우: 기간을 7일로 확장하고, 인증서 체인 검증 및 중간 인증서 상태를 포함한 대안적 증거 소스를 검토하고, 인증서 만료 임박이나 도메인 검증 만료와 같은 점진적 문제를 확인합니다.