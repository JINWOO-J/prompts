---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/High-CPU-Utilization-EC2.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- ec2
- high
- incident-response
- k8s-service
- performance
- scaling
- sts
- utilization
---

# EC2 인스턴스 높은 CPU 사용률 (High CPU Utilization)

## 의미

EC2 인스턴스가 지속적으로 높은 CPU 사용률을 경험합니다(CPUUtilizationHigh 같은 알람 트리거). CPU 집약적 프로세스가 과도한 리소스를 소비하거나, 애플리케이션 코드 비효율이 높은 CPU 사용을 유발하거나, 인스턴스 유형이 워크로드에 비해 작거나, 백그라운드 프로세스가 CPU 리소스를 경쟁하거나, CloudWatch 메트릭이 CPU 사용률이 지속적으로 임계값을 초과함을 나타내기 때문입니다. CPU 사용률 메트릭이 장기간 80-90%를 초과하고, CloudWatch 알람이 높은 CPU에 대해 트리거되며, 애플리케이션 성능이 저하됩니다. 이는 컴퓨팅 계층에 영향을 미치며 서비스 성능에 영향을 줍니다. 일반적으로 리소스 제약, 애플리케이션 비효율, 또는 인스턴스 사이징 이슈가 원인이며, 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 높은 CPU가 컨테이너 스케줄링에 영향을 줄 수 있고 애플리케이션에서 성능 저하가 발생할 수 있습니다.

## 영향

CPUUtilizationHigh 알람 발생; 애플리케이션 성능 저하; 응답 시간 증가; 사용자 대면 서비스 느려짐; 인스턴스 응답 불가; Auto Scaling이 불필요한 스케일링을 트리거할 수 있음; 인스턴스의 다른 프로세스가 CPU 리소스 부족; 시스템 안정성 저하. 인스턴스 CPU 사용률이 지속적으로 80-90% 초과; 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 컨테이너 스케줄링에 영향을 줄 수 있고 애플리케이션에서 성능 저하 발생 가능; 애플리케이션 워크플로우가 느려지거나 실패할 수 있음; 사용자 대면 서비스에서 지연 증가 경험.

## 플레이북

1. 인스턴스 `<instance-id>`가 존재하고 "running" 상태이며, 리전 `<region>`에서 EC2의 AWS 서비스 상태가 정상인지 확인합니다.
2. EC2 인스턴스 `<instance-id>`의 CloudWatch 메트릭(CPUUtilization 포함)을 최근 1시간 동안 조회하여 CPU 사용 패턴과 급증을 파악하고, 시간에 따른 CPU 추이를 분석합니다.
3. 리전 `<region>`의 EC2 인스턴스 `<instance-id>`를 조회하여 인스턴스 유형 설정을 검사하고, 인스턴스 유형이 워크로드에 적합한지 확인합니다.
4. 인스턴스 `<instance-id>`의 애플리케이션 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 CPU 집약적 작업을 나타내는 에러 패턴 또는 성능 관련 로그 항목(프로세스 수준 CPU 사용 지표 포함)을 필터링합니다.
5. 인스턴스 `<instance-id>`와 연관된 CloudWatch 알람을 CPUUtilization 메트릭으로 조회하고 ALARM 상태의 알람을 확인하며, 알람 임계값 설정을 검증합니다.
6. 리전 `<region>`에서 `<instance-id>`와 동일한 인스턴스 유형의 EC2 인스턴스를 나열하고 CPU 사용률 패턴을 비교하여 이슈가 인스턴스별 문제인지 판단하고, 유사 인스턴스 간 CPU 사용률을 분석합니다.
7. 인스턴스 `<instance-id>`와 연관된 Auto Scaling 그룹 `<asg-name>`을 조회하여 스케일링 정책 및 대상 추적 설정을 검사하고, 높은 CPU가 스케일링 액션을 트리거하는지 확인하며, 스케일링 정책 CPU 임계값을 점검합니다.
8. EC2 인스턴스 `<instance-id>`의 CloudWatch 메트릭(NetworkIn, NetworkOut, DiskReadOps 포함)을 조회하여 높은 CPU가 I/O 작업과 상관관계가 있는지 파악하고, CPU와 I/O 메트릭 간의 상관관계를 분석합니다.
9. 인스턴스 `<instance-id>`의 시스템 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 프로세스 관련 에러 또는 리소스 경합 패턴을 필터링하고, 백그라운드 프로세스 이슈를 확인합니다.

## 진단

1. 플레이북 5단계의 CloudWatch 알람 이력을 분석하여 CPUUtilizationHigh 알람이 처음 ALARM 상태에 진입한 시점을 파악합니다. 이 타임스탬프가 근본 원인 분석의 상관관계 기준선을 확립합니다.

2. 플레이북 4단계의 애플리케이션 로그에서 알람 타임스탬프 전후로 에러 패턴 또는 성능 관련 항목이 표시되면, 특정 애플리케이션 작업이 CPU 급증을 유발하고 있을 가능성이 높습니다.

3. 플레이북 6단계에서 유사 인스턴스 간 CPU 패턴을 비교하여 이슈가 하나의 인스턴스에 국한된 경우, 근본 원인은 인스턴스별 문제(폭주 프로세스, 악성코드, 또는 로컬 설정)입니다. 여러 인스턴스가 영향을 받으면, 원인은 워크로드 관련입니다.

4. 플레이북 2단계의 CloudWatch 메트릭에서 점진적 증가가 아닌 갑작스러운 CPU 급증이 보이면, I/O 메트릭(플레이북 8단계)과 상관관계를 분석합니다. NetworkIn/Out 또는 DiskReadOps가 동시에 급증했다면, 증가된 I/O 워크로드가 CPU 사용을 유발하고 있습니다.

5. 인스턴스가 버스터블 유형(T 시리즈)이고 CloudWatch에서 지속적인 높은 사용 후 CPU가 하락하는 추세를 보이면, CPU 크레딧 잔액을 확인합니다. 크레딧 고갈은 높은 CPU 대기 시간으로 나타나는 성능 스로틀링을 유발합니다.

6. 플레이북 7단계의 Auto Scaling 그룹에서 알람 시점 전후로 스케일링 활동이 표시되지만 새 인스턴스도 높은 CPU를 보이면, 워크로드가 현재 용량을 초과하며 더 많은 인스턴스 또는 더 큰 인스턴스 유형이 필요합니다.

7. 플레이북 9단계의 시스템 로그에서 리소스 경합 또는 백그라운드 프로세스 에러가 표시되면, 시스템 수준 프로세스가 애플리케이션 워크로드와 CPU 리소스를 경쟁하고 있습니다.

상관관계를 찾을 수 없는 경우: 분석을 4시간으로 확장하고, 프로세스 수준 CPU 메트릭을 검토하고, 메모리 압박으로 인한 CPU 스래싱을 확인하고, EBS 볼륨 IOPS 제한이 CPU 대기 시간에 영향을 미치는지 검증하고, 외부 병목에 대한 데이터베이스 쿼리 성능을 검사합니다.
