---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Connection-Timeout-SSH-Issues-EC2.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- connection
- ec2
- incident-response
- issues
- k8s-pod
- k8s-service
- performance
- rds
- scaling
- security
- timeout
---

# EC2 인스턴스 연결 타임아웃 - SSH 이슈 (Connection Timeout SSH Issues)

## 의미

EC2 인스턴스 SSH 연결이 타임아웃되거나 실패합니다(EC2InstanceStatusCheckFailed 또는 연결 타임아웃 에러 같은 알람 트리거). 보안 그룹 규칙이 SSH 접근을 차단하거나, 인스턴스에 퍼블릭 IP 주소가 없거나, 키 페어 불일치가 발생하거나, 네트워크 연결 이슈가 SSH 접근을 방해하거나, Systems Manager Session Manager가 설정되지 않았기 때문입니다. 사용자는 SSH 접근 시도 시 "Connection timed out" 또는 "Connection refused" 에러를 경험하고, 인스턴스는 "running" 상태를 보이지만 AWS 콘솔에서 상태 확인이 실패를 나타낼 수 있으며, 보안 그룹 규칙이 포트 22 접근을 차단할 수 있습니다. 이는 컴퓨팅 계층에 영향을 미치며 원격 접근을 방해합니다. 일반적으로 보안 그룹 제한, 퍼블릭 IP 주소 누락, 네트워크 연결 이슈, 또는 IMDSv2 적용이 원인이며, 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 Pod 트러블슈팅이 차단되고 컨테이너 오케스트레이션 작업이 실패할 수 있습니다.

## 영향

EC2InstanceStatusCheckFailed 알람 발생 가능; 관리자가 인스턴스에 접근 불가; SSH 연결 타임아웃 에러 발생; 로그에 "Connection timed out" 또는 "Connection refused" 메시지 표시; 인스턴스 접근 불가 상태 유지; 원격 관리 실패; 트러블슈팅 차단. AWS 콘솔에서 인스턴스가 "running" 상태를 보이지만 상태 확인이 실패를 나타냄; 수동 개입 필요; 운영 작업 지연; 사용자가 관리 작업 수행 불가; 설정 변경 적용 불가. CloudWatch 대시보드에서 인스턴스 상태가 저하된 것으로 표시; Auto Scaling이 인스턴스를 비정상으로 표시할 수 있음; 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 Pod 스케줄링 실패, 컨테이너 시작 불가, 또는 클러스터 연결 이슈 발생 가능; 컨테이너 오케스트레이션 작업에 실패 표시 가능; 애플리케이션에 에러 또는 성능 저하 발생 가능.

## 플레이북

### AI 에이전트용 (NLP)

1. 인스턴스 `<instance-id>`가 "running" 상태이고 리전 `<region>`에서 EC2의 AWS 서비스 상태가 정상인지 확인합니다.
2. EC2 인스턴스 `<instance-id>`와 연관된 보안 그룹 `<security-group-id>`를 조회하여 SSH 포트 22 접근에 대한 인바운드 규칙을 검사하고, 소스 IP 주소 또는 CIDR 블록을 확인합니다.
3. 리전 `<region>`의 EC2 인스턴스 `<instance-id>`를 조회하여 퍼블릭 IP 주소 또는 Elastic IP 할당을 확인하고, 인스턴스가 인터넷 게이트웨이 라우트가 있는 퍼블릭 서브넷에 있는지 점검합니다.
4. 키 페어 `<key-pair-name>`이 인스턴스 `<instance-id>`에 할당된 키 페어와 일치하는지 인스턴스 키 페어 설정을 조회하여 확인합니다.
5. EC2 인스턴스 `<instance-id>`의 메타데이터 서비스 설정을 조회하여 IMDSv2 적용 설정을 확인합니다.
6. EC2 인스턴스 `<instance-id>`의 IAM 역할 설정을 조회하여 인스턴스 프로파일이 연결되어 있는지 확인하고, IAM 역할 연결을 점검합니다.
7. 인스턴스 `<instance-id>`의 EC2 시리얼 콘솔 출력에 대한 CloudWatch Logs를 조회하여 연결 에러 또는 인증 실패를 필터링합니다.
8. 인스턴스 `<instance-id>`가 포함된 서브넷의 라우트 테이블 `<route-table-id>`과 네트워크 ACL `<nacl-id>`을 조회하여 인터넷 게이트웨이로의 라우트(0.0.0.0/0 → igw-id)가 존재하고 인바운드 및 아웃바운드 규칙이 SSH 트래픽(포트 22 TCP)을 허용하는지 확인합니다.
9. VPC Flow Logs가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 인스턴스 `<instance-id>`의 포트 22로의 차단된 트래픽을 필터링합니다.

### DevOps/SRE용 (CLI)

1. 인스턴스 상태 및 AWS 서비스 상태 확인:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> --region <region> --query 'Reservations[*].Instances[*].[State.Name,InstanceId]' --output table
   aws health describe-events --filter services=EC2 --region <region>
   ```

2. SSH에 대한 보안 그룹 인바운드 규칙 확인:
   ```bash
   aws ec2 describe-security-groups --group-ids <security-group-id> --region <region> --query 'SecurityGroups[*].IpPermissions[?FromPort==`22`]' --output json
   ```

3. 퍼블릭 IP 및 서브넷 설정 확인:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> --region <region> --query 'Reservations[*].Instances[*].[PublicIpAddress,SubnetId,VpcId]' --output table
   ```

4. 키 페어 할당 확인:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> --region <region> --query 'Reservations[*].Instances[*].KeyName' --output text
   ```

5. IMDSv2 설정 확인:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> --region <region> --query 'Reservations[*].Instances[*].MetadataOptions' --output json
   ```

6. IAM 인스턴스 프로파일 확인:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> --region <region> --query 'Reservations[*].Instances[*].IamInstanceProfile' --output json
   ```

7. EC2 시리얼 콘솔 출력 조회:
   ```bash
   aws ec2 get-console-output --instance-id <instance-id> --region <region> --output text
   ```

8. 라우트 테이블 및 NACL 규칙 확인:
   ```bash
   aws ec2 describe-route-tables --route-table-ids <route-table-id> --region <region> --output table
   aws ec2 describe-network-acls --network-acl-ids <nacl-id> --region <region> --query 'NetworkAcls[*].Entries' --output json
   ```

9. 차단된 SSH 트래픽에 대한 VPC Flow Logs 조회:
   ```bash
   aws logs filter-log-events --log-group-name <vpc-flow-logs-group> --filter-pattern "REJECT <instance-id> 22" --region <region>
   ```

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전 내 EC2 서비스 가용성을 확인합니다. 서비스 상태에 이슈가 있거나 인스턴스가 "running" 상태가 아닌 경우, 인스턴스 수준의 이슈를 먼저 해결해야 합니다.

2. 플레이북 2단계의 보안 그룹 인바운드 규칙이 클라이언트 IP 주소 또는 CIDR 블록에서의 SSH(포트 22)를 허용하지 않으면, 보안 그룹 수준에서 네트워크 접근이 차단되어 있습니다. 소스 IP가 명시적으로 허용되어 있는지 확인합니다.

3. 플레이북 3단계의 인스턴스 설정에서 퍼블릭 IP 또는 Elastic IP가 없고 인스턴스가 프라이빗 서브넷에 있으면, SSH는 배스천 호스트, VPN, 또는 Systems Manager Session Manager를 통해서만 가능합니다.

4. 플레이북 8단계의 라우트 테이블에 인터넷 게이트웨이로의 라우트(0.0.0.0/0 -> igw-*)가 없으면, 퍼블릭 서브넷의 인스턴스가 SSH를 포함한 인바운드 인터넷 트래픽을 수신할 수 없습니다.

5. 플레이북 8단계의 네트워크 ACL에 포트 22 또는 임시 포트(1024-65535)에 대한 Deny 규칙이 있으면, NACL 규칙이 SSH 트래픽을 차단하고 있습니다. NACL은 상태 비저장이므로 인바운드와 아웃바운드 규칙이 모두 필요합니다.

6. 플레이북 4단계의 키 페어가 연결 시도에 사용된 키 페어와 일치하지 않으면, 타임아웃이 아닌 "Permission denied" 에러로 인증이 실패합니다.

7. 플레이북 5단계의 IMDSv2 설정에서 IMDSv2가 필수이고 홉 제한이 1인 상태에서 프록시 또는 배스천을 통해 SSH를 시도하면, 메타데이터 서비스 요청이 실패하여 인스턴스 설정에 영향을 줄 수 있습니다.

8. 플레이북 9단계의 VPC Flow Logs에서 인스턴스 포트 22로의 트래픽에 REJECT 액션이 표시되면, 거부하는 컴포넌트를 파악합니다(보안 그룹은 REJECT로 표시, NACL은 명시적 규칙 번호와 함께 REJECT로 표시).

9. 플레이북 7단계의 시리얼 콘솔 출력에서 부팅 실패 또는 SSH 데몬 에러가 표시되면, 인스턴스 수준의 SSH 서비스가 제대로 실행되지 않고 있습니다.

수집된 데이터에서 상관관계를 찾을 수 없는 경우: VPC Flow Log 조회 기간을 30분으로 확장하고, 클라이언트 측 방화벽 규칙을 확인하고, 인스턴스 수준의 iptables/firewalld 규칙을 점검하고, SSH 데몬 설정을 검사합니다. 연결 실패는 호스트 기반 방화벽, SSH 서비스 크래시, 또는 디스크 풀로 인한 SSH 데몬 작동 불가로 인해 발생할 수 있습니다.
