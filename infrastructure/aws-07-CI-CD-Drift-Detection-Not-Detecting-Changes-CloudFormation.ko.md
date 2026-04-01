---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Drift-Detection-Not-Detecting-Changes-CloudFormation.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- changes
- ci-cd
- cloudformation
- cloudwatch
- compliance
- detecting
- detection
- drift
- iam
- infrastructure
- k8s-service
- sts
---

# CloudFormation 드리프트 감지가 변경 사항을 감지하지 못함

## 의미

CloudFormation 드리프트 감지가 변경 사항을 감지하지 못하는(드리프트 감지 실패 또는 CloudFormationDriftDetectionFailed 알람 트리거) 이유는 드리프트 감지가 활성화되지 않았거나, 스택 리소스가 드리프트 감지 범위에 없거나, 드리프트 감지 실행이 실패하거나, IAM 권한이 드리프트 감지에 부족하거나, CloudFormation 서비스가 드리프트 감지 중 오류를 만나거나, CloudFormation 스택 리소스 유형이 드리프트 감지를 지원하지 않기 때문입니다. CloudFormation 드리프트 감지가 실패하고, 인프라 드리프트가 감지되지 않으며, 스택 구성 드리프트가 인지되지 않습니다. 이는 인프라 컴플라이언스 및 추적 계층에 영향을 미치며 인프라 상태 추적을 손상시킵니다. 일반적으로 드리프트 감지 구성 문제, 권한 문제 또는 리소스 유형 제한으로 인해 발생합니다. 중첩 스택 또는 스택 세트와 함께 CloudFormation을 사용하는 경우 드리프트 감지 동작이 다를 수 있으며 애플리케이션에서 드리프트 감지 실패가 발생할 수 있습니다.

## 영향

CloudFormation 드리프트 감지 실패; 인프라 드리프트 미감지; 스택 구성 드리프트 미인지; 드리프트 감지 자동화 무효; 인프라 컴플라이언스 추적 실패; 스택 리소스 변경 미식별; 드리프트 감지 알람 미발생; 인프라 상태 추적 손상. CloudFormationDriftDetectionFailed 알람이 발생할 수 있으며, 중첩 스택 또는 스택 세트와 함께 CloudFormation을 사용하는 경우 드리프트 감지 동작이 다를 수 있고, 애플리케이션에서 인프라 컴플라이언스 문제가 발생할 수 있으며, 인프라 상태 추적이 무효할 수 있습니다.

## 플레이북

1. CloudFormation 스택 `<stack-name>`이 존재하고 리전 `<region>`에서 CloudFormation의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 CloudFormation 스택 `<stack-name>`을 조회하고 드리프트 감지 상태, 스택 리소스 구성, 드리프트 감지 실행 이력을 검사하여 드리프트 감지가 활성화되었는지 확인합니다.
3. CloudFormation 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 스택 `<stack-name>`과 관련된 드리프트 감지 실패 패턴 또는 드리프트 감지 실행 오류를 필터링하여 오류 메시지 세부 정보를 포함합니다.
4. 스택 `<stack-name>`의 CloudFormation 스택 드리프트 감지 결과를 조회하고 드리프트 상태, 감지된 드리프트 세부 정보, 드리프트 감지 타임스탬프를 확인하여 드리프트 감지 결과를 분석합니다.
5. CloudFormation이 드리프트 감지에 사용하는 IAM 역할 `<role-name>`을 조회하고 리소스 구성 접근에 대한 정책 권한을 검사하여 IAM 권한을 확인합니다.
6. 스택 `<stack-name>`의 CloudFormation 스택 리소스를 나열하고 리소스 드리프트 상태, 리소스 구성, 드리프트 감지 범위를 확인하여 리소스 드리프트 감지 지원을 확인합니다.
7. 해당되는 경우 CloudFormation 스택 `<stack-name>` 중첩 스택 구성을 조회하고 중첩 스택 드리프트 감지를 확인하여 중첩 스택이 드리프트 감지에 영향을 미치는지 확인합니다.
8. 드리프트 감지 실행 횟수를 포함한 CloudFormation의 CloudWatch 메트릭을 조회하고 드리프트 감지 실행 패턴을 확인하여 드리프트 감지가 실행되고 있는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 7일 이내 스택 `<stack-name>`과 관련된 CloudFormation 드리프트 감지 활성화 또는 IAM 역할 정책 수정 이벤트를 필터링하여 구성 변경을 확인합니다.

## 진단

1. **3단계의 CloudWatch Logs 분석**: 드리프트 감지 실패 패턴에 대한 CloudFormation 이벤트 로그를 검토합니다. CloudWatch Logs가 드리프트 감지 중 "AccessDenied" 또는 권한 관련 오류를 나타내면 IAM 권한 문제가 원인입니다(5단계로 진행). 로그가 "Resource type not supported" 오류를 표시하면 특정 리소스는 드리프트를 확인할 수 없습니다. 로그가 결론적이지 않으면 2단계로 계속합니다.

2. **5단계의 IAM 권한 확인**: 드리프트 감지가 리소스 구성 읽기를 포함하는 경우, 5단계의 IAM 역할이 추적 중인 리소스를 설명할 권한(예: `ec2:DescribeInstances`, `s3:GetBucketConfiguration`)이 있는지 확인합니다. IAM 역할에 리소스별 읽기 권한이 없으면 권한 격차가 드리프트 감지를 방해합니다. 권한이 올바른 것으로 보이면 3단계로 계속합니다.

3. **4단계의 드리프트 감지 결과 검토**: 4단계의 드리프트 감지 결과가 "DETECTION_COMPLETE"를 표시하지만 변경이 있을 때 드리프트가 감지되지 않으면 확인된 특정 리소스를 확인합니다. 수동으로 수정된 리소스에 대해 드리프트 감지 결과가 "IN_SYNC"를 표시하면 수정이 CloudFormation이 추적하는 속성이 아니거나 드리프트 감지 범위가 제한적입니다. 4단계로 계속합니다.

4. **6단계의 리소스 지원 평가**: 6단계의 스택 리소스에 드리프트 감지를 지원하지 않는 리소스 유형이 포함된 경우(지원되는 유형은 AWS 문서 확인) 해당 리소스는 드리프트를 모니터링할 수 없습니다. 리소스가 "NOT_CHECKED" 드리프트 상태를 표시하면 드리프트 감지 범위에서 명시적으로 제외된 것입니다. 모든 리소스가 드리프트 감지를 지원하면 5단계로 계속합니다.

5. **9단계의 구성 변경과 상관관계**: 9단계의 CloudTrail 이벤트가 드리프트 감지 실패 30분 이내에 드리프트 감지 구성 변경 또는 IAM 역할 수정을 표시하면 최근 변경이 드리프트 감지 기능에 영향을 미쳤습니다. 특정 변경을 검토하여 문제를 식별합니다.

**상관관계를 찾을 수 없는 경우**: 8단계의 드리프트 감지 실행 패턴을 사용하여 분석을 30일로 확장합니다. 7단계의 중첩 스택의 경우 각 중첩 스택이 개별적으로 드리프트 확인되는지 확인합니다. 1단계의 CloudFormation 서비스 상태를 확인하고 드리프트 감지 작업이 실제로 트리거되었는지 확인합니다. AWS 문서에서 리소스 유형 제한을 검토합니다.
