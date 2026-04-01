---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Not-Mitigating-DDoS-Attacks-Shield.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- attacks
- cloudwatch
- ddos
- k8s-service
- mitigating
- performance
- security
- shield
- sts
---

# Shield DDoS 공격 완화 실패 — AWS Shield Not Mitigating DDoS Attacks

## 의미

AWS Shield가 DDoS 공격을 완화하지 못합니다(보호 실패 또는 ShieldMitigationFailed 알람 발생). 원인으로는 Shield 미활성화, Shield Advanced 미구독, 공격 탐지 임계값 미충족, Shield 완화 규칙 설정 오류, Shield 서비스의 공격 완화 중 오류, Shield 보호 범위가 대상 리소스를 포함하지 않는 경우 등이 있습니다. AWS Shield DDoS 보호가 실패하고, DDoS 공격이 완화되지 않으며, 서비스 가용성이 저해됩니다. 이는 보안 및 DDoS 보호 계층에 영향을 미치며 서비스 가용성을 저해합니다. 일반적으로 Shield 구성 문제, 구독 문제, 탐지 임계값 설정 오류가 원인이며, Shield Advanced와 Shield Standard를 사용할 때 완화 역량이 다르고 애플리케이션에서 DDoS 보호 실패가 발생할 수 있습니다.

## 영향

AWS Shield DDoS 보호 실패, DDoS 공격 미완화, 서비스 가용성 저해, 공격 트래픽이 리소스에 도달, Shield 보호 자동화 무효, DDoS 공격 탐지 실패, 서비스 안정성 영향, 보안 보호 저해. ShieldMitigationFailed 알람 발생 가능. Shield Advanced와 Shield Standard를 사용할 때 완화 역량이 다름. DDoS 공격으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 서비스 가용성이 완전히 저해될 수 있습니다.

## 플레이북

1. 리소스 `<resource-arn>`에 대한 AWS Shield 보호의 존재를 확인하고 리전 `<region>`의 Shield AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 리소스 `<resource-arn>`에 대한 AWS Shield 보호 구성을 조회하여 Shield 활성화 상태, Shield Advanced 구독, 보호 설정을 검사하고 Shield가 활성화되었는지 확인합니다.
3. Shield 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 DDoS 공격 탐지 패턴, 완화 이벤트, 보호 실패 메시지를 필터링하고 완화 오류 세부사항을 포함합니다.
4. AttackCount 및 MitigatedAttackCount를 포함한 Shield 보호 CloudWatch 메트릭을 지난 7일 동안 조회하여 공격 패턴과 완화 효과를 식별하고 완화 메트릭을 분석합니다.
5. Shield 보호 리소스를 나열하고 보호 상태, 공격 이력, 완화 구성을 확인하며 보호 범위를 검증합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Shield 구성 또는 공격 완화 이벤트를 필터링하고 구성 변경을 확인합니다.
7. AWS Shield Advanced 구독 상태를 조회하여 Shield Advanced 구독을 확인하고 구독이 완화 역량에 영향을 미치는지 확인합니다.
8. AttackTraffic을 포함한 Shield 보호 CloudWatch 메트릭을 조회하여 공격 트래픽 패턴을 확인하고 공격 탐지 임계값이 충족되는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 7일 동안 리소스 `<resource-arn>`과 관련된 Shield 보호 구성 수정 이벤트를 필터링하고 구성 변경을 확인합니다.

## 진단

1. **4단계 및 8단계의 CloudWatch 메트릭 분석**: 공격 탐지 및 완화 패턴에 대한 Shield 메트릭을 검토합니다. 4단계의 CloudWatch 메트릭에서 AttackCount > 0이지만 MitigatedAttackCount = 0이면 공격은 탐지되지만 완화되지 않는 것입니다. 8단계의 메트릭에서 공격 트래픽이 탐지 임계값 미만이면 공격 볼륨이 자동 완화를 트리거하지 못할 수 있습니다. 메트릭에서 공격 탐지가 없으면 2단계로 진행합니다.

2. **2단계의 Shield 보호 구성 확인**: 2단계의 Shield 보호에서 리소스가 보호되지 않거나 Shield가 활성화되지 않은 것으로 확인되면 보호 부재가 근본 원인입니다. 7단계의 Shield Advanced 구독 상태를 확인합니다 - 공격 유형에 Shield Advanced가 필요하지만 Standard만 활성화되어 있으면 구독 수준이 불충분한 것입니다. 보호가 올바르게 구성되어 있으면 3단계로 진행합니다.

3. **5단계의 보호 범위 확인**: 5단계의 보호 리소스 목록에 대상 리소스가 포함되지 않으면 불완전한 보호 범위가 문제입니다. CloudFront 배포, Route 53 호스팅 영역, ELB, Elastic IP, Global Accelerator가 모두 포함되었는지 확인합니다. 범위가 완전하면 4단계로 진행합니다.

4. **3단계 및 6단계의 CloudWatch Logs 및 CloudTrail 이벤트 검토**: 3단계의 CloudWatch Logs에서 Shield 완화 이벤트가 오류 또는 부분 완화와 함께 확인되면 완화 규칙 구성이 최적이 아닐 수 있습니다. 6단계의 CloudTrail 이벤트에서 완화 실패와 상관관계가 있는 Shield 구성 수정이 확인되면 최근 변경이 보호에 영향을 미친 것입니다. 로그에서 특정 공격 벡터에 대한 보호 실패가 확인되면 해당 공격 유형이 포함되지 않을 수 있습니다.

5. **7단계의 Shield Advanced 기능 상관관계 분석**: Shield Advanced를 사용하는 경우 DDoS Response Team(DRT) 참여 및 사전 참여 기능이 구성되었는지 확인합니다. Shield Advanced 메트릭에서 예상보다 낮은 완화율이 확인되면 고급 기능이 올바르게 활성화되지 않았거나 공격 패턴이 새로운 것일 수 있습니다.

**상관관계가 발견되지 않는 경우**: 4단계의 CloudWatch 메트릭을 사용하여 분석을 30일로 확장합니다. 완화 실패가 지속적이면 모든 리소스에 대해 Shield가 올바르게 활성화되었는지 확인합니다. 실패가 간헐적이면 표준 탐지를 우회할 수 있는 공격 패턴을 조사합니다. 9단계의 CloudTrail 이벤트에서 보호 구성 변경을 확인하고 1단계의 Shield 서비스 상태를 검증합니다.
