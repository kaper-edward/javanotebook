# 기본 Java 프로그래밍 예제

이 노트북은 Java의 기본 문법과 개념들을 다룹니다.

## Hello World

가장 기본적인 Java 프로그램입니다.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("안녕하세요, Java Notebook입니다!");
        System.out.println("Hello, Java Notebook!");
    }
}
```

## 변수와 데이터 타입

Java의 기본 데이터 타입들을 살펴보겠습니다.

```java
public class DataTypes {
    public static void main(String[] args) {
        // 정수형
        int age = 25;
        long population = 51800000L;
        
        // 실수형
        double height = 175.5;
        float weight = 70.2f;
        
        // 문자형
        char grade = 'A';
        
        // 불린형
        boolean isStudent = true;
        
        // 문자열
        String name = "홍길동";
        
        System.out.println("이름: " + name);
        System.out.println("나이: " + age + "세");
        System.out.println("키: " + height + "cm");
        System.out.println("몸무게: " + weight + "kg");
        System.out.println("학점: " + grade);
        System.out.println("학생 여부: " + isStudent);
        System.out.println("인구: " + population + "명");
    }
}
```

## 연산자

Java의 다양한 연산자들을 사용해보겠습니다.

```java
public class Operators {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        
        // 산술 연산자
        System.out.println("=== 산술 연산자 ===");
        System.out.println(a + " + " + b + " = " + (a + b));
        System.out.println(a + " - " + b + " = " + (a - b));
        System.out.println(a + " * " + b + " = " + (a * b));
        System.out.println(a + " / " + b + " = " + (a / b));
        System.out.println(a + " % " + b + " = " + (a % b));
        
        // 비교 연산자
        System.out.println("\n=== 비교 연산자 ===");
        System.out.println(a + " > " + b + " = " + (a > b));
        System.out.println(a + " < " + b + " = " + (a < b));
        System.out.println(a + " == " + b + " = " + (a == b));
        System.out.println(a + " != " + b + " = " + (a != b));
        
        // 논리 연산자
        boolean x = true;
        boolean y = false;
        System.out.println("\n=== 논리 연산자 ===");
        System.out.println(x + " && " + y + " = " + (x && y));
        System.out.println(x + " || " + y + " = " + (x || y));
        System.out.println("!" + x + " = " + (!x));
    }
}
```

## 조건문 (if-else)

조건에 따라 다른 코드를 실행하는 방법입니다.

```java
public class ConditionalStatements {
    public static void main(String[] args) {
        int score = 85;
        String grade;
        
        if (score >= 90) {
            grade = "A";
        } else if (score >= 80) {
            grade = "B";
        } else if (score >= 70) {
            grade = "C";
        } else if (score >= 60) {
            grade = "D";
        } else {
            grade = "F";
        }
        
        System.out.println("점수: " + score);
        System.out.println("학점: " + grade);
        
        // 삼항 연산자
        String result = (score >= 60) ? "합격" : "불합격";
        System.out.println("결과: " + result);
    }
}
```

## 반복문 (for, while)

반복적인 작업을 수행하는 방법입니다.

```java
public class Loops {
    public static void main(String[] args) {
        System.out.println("=== for 문 ===");
        for (int i = 1; i <= 5; i++) {
            System.out.println("현재 숫자: " + i);
        }
        
        System.out.println("\n=== while 문 ===");
        int count = 1;
        while (count <= 3) {
            System.out.println("반복 " + count + "회");
            count++;
        }
        
        System.out.println("\n=== do-while 문 ===");
        int num = 1;
        do {
            System.out.println("무조건 한 번은 실행: " + num);
            num++;
        } while (num <= 2);
        
        System.out.println("\n=== 구구단 3단 ===");
        for (int i = 1; i <= 9; i++) {
            System.out.println("3 × " + i + " = " + (3 * i));
        }
    }
}
```

## 배열

여러 개의 값을 저장하고 관리하는 방법입니다.

```java
public class Arrays {
    public static void main(String[] args) {
        // 배열 선언과 초기화
        int[] numbers = {10, 20, 30, 40, 50};
        String[] fruits = {"사과", "바나나", "오렌지", "포도"};
        
        System.out.println("=== 숫자 배열 ===");
        System.out.println("배열 길이: " + numbers.length);
        for (int i = 0; i < numbers.length; i++) {
            System.out.println("numbers[" + i + "] = " + numbers[i]);
        }
        
        System.out.println("\n=== 과일 배열 (향상된 for문) ===");
        for (String fruit : fruits) {
            System.out.println("과일: " + fruit);
        }
        
        // 배열의 합계와 평균 계산
        int sum = 0;
        for (int number : numbers) {
            sum += number;
        }
        double average = (double) sum / numbers.length;
        
        System.out.println("\n=== 통계 ===");
        System.out.println("합계: " + sum);
        System.out.println("평균: " + average);
    }
}
```

이제 각 코드 셀을 실행해보세요! 실행 버튼을 클릭하거나 `Ctrl+Enter` 키를 사용할 수 있습니다.