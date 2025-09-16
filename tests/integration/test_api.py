"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from javanotebook.main import create_app


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def app(self, temp_notebook_file):
        """Create app with a test notebook file."""
        return create_app(temp_notebook_file)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Java Notebook"
    
    def test_api_health_endpoint(self, client):
        """Test the API health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "java_available" in data
    
    def test_execute_valid_java_code(self, client):
        """Test executing valid Java code."""
        java_code = """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}"""
        
        response = client.post(
            "/api/v1/execute",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Hello, World!" in data["stdout"]
        assert data["stderr"] == ""
        assert "execution_time" in data
    
    def test_execute_java_code_with_error(self, client):
        """Test executing Java code with compilation error."""
        java_code = """public class BadCode {
    public static void main(String[] args) {
        System.out.println("Missing semicolon")  // Missing semicolon
    }
}"""
        
        response = client.post(
            "/api/v1/execute",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["compilation_error"] is not None
        assert "execution_time" in data
    
    def test_execute_invalid_structure(self, client):
        """Test executing Java code without proper structure."""
        java_code = """public class NoMain {
    public void someMethod() {
        System.out.println("No main method");
    }
}"""
        
        response = client.post(
            "/api/v1/execute",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "main method" in data["error_message"].lower()
    
    def test_execute_empty_code(self, client):
        """Test executing empty code."""
        response = client.post(
            "/api/v1/execute",
            json={"code": ""}
        )
        
        # This should return a validation error
        assert response.status_code == 422  # Validation error
    
    def test_validate_valid_java_code(self, client):
        """Test validating valid Java code."""
        java_code = """public class ValidCode {
    public static void main(String[] args) {
        System.out.println("Valid code");
    }
}"""
        
        response = client.post(
            "/api/v1/validate",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["class_name"] == "ValidCode"
        assert data["has_main_method"] is True
        assert len(data["errors"]) == 0
    
    def test_validate_invalid_java_code(self, client):
        """Test validating invalid Java code."""
        java_code = """public class InvalidCode {
    public void notMainMethod() {
        System.out.println("Invalid code");
    }
}"""
        
        response = client.post(
            "/api/v1/validate",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is False
        assert data["class_name"] == "InvalidCode"
        assert data["has_main_method"] is False
        assert len(data["errors"]) > 0
    
    def test_index_page(self, client):
        """Test the main index page."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Check that the response contains expected HTML elements
        content = response.text
        assert "Java Notebook" in content
        assert "notebook" in content.lower()
    
    def test_execute_with_cell_id(self, client):
        """Test executing code with a cell ID."""
        java_code = """public class TestWithId {
    public static void main(String[] args) {
        System.out.println("Test with cell ID");
    }
}"""
        
        response = client.post(
            "/api/v1/execute",
            json={
                "code": java_code,
                "cell_id": "test-cell-123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_malformed_request(self, client):
        """Test handling of malformed requests."""
        # Missing required 'code' field
        response = client.post(
            "/api/v1/execute",
            json={"cell_id": "test"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_java_runtime_error(self, client):
        """Test handling Java runtime errors."""
        java_code = """public class RuntimeError {
    public static void main(String[] args) {
        int[] arr = new int[1];
        System.out.println(arr[10]); // Array index out of bounds
    }
}"""
        
        response = client.post(
            "/api/v1/execute",
            json={"code": java_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should compile successfully but fail at runtime
        assert data["success"] is False
        assert data["compilation_error"] is None
        assert "error_message" in data or data["stderr"] != ""