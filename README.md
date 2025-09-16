# 🚀 Java Notebook (jvnb)

[![PyPI version](https://badge.fury.io/py/javanotebook.svg)](https://badge.fury.io/py/javanotebook)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Java Notebook (jvnb)은 Java 코드를 Jupyter 스타일의 노트북 환경에서 실행할 수 있게 해주는 Python 패키지입니다. 마크다운 형식으로 작성된 파일에서 Java 코드 블록을 실행하고 결과를 웹 인터페이스에서 바로 확인할 수 있습니다.

## ✨ 주요 기능

- 📝 **마크다운 기반**: 표준 마크다운 형식으로 문서와 코드를 함께 작성
- ☕ **Java 코드 실행**: 웹 인터페이스에서 Java 코드를 즉시 컴파일하고 실행
- 🌐 **FastAPI 기반**: 현대적이고 빠른 웹 서버와 API
- 🎨 **서버사이드 렌더링**: Python markdown + Pygments로 구문 강조
- ⌨️ **향상된 편집기**: CodeMirror 기반 에디터와 키보드 단축키 지원
- 🔍 **구조화된 에러**: 컴파일/런타임 오류의 상세한 표시
- ➕ **동적 셀 추가**: 런타임에 새로운 코드 셀을 추가/삭제
- 🚀 **자동 main 래핑**: main 메소드 없는 간단한 코드도 즉시 실행
- 📤 **완전한 출력**: stdout과 stderr 모두 실행 결과에 표시
- 📦 **간편한 설치**: pip를 통한 원클릭 설치

## 🛠 설치 요구사항

- **Python**: 3.8 이상
- **JDK**: Java 8 이상 (javac, java 명령어가 PATH에 포함되어야 함)

## 📦 설치

```bash
pip install javanotebook
```

## 🚀 사용법

### 1. 노트북 파일 생성

마크다운 형식으로 Java 코드가 포함된 파일을 작성합니다:

```markdown
# 내 첫 번째 Java 노트북

안녕하세요! 이것은 마크다운 셀입니다.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Java Notebook!");
    }
}
```

계산기 예제입니다:

```java
public class Calculator {
    public static void main(String[] args) {
        int a = 10;
        int b = 5;
        
        System.out.println("덧셈: " + a + " + " + b + " = " + (a + b));
        System.out.println("뺄셈: " + a + " - " + b + " = " + (a - b));
        System.out.println("곱셈: " + a + " * " + b + " = " + (a * b));
        System.out.println("나눗셈: " + a + " / " + b + " = " + (a / b));
    }
}
```

**🚀 NEW: 간단한 코드는 main 메소드 없이도 실행 가능!**

```java
// 이런 간단한 코드도 바로 실행됩니다 (자동으로 Main 클래스로 감싸짐)
System.out.println("Hello, World!");
int x = 10;
int y = 20;
System.out.println("합계: " + (x + y));
```
```

### 2. 노트북 실행

```bash
# Makefile을 사용한 간편 실행 (추천)
make dev                    # 기본 예제로 서버 시작
make example-algorithms     # 알고리즘 예제
make example-data-structures # 자료구조 예제

# 직접 명령어 사용
python -m javanotebook my_notebook.md

# 설치된 패키지 명령어
javanotebook my_notebook.md

# 옵션과 함께 실행
python -m javanotebook examples/basic_java.md --port 8080 --debug
```

### 3. 웹 브라우저에서 확인

서버가 시작되면 자동으로 브라우저가 열리고 `http://localhost:8000`에서 노트북을 확인할 수 있습니다.

### 4. 주요 기능 사용법

#### 🆕 동적 셀 추가
- 헤더에 있는 **"+ 코드 셀 추가"** 버튼을 클릭하여 새로운 Java 코드 셀을 언제든지 추가
- 각 셀에는 **"삭제"** 버튼이 있어 불필요한 셀 제거 가능

#### 🚀 자동 main 메소드 래핑
- `public static void main` 메소드가 없는 간단한 Java 코드도 자동으로 실행 가능
- 시스템이 자동으로 `Main` 클래스와 `main` 메소드로 코드를 감싸서 실행

#### 📤 완전한 출력 표시
- `System.out.println()` (표준 출력)
- `System.err.println()` (표준 에러) 
- 모든 출력이 "실행 결과"에 함께 표시됩니다

### 5. 키보드 단축키

```
실행:
• Ctrl+Enter / Shift+Enter : 현재 셀 실행
• Ctrl+Shift+Enter : 모든 셀 실행
• Ctrl+Shift+V : 현재 셀 검증

편집:
• Ctrl+/ : 주석 토글
• Ctrl+Shift+F : 코드 포맷팅
• Ctrl+] : 들여쓰기 증가

기타:
• F1 : 키보드 단축키 도움말
• Shift+Esc : 모든 출력 지우기
```

## 📋 예제

프로젝트에 포함된 예제 파일들:

- `examples/basic_java.md`: 기본 Java 문법 예제
- `examples/data_structures.md`: 자료구조 예제
- `examples/algorithms.md`: 알고리즘 예제

```bash
# 예제 실행
make example-basic          # 또는 python -m javanotebook examples/basic_java.md
make example-algorithms     # 또는 python -m javanotebook examples/algorithms.md  
make example-data-structures # 또는 python -m javanotebook examples/data_structures.md
```

## 🎯 사용 시나리오

### 교육용
- Java 프로그래밍 강의 자료 작성
- 학생들의 코딩 실습 과제
- 알고리즘 설명과 구현 예제

### 문서화
- 코드 예제가 포함된 기술 문서
- API 사용법 가이드
- 튜토리얼 작성

### 프로토타이핑
- 간단한 Java 코드 테스트
- 알고리즘 검증
- 코드 스니펫 공유

## ⚙️ 고급 사용법

### 명령행 옵션

```bash
# 포트 지정
python -m javanotebook my_notebook.md --port 8080

# 호스트 바인딩 (외부 접속 허용)
python -m javanotebook my_notebook.md --host 0.0.0.0

# 디버그 모드
python -m javanotebook my_notebook.md --debug

# 자동 브라우저 열기 비활성화
python -m javanotebook my_notebook.md --no-browser
```

### 개발 명령어

```bash
# 개발 환경 설정
make setup                  # 개발 의존성 설치 + pre-commit 설정

# 코드 품질 검사
make check                  # 전체 품질 검사 (lint + typecheck + test)
make lint                   # 코드 린팅
make format                 # 코드 포맷팅
make test                   # 테스트 실행

# Java 환경 확인
make check-java             # Java JDK 설치 확인
```

## 🔧 개발자를 위한 정보

### 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yourusername/javanotebook.git
cd javanotebook

# 개발 모드로 설치
pip install -e .

# 테스트 실행
pytest

# 코드 품질 검사
black src/
flake8 src/
mypy src/
```

### 아키텍처

Java Notebook은 다음과 같은 구조로 작동합니다:

1. **파서**: 마크다운 파일을 파싱하여 서버사이드에서 HTML로 렌더링
2. **실행 엔진**: Java 코드를 임시 파일로 저장하고 JDK를 사용해 컴파일/실행
3. **웹 서버**: FastAPI 기반 현대적 웹 서버와 RESTful API
4. **프론트엔드**: CodeMirror 기반 고급 편집기와 향상된 UI/UX

### 주요 개선사항

- **서버사이드 렌더링**: Python markdown + Pygments로 성능과 보안 향상
- **구조화된 에러 표시**: 컴파일/런타임 오류의 상세한 분석과 표시
- **키보드 단축키**: Jupyter와 유사한 워크플로 지원
- **향상된 편집기**: 자동 크기 조정, 문법 강조, 검색 기능

## 🚨 제한사항

- ~~각 Java 코드 셀은 독립적인 `public static void main` 메소드를 포함해야 합니다~~ ✅ **해결됨**: 간단한 코드는 자동 래핑 지원
- 셀 간 변수나 상태 공유는 지원되지 않습니다
- JDK가 시스템에 설치되어 있어야 합니다
- 현재 단일 파일 Java 프로그램만 지원됩니다

## 🛣 로드맵

### 완료된 기능 ✅
- [x] FastAPI 기반 웹 서버
- [x] 서버사이드 마크다운 렌더링
- [x] Pygments 문법 강조
- [x] 구조화된 에러 메시지 표시
- [x] CodeMirror 기반 편집기
- [x] 키보드 단축키 지원
- [x] **NEW (2025-09-16)**: 동적 코드 셀 추가/삭제 기능
- [x] **NEW (2025-09-16)**: 자동 main 메소드 래핑
- [x] **NEW (2025-09-16)**: stdout/stderr 완전한 출력 표시
- [x] **NEW (2025-09-16)**: 향상된 런타임 에러 표시

### 향후 계획 📋
- [ ] 멀티파일 Java 프로젝트 지원
- [ ] 외부 라이브러리 import 지원  
- [ ] 셀 간 변수 공유 기능 (JShell 활용)
- [ ] 실행 결과 시각화 도구
- [ ] WebSocket 기반 실시간 통신
- [ ] VS Code 확장 개발
- [ ] Docker 기반 Java 환경 지원
- [ ] 셀 재정렬 및 마크다운 셀 편집 기능
- [ ] 코드 자동완성 및 IntelliSense 지원

## 🤝 기여하기

기여를 환영합니다! 다음과 같은 방법으로 참여할 수 있습니다:

1. 이슈 리포트
2. 기능 제안
3. 풀 리퀘스트
4. 문서 개선

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 📞 지원

- 🐛 버그 리포트: [GitHub Issues](https://github.com/yourusername/javanotebook/issues)
- 💡 기능 요청: [GitHub Discussions](https://github.com/yourusername/javanotebook/discussions)
- 📧 이메일: your.email@example.com

## 🙏 감사의 말

- [Jupyter Project](https://jupyter.org/)에서 영감을 받았습니다
- [CodeMirror](https://codemirror.net/) 코드 편집기를 사용합니다
- [Flask](https://flask.palletsprojects.com/) 웹 프레임워크를 사용합니다

---

**Java Notebook**으로 더 즐거운 Java 학습과 개발을 경험해보세요! 🎉