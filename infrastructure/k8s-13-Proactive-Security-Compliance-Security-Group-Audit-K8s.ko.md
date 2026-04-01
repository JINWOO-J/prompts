---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/Security-Group-Audit-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- audit
- compliance
- group
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-pod
- security
---

# Network Policy Audit — NetworkPolicy 감사

## 의미

NetworkPolicy 감사는 NetworkPolicy가 과도하게 허용적이거나, 잘못 구성되었거나, 보안 모범 사례를 위반하고 있음을 나타냅니다(OverlyPermissiveNetworkPolicy 또는 NetworkPolicyAuditFailed 같은 알림 발생). NetworkPolicy가 과도하게 광범위한 접근을 허용하거나, 사용되지 않는 NetworkPolicy가 존재하거나, NetworkPolicy 규칙이 최소 권한 원칙을 위반하거나, NetworkPolicy 인그레스 규칙이 모든 소스에서의 접근을 허용하거나, NetworkPolicy 이그레스 규칙이 제한되지 않은 것이 원인입니다. NetworkPolicy에서 과도하게 허용적인 규칙이 나타나고, NetworkPolicy 감사 결과에서 위반이 감지되며, 사용되지 않는 NetworkPolicy가 탐지되고, NetworkPolicy 구성이 보안 정책을 위반합니다. 이는 보안 계층과 네트워크 접근 제어에 영향을 미치며, 일반적으로 잘못 구성된 NetworkPolicy 규칙, NetworkPolicy 수명주기 관리 부재, 또는 보안 정책 위반으로 인해 발생합니다. NetworkPolicy가 컨테이너 워크로드를 보호하는 경우 컨테이너 네트워크 접근이 과도하게 허용적이고 애플리케이션에서 보안 위험이 발생할 수 있습니다.

## 영향

NetworkPolicyAuditFailed 알림 발생, OverlyPermissiveNetworkPolicy 알림 발생, 네트워크 접근이 과도하게 허용적, 보안 정책 위반, 사용되지 않는 NetworkPolicy가 리소스 소비, NetworkPolicy 규칙이 최소 권한 원칙 위반. NetworkPolicy 구성에서 과도하게 허용적인 규칙이 나타나며, NetworkPolicy가 컨테이너 워크로드를 보호하는 경우 컨테이너 네트워크 접근이 과도하게 허용적이고, Pod NetworkPolicy가 잘못 구성되며, 컨테이너 애플리케이션에서 보안 위험이 발생할 수 있습니다. 애플리케이션에서 보안 취약점 또는 무단 접근 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 모든 NetworkPolicy를 상세 조회하여 Pod 셀렉터와 정책 유형을 포함한 구성을 확인합니다.
2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 NetworkPolicy 위반, 보안 경고, 정책 관련 오류를 확인합니다.
3. 네임스페이스 <namespace>의 NetworkPolicy <network-policy-name>을 상세 조회하여 인그레스 및 이그레스 규칙, Pod 셀렉터, 규칙 제한 수준을 포함한 NetworkPolicy 구성을 검사합니다.
4. 네임스페이스 `<namespace>`의 Pod를 조회하고 NetworkPolicy 연결을 확인하여 어떤 Pod에도 연결되지 않은 사용되지 않는 NetworkPolicy를 파악합니다.
5. 네트워크 정책 컨트롤러 Pod의 로그를 조회하고 최근 7일 이내의 과도하게 허용적인 NetworkPolicy 규칙을 나타내는 트래픽 패턴을 필터링합니다.
6. NetworkPolicy 컴플라이언스 점검에 대한 보안 감사 결과를 조회하고 NetworkPolicy 구성 오류와 관련된 심각도 'HIGH' 또는 'CRITICAL' 결과를 필터링합니다.
7. NetworkPolicy 규칙 수정 타임스탬프와 보안 정책 변경 타임스탬프를 24시간 이내로 비교하고, NetworkPolicy 이벤트를 보조 증거로 사용하여 NetworkPolicy 변경이 보안 정책을 위반하는지 확인합니다.
8. NetworkPolicy `<network-policy-name>`의 규칙 사용 메트릭을 조회하고 규칙이 활발히 사용되는지 사용되지 않는지 확인하며 규칙 활용 패턴을 점검합니다.

## 진단

1. 3~4단계의 NetworkPolicy 구성을 검토합니다. 정책이 모든 네임스페이스나 모든 Pod에서의 인그레스를 허용하거나 이그레스가 제한되지 않으면 즉시 강화가 필요한 최우선 보안 문제입니다.

2. 4단계의 Pod-정책 매핑을 분석합니다. NetworkPolicy가 어떤 Pod에도 연결되지 않으면 사용되지 않는 것이며 제거하거나 적절한 Pod 셀렉터 구성을 검토해야 합니다.

3. 5단계의 네트워크 정책 컨트롤러 로그에서 과도하게 허용적인 규칙이 의도하지 않은 접근에 활발히 사용되는 트래픽 패턴이 나타나면 정책 규칙을 즉시 제한해야 합니다. 로그에서 허용되어야 할 트래픽이 거부되면 정책이 과도하게 제한적일 수 있습니다.

4. 6단계의 보안 감사 결과를 검토합니다. HIGH 또는 CRITICAL 결과가 NetworkPolicy 구성 오류와 관련되면 해결을 우선시합니다. 결과가 낮은 심각도이면 정기 유지보수의 일환으로 해결을 예약합니다.

5. 8단계의 규칙 사용 메트릭에서 매칭되지 않는 규칙이 나타나면 해당 규칙은 중복이거나 잘못 구성된 것일 수 있습니다. 규칙이 많이 매칭되면 트래픽 패턴이 의도적인 것인지 확인합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 위반을 도입했을 수 있는 최근 NetworkPolicy 수정 사항을 확인합니다. 과도하게 허용적인 구성이 특정 네임스페이스에 집중되어 있는지(국소적 구성 오류 시사) 또는 분산되어 있는지(정책 템플릿 문제 시사) 판단합니다. 지속적인 정책 유지보수를 위한 NetworkPolicy 수명주기 관리 프로세스가 존재하는지 확인합니다.
