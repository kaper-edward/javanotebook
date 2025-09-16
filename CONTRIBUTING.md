# Contributing to Java Notebook

Java Notebook에 기여해주셔서 감사합니다! 이 가이드는 프로젝트에 기여하는 방법을 설명합니다.

## 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- JDK 8 이상 (javac, java 명령어가 PATH에 포함되어야 함)
- Git

### 로컬 개발 환경 설정

1. **저장소 클론**
```bash
git clone https://github.com/yourusername/javanotebook.git
cd javanotebook
```

2. **가상 환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. **개발 의존성 설치**
```bash
make install-dev
# 또는
pip install -e ".[dev]"
pre-commit install
```

4. **Java 설치 확인**
```bash
make check-java
```

5. **개발 서버 테스트**
```bash
make dev
```

## 개발 워크플로

### 코드 스타일

이 프로젝트는 다음 도구들을 사용하여 코드 품질을 유지합니다:

- **Black**: 코드 포맷팅
- **isort**: import 정렬
- **flake8**: 린팅
- **mypy**: 타입 체킹

### 코드 품질 검사

```bash
# 모든 품질 검사 실행
make check

# 개별 검사
make lint       # flake8 린팅
make format     # black + isort 포맷팅
make typecheck  # mypy 타입 체킹
```

### Pre-commit Hooks

Pre-commit hooks가 설정되어 있어 커밋 시 자동으로 코드 품질 검사가 실행됩니다:

```bash
# 수동으로 pre-commit 실행
make pre-commit
```

## 테스트

### 테스트 실행

```bash
# 모든 테스트
make test

# 단위 테스트만
make test-unit

# 통합 테스트만
make test-integration

# 커버리지 포함 테스트
make coverage
```

### 새로운 테스트 작성

- 단위 테스트: `tests/unit/` 디렉토리에 추가
- 통합 테스트: `tests/integration/` 디렉토리에 추가
- 테스트 파일명은 `test_*.py` 형식으로 작성
- pytest fixtures는 `conftest.py`에 정의

## 기여 프로세스

### 1. 이슈 생성

새로운 기능이나 버그 수정을 위해 먼저 GitHub 이슈를 생성해주세요:

- **Bug Report**: 버그 발견 시
- **Feature Request**: 새로운 기능 제안
- **Documentation**: 문서 개선

### 2. 브랜치 생성

```bash
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/bug-description
```

브랜치 명명 규칙:
- `feature/`: 새로운 기능
- `fix/`: 버그 수정
- `docs/`: 문서 개선
- `refactor/`: 리팩토링

### 3. 개발 및 테스트

```bash
# 코드 변경 후
make format     # 코드 포맷팅
make check      # 품질 검사 및 테스트
```

### 4. 커밋

커밋 메시지는 다음 형식을 따라주세요:

```
type(scope): description

Longer description if needed

Fixes #123
```

커밋 타입:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스 등의 변경

### 5. Pull Request

1. 브랜치를 GitHub에 push
2. Pull Request 생성
3. PR 템플릿을 작성
4. 코드 리뷰 받기
5. 피드백 반영 후 merge

## 코딩 가이드라인

### Python 코딩 스타일

- [PEP 8](https://pep8.org/) 준수
- Black 포맷터 사용 (88자 라인 길이)
- Type hints 사용 권장
- Docstring 작성 (Google 스타일)

### 아키텍처 가이드라인

- **단일 책임 원칙**: 각 클래스/함수는 하나의 책임만
- **의존성 주입**: FastAPI의 Depends 활용
- **에러 핸들링**: 적절한 예외 처리 및 HTTP 상태 코드
- **비동기 프로그래밍**: async/await 패턴 사용

### 새로운 기능 추가 시 고려사항

1. **API 설계**: RESTful API 원칙 준수
2. **테스트 작성**: 단위 테스트 및 통합 테스트 필수
3. **문서 업데이트**: README, CLAUDE.md 등 관련 문서 업데이트
4. **예제 추가**: 필요시 examples/ 디렉토리에 예제 추가
5. **하위 호환성**: 기존 API 호환성 유지

## 문서화

### 코드 문서화

```python
def execute_java_code(self, java_code: str) -> ExecutionResult:
    """Execute Java code and return results.
    
    Args:
        java_code: The Java source code to execute
        
    Returns:
        ExecutionResult containing stdout, stderr, and execution status
        
    Raises:
        CompilationError: If Java code fails to compile
        ExecutionError: If compiled code fails to execute
    """
```

### README 및 가이드 업데이트

새로운 기능 추가 시 다음 문서들을 업데이트해주세요:

- `README.md`: 사용법 및 예제
- `CLAUDE.md`: 개발자 가이드라인
- `examples/`: 새로운 예제 노트북

## 릴리스 프로세스

1. 버전 번호 업데이트 (`pyproject.toml`, `__init__.py`)
2. CHANGELOG 작성
3. 태그 생성 및 GitHub Release
4. PyPI 배포 (`make upload`)

## 질문 및 지원

- **GitHub Issues**: 버그 리포트, 기능 요청
- **GitHub Discussions**: 일반적인 질문, 아이디어 논의
- **Email**: 프로젝트 관리자에게 직접 연락

## 행동 강령

이 프로젝트는 모든 기여자가 존중받는 환경을 유지하기 위해 [Contributor Covenant](https://www.contributor-covenant.org/) 행동 강령을 따릅니다.

## 라이선스

기여하신 코드는 프로젝트의 MIT 라이선스 하에 배포됩니다.

---

Java Notebook 프로젝트에 기여해주셔서 다시 한 번 감사드립니다! 🎉