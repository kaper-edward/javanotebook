# Java Package Support Test

This notebook tests the new package support functionality.

## Test 1: Calculator Class (Utility Package)

This class provides basic calculation functionality and lives in the `com.example.util` package.

```java
package com.example.util;

/**
 * 간단한 계산 기능을 제공하는 클래스입니다.
 * 외부 패키지에서 사용할 수 있도록 public으로 선언되었습니다.
 */
public class Calculator {
    /**
     * 두 정수를 더한 결과를 반환합니다.
     * @param a 첫 번째 정수
     * @param b 두 번째 정수
     * @return a와 b의 합
     */
    public int add(int a, int b) {
        return a + b;
    }

    /**
     * 두 정수를 곱한 결과를 반환합니다.
     * @param a 첫 번째 정수
     * @param b 두 번째 정수
     * @return a와 b의 곱
     */
    public int multiply(int a, int b) {
        return a * b;
    }
}
```

## Test 2: MainApp Class (Main Package)

This is the main application that uses the Calculator class from a different package.

```java
package com.example.main;

// 다른 패키지에 있는 Calculator 클래스를 import
import com.example.util.Calculator;

/**
 * 애플리케이션의 시작점 역할을 하는 메인 클래스입니다.
 */
public class MainApp {
    public static void main(String[] args) {
        // Calculator 객체 생성 (다른 패키지에서 import됨)
        Calculator calc = new Calculator();

        // 덧셈 테스트
        int sumResult = calc.add(5, 3);
        System.out.println("5 + 3 = " + sumResult);

        // 곱셈 테스트
        int multiplyResult = calc.multiply(4, 7);
        System.out.println("4 × 7 = " + multiplyResult);

        System.out.println("패키지 지원 기능이 정상적으로 작동합니다!");
    }
}
```

## Test 3: Legacy Compatibility (No Package)

This test ensures that code without packages still works as before.

```java
public class SimpleTest {
    public static void main(String[] args) {
        System.out.println("Hello from legacy code without packages!");
        int result = 10 + 20;
        System.out.println("10 + 20 = " + result);
    }
}
```

## Test 4: Auto-wrapped Code (No Package, No Main)

This tests that simple statements are still auto-wrapped correctly.

```java
// 이 코드는 자동으로 Main 클래스와 main 메소드로 감싸집니다
String message = "Auto-wrapped code test";
System.out.println(message);
int x = 15;
int y = 25;
System.out.println("Sum: " + (x + y));
```

## Expected Results

When this notebook is executed:

1. **Calculator class**: Should compile successfully and be available for import
2. **MainApp class**: Should successfully import Calculator and produce output:
   ```
   5 + 3 = 8
   4 × 7 = 28
   패키지 지원 기능이 정상적으로 작동합니다!
   ```
3. **SimpleTest class**: Should work as before (legacy compatibility)
4. **Auto-wrapped code**: Should be wrapped in Main class and execute properly

This demonstrates that the package support feature works correctly while maintaining backward compatibility.