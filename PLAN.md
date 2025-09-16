# PLAN.md - 코드 셀 추가 및 자동 main 메소드 래핑 기능 구현
*작성일: 2025-09-16*

## 요구사항
1. **코드 셀 추가 기능**: 사용자가 새로운 Java 코드 셀을 웹 인터페이스에서 동적으로 추가
2. **자동 main 메소드 래핑**: main 메소드가 없는 코드를 자동으로 `class Main { public static void main... }` 구조로 감싸서 실행

## 구현 계획

### 1. 백엔드 (Python) - 자동 main 메소드 래핑
**파일**: `src/javanotebook/executor.py`

**구현 내용**:
- `wrap_code_with_main()` 메소드 추가
  - main 메소드가 없는 코드를 감지
  - 코드를 Main 클래스의 main 메소드 내부에 자동 배치
- `execute_java_code()` 메소드 수정
  - 실행 전 main 메소드 존재 여부 확인
  - 없으면 자동 래핑 적용

**예시 래핑 결과**:
```java
// 입력 코드:
System.out.println("Hello World");
int x = 5 + 3;

// 자동 래핑 결과:
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
        int x = 5 + 3;
    }
}
```

### 2. 프론트엔드 (JavaScript) - 동적 셀 추가
**파일**: `src/javanotebook/static/js/notebook.js`

**구현 내용**:
- `addNewCodeCell()` 메소드 추가
  - 새로운 코드 셀 HTML 생성
  - 고유한 셀 ID 할당
  - CodeMirror 에디터 초기화
- 셀 ID 관리 시스템 개선
  - 동적 생성된 셀들의 고유 ID 보장
- 이벤트 바인딩
  - 새로운 셀의 실행/검증 버튼 기능 연결

### 3. 웹 인터페이스 (HTML/CSS) - UI 개선
**파일**: 
- `src/javanotebook/templates/notebook.html`
- `src/javanotebook/static/css/style.css`

**구현 내용**:
- "코드 셀 추가" 버튼 추가
- 새로운 UI 요소 스타일링
- 반응형 디자인 고려

### 4. 선택적 백엔드 확장
**파일**: `src/javanotebook/models.py` (필요시)

**구현 내용**:
- 새로운 요청/응답 모델 (필요한 경우에만)

## 기술적 세부사항

### 자동 main 메소드 래핑 로직
1. **감지**: 정규식으로 `public static void main` 메소드 존재 확인
2. **래핑**: 없으면 코드를 Main 클래스의 main 메소드 내부에 배치
3. **예외 처리**: 이미 클래스 선언이 있는 경우 래핑하지 않음

### 동적 셀 추가 로직
1. **HTML 생성**: 템플릿 기반으로 새로운 셀 HTML 구조 생성
2. **DOM 삽입**: 기존 노트북에 새로운 셀 추가
3. **에디터 초기화**: CodeMirror 인스턴스 생성 및 설정
4. **이벤트 연결**: 실행/검증 버튼 기능 바인딩

### 셀 ID 관리
- 기존 셀: `cell-{counter}` 형식
- 새로운 셀: `cell-new-{timestamp}` 형식으로 충돌 방지

## 구현 순서
1. ✅ 계획 수립 및 PLAN.md 작성
2. 🔄 자동 main 래핑 로직 구현 (executor.py)
3. ⏳ 동적 셀 추가 기능 구현 (notebook.js)
4. ⏳ UI 버튼 및 스타일 추가 (HTML/CSS)
5. ⏳ 통합 테스트 및 디버깅

## 예상 이점
- **빠른 프로토타이핑**: main 메소드 없이도 간단한 Java 코드 테스트 가능
- **유연한 노트북**: 런타임에 코드 셀 추가로 더 동적인 학습 환경
- **사용성 향상**: 반복적인 boilerplate 코드 작성 불필요

## 주의사항
- 자동 래핑 시 기존 import 문, 클래스 선언 등과의 충돌 방지
- 동적 추가된 셀의 상태 관리 (실행 결과, 에러 표시 등)
- 브라우저 호환성 고려 (CodeMirror 초기화)