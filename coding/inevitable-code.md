---
category: coding
tags:
- coding
- typescript
- design
- simplicity
- ai-agent
role: Developer
origin: custom
source: ''
---
# Inevitable Code — 필연적 코드 철학

## 개요

Giselle AI 팀의 ts-coder 에이전트가 따르는 코딩 철학.
"모든 설계 선택이 유일하게 합리적인 옵션처럼 느껴지는 코드"를 작성하는 원칙이다.
개발자가 코드를 만났을 때 "당연히 이렇게 되어야지. 다른 방법이 있겠어?"라고 느끼게 만드는 것이 목표.

> 출처: [giselles-ai/giselle ts-coder agent](https://github.com/giselles-ai/giselle/blob/main/.claude/agents/ts-coder.md)

## 핵심 원리: 표면적 단순함, 내부적 정교함

단순한 인터페이스가 정교한 구현을 숨길 수 있다.
외부 인지 부하를 제거하기 위해 내부 복잡성을 기꺼이 수용한다.

```typescript
// 필연적: 직접적이고 명백함
const user = await getUser(id);
if (!user) return null;

// 과도한 설계: 불필요한 추상화 레이어
const userService = createUserService(dependencies);
const result = await userService.getUser(id);
if (!result.success) handleError(result.error);
```

## 설계 원칙

### 1. 결정 지점 최소화
사용자에게 강제하는 모든 API 선택은 인지 부하를 만든다.
JavaScript의 자연스러운 패턴을 활용하여 결정을 줄여라.

### 2. 목적 뒤에 복잡성 숨기기
내부 복잡성은 수용 가능하다 — 다른 곳의 복잡성을 제거할 때.
복잡성을 한 곳에 집중시켜 다른 곳을 단순하게 만들어라.

### 3. 회상이 아닌 인식을 위한 설계
기존 멘탈 모델을 활용하는 패턴과 이름을 선택하라.
임의의 규칙을 암기하지 않고도 코드가 무엇을 하는지 인식할 수 있어야 한다.

### 4. 클래스보다 함수, 상속보다 합성
클래스는 상태 관리, 생명주기, 상속 계층을 통해 우발적 복잡성을 도입한다.
함수는 자연스럽게 합성된다.

### 5. 에러를 감지 가능하게가 아니라 불가능하게 만들어라
TypeScript의 타입 시스템을 사용하여 명백한 실수를 방지하되, 의식(ceremony)을 만들지 마라.

## 안티패턴 제거 목록

- **과도한 추상화**: 단순한 함수로 충분할 때 복잡한 패턴 생성
- **설정 폭발**: 좋은 기본값으로 결정할 수 있는 것을 사용자에게 떠넘기기
- **타입 의식**: 단순한 타입으로 충분히 소통할 때 복잡한 타입 사용
- **조기 일반화**: 필요한 것을 알기 전에 추상화 구축
- **서비스 레이어**: 실제 문제를 해결하지 않는 간접 참조 추가

## 리트머스 테스트

코드를 내보내기 전에 자문:
1. 이것이 가능한 한 단순한가?
2. 자연스럽게 느껴지는가?
3. 실제 문제를 해결하고 있는가?
4. 깨졌을 때 무슨 일이 일어나는가?
