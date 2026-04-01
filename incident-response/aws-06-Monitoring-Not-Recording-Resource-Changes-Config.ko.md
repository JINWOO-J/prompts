---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Not-Recording-Resource-Changes-Config.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- changes
- compliance
- config
- iam
- incident-response
- k8s-service
- monitoring
- recording
- resource
- s3
- sts
---

# AWS Config Not Recording Resource Changes - AWS Config 리소스 변경 미기록

## 의미

AWS Config가 리소스 변경을 기록하지 않는 현상(구성 추적 격차 또는 ConfigResourceChangesNotRecorded 경보 트리거)은 Config 레코더가 중지되었거나, Config 전달 채널이 잘못 구성되었거나, IAM 권한이 Config 작업에 불충분하거나, 리소스 유형이 기록되지 않거나, Config 서비스가 변경 기록 중 오류를 만나거나, Config 레코더 리소스 유형 범위가 리소스를 제외할 때 발생합니다.
 AWS Config 리소스 변경이 기록되지 않고, 구성 이력이 불완전하며, 컴플라이언스 추적이 실패합니다. 이는 컴플라이언스 및 감사 계층에 영향을 미치며 리소스 변경 추적을 손상시킵니다.

## 영향

AWS Config 리소스 변경이 기록되지 않습니다. 구성 이력이 불완전합니다. 컴플라이언스 추적이 실패합니다. Config 기반 분석을 사용할 수 없습니다. 리소스 변경 가시성이 상실됩니다. Config 기록 자동화가 효과가 없습니다. 구성 감사 추적이 불완전합니다. 컴플라이언스 요구사항이 충족되지 않습니다.

## 플레이북

1. AWS Config 레코더 `<recorder-name>`이 존재하고 리전 `<region>`의 Config AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 AWS Config 레코더 `<recorder-name>`을 조회하여 레코더 상태, 기록 상태, 기록되는 리소스 유형, 기록 구성을 점검하고, 레코더가 기록 중인지 검증합니다.
3. 리전 `<region>`의 AWS Config 전달 채널 `<delivery-channel-name>`을 조회하여 전달 채널 구성, S3 버킷 설정, SNS 주제 설정을 점검합니다.
4. Config 이벤트가 포함된 CloudWatch Logs에서 레코더 `<recorder-name>` 관련 기록 실패 패턴이나 전달 오류를 필터링합니다.
5. AWS Config가 사용하는 IAM 역할 `<role-name>`을 조회하여 Config 작업 및 리소스 접근에 대한 정책 권한을 점검합니다.
6. AWS Config 구성 스냅샷을 나열하고 스냅샷 생성 타임스탬프, 스냅샷 완전성, 리소스 변경 기록 패턴을 확인합니다.
7. AWS Config 레코더 `<recorder-name>`의 리소스 유형 기록 범위를 조회하여 리소스 유형이 포함되어 있는지 확인합니다.
8. AWS Config의 CloudWatch 지표(가용한 경우 ConfigurationItemsRecorded)를 조회하여 구성 항목 기록 패턴을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 7일 이내 레코더 `<recorder-name>` 관련 AWS Config 레코더 상태 또는 전달 채널 변경 이벤트를 필터링합니다.

## 진단

1. **4단계 및 8단계의 CloudWatch Logs 및 지표 분석**: Config 이벤트 로그 및 기록 지표에서 패턴을 검토합니다. 4단계의 CloudWatch Logs에서 S3 또는 SNS로의 전달 오류가 표시되면 전달 채널 문제가 기록을 방해하고 있는 것입니다. 8단계의 지표에서 ConfigurationItemsRecorded가 0이면 변경이 캡처되지 않고 있는 것입니다.

2. **5단계의 IAM 권한 확인**: Config가 리소스 구성을 읽고 전달 대상에 쓰기 위한 권한이 필요한 경우 5단계의 IAM 역할에 `config:Put*`, `s3:PutObject` 및 리소스별 읽기 권한이 있는지 확인합니다.

3. **2단계 및 7단계의 레코더 및 기록 범위 확인**: 2단계의 레코더 상태에서 "Recording: false"이면 레코더가 중지된 것입니다. 7단계의 리소스 유형 범위가 특정 유형으로 제한되어 있고 변경된 리소스가 포함되지 않으면 범위 제한이 기록을 방해합니다.

4. **3단계의 전달 채널 구성 검토**: 3단계의 전달 채널에서 S3 버킷이 누락되었거나, 버킷 정책이 접근을 차단하거나, SNS 주제가 잘못 구성되었으면 구성 항목을 전달할 수 없습니다.

5. **9단계의 구성 변경과 상관 분석**: 9단계의 CloudTrail 이벤트에서 기록 중지 5분 이내에 레코더 상태 변경, 전달 채널 변경 또는 IAM 역할 변경이 표시되면 최근 변경이 문제를 유발한 것입니다.

**상관관계를 찾을 수 없는 경우**: 6단계의 스냅샷 데이터를 사용하여 분석을 30일로 확장합니다. 기록될 것으로 예상되는 리소스가 AWS Config에서 지원되는지 확인합니다(지원되는 리소스 유형에 대한 AWS 문서 확인). 다중 리전 추적의 경우 모든 필요한 리전에서 Config가 활성화되어 있는지 확인합니다.