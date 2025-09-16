"""Pytest configuration and fixtures for Java Notebook tests."""

import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from javanotebook.main import create_app
from javanotebook.parser import NotebookParser


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_notebook_content():
    """Sample notebook content for testing."""
    return """# Test Notebook

This is a sample notebook for testing.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

## Another Section

Some more markdown content.

```java
public class Calculator {
    public static void main(String[] args) {
        int a = 5;
        int b = 3;
        System.out.println("Sum: " + (a + b));
    }
}
```
"""


@pytest.fixture
def temp_notebook_file(sample_notebook_content):
    """Create a temporary notebook file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_notebook_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def notebook_parser():
    """Create a NotebookParser instance."""
    return NotebookParser()


@pytest.fixture
def valid_java_code():
    """Sample valid Java code for testing."""
    return """public class TestClass {
    public static void main(String[] args) {
        System.out.println("Test output");
    }
}"""


@pytest.fixture
def invalid_java_code():
    """Sample invalid Java code for testing."""
    return """public class TestClass {
    // Missing main method
    public void someMethod() {
        System.out.println("This won't work");
    }
}"""