---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Not-Recording-Changes-Config.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- changes
- cloudwatch
- compliance
- config
- iam
- incident-response
- k8s-service
- monitoring
- recording
- sts
---

# AWS Config Not Recording Changes - AWS Config 변경 미기록

## 의미

AWS Config가 변경을 기록하지 않는 현상(구성 감사 격차 또는 ConfigChangesNotRecorded 경보 트리거)은 Config 레코더가 비활성화되었거나, Config 규칙이 평가되지 않거나, 전달 채널 구성이 잘못되었거나, IAM 권한이 불충분하거나, Config 서비스가 변경 감지 중 오류를 만나거나, Config 레코더 리소스 유형 기록 범위가 변경된 리소스를 제외할 때 발생합니다.
 AWS Config 변경 감지가 실패하고, 구성 변경 이력이 불완전하며, Config 기반 컴플라이언스가 실패합니다. 이는 컴플라이언스 및 감사 계층에 영향을 미치며 구성 추적을 손상시킵니다.

## 영향

AWS Config 변경 감지가 실패합니다. 구성 변경 이력이 불완전합니다. Config 기반 컴플라이언스가 실패합니다. 변경 추적 자동화가 효과가 없습니다. 구성 감사 추적이 누락됩니다. Config 규칙 평가가 실패합니다. 컴플라이언스 요구사항이 충족되지 않습니다.

## 플레이북

1. AWS Config 레코더 `<recorder-name>`이 존재하고 리전 `<region>`의 Config AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 AWS Config 레코더 `<recorder-name>`을 조회하여 기록 상태, 리소스 유형 기록 구성, 레코더 활성화 상태를 점검합니다.
3. 리전 `<region>`의 AWS Config 규칙을 조회하여 규칙 평가 상태, 규칙 컴플라이언스 상태, 규칙 구성을 점검합니다.
4. Config 이벤트가 포함된 CloudWatch Logs에서 레코더 `<recorder-name>` 관련 변경 감지 실패 패턴이나 기록 오류를 필터링합니다.
5. AWS Config가 사용하는 IAM 역할 `<role-name>`을 조회하여 Config 작업 및 리소스 구성 접근에 대한 정책 권한을 점검합니다.
6. AWS Config 구성 항목을 나열하고 구성 항목 생성 타임스탬프, 변경 감지 패턴, 리소스 기록 상태를 확인합니다.
7. AWS Config 전달 채널 `<delivery-channel-name>` 구성을 조회하여 전달 채널 구성을 확인합니다.
8. AWS Config의 CloudWatch 지표(가용한 경우 ConfigurationItemsRecorded)를 조회하여 구성 항목 기록 패턴을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 7일 이내 레코더 `<recorder-name>` 관련 AWS Config 레코더 활성화 또는 IAM 역할 정책 변경 이벤트를 필터링합니다.

## 진단

1. **4단계 및 8단계의 CloudWatch Logs 및 지표 분석**: Config 이벤트 로그 및 기록 지표를 검토합니다. 4단계의 CloudWatch Logs에서 레코더 오류나 전달 실패가 표시되면 구성 기록에 문제가 발생하고 있는 것입니다. 8단계의 지표에서 ConfigurationItemsRecorded가 0이면 변경이 캡처되지 않고 있는 것입니다.

2. **5단계의 IAM 권한 확인**: Config 기록에 리소스 구성 읽기가 필요한 경우 5단계의 IAM 역할에 `config:Put*` 권한과 추적되는 모든 리소스 유형에 대한 읽기 권한이 있는지 확인합니다.

3. **2단계의 레코더 상태 확인**: 2단계의 레코더 상태에서 "Recording: false"이거나 레코더가 중지되었으면 기록이 비활성화된 것입니다. 2단계의 리소스 유형 범위가 변경된 특정 리소스 유형을 제외하는지 확인합니다.

4. **7단계의 전달 채널 검토**: 7단계의 전달 채널에서 S3 버킷에 접근할 수 없거나 SNS 주제 전달이 실패하면 구성 스냅샷과 변경 알림이 전달되지 않고 있는 것입니다.

5. **9단계의 구성 변경과 상관 분석**: 9단계의 CloudTrail 이벤트에서 기록 중지 5분 이내에 레코더 상태 변경이나 IAM 역할 변경이 표시되면 최근 변경이 Config 기록에 영향을 미친 것입니다.

**상관관계를 찾을 수 없는 경우**: 6단계의 구성 항목 데이터를 사용하여 분석을 30일로 확장합니다. 기록될 것으로 예상되는 리소스가 레코더 범위 내에 있는지 확인합니다.