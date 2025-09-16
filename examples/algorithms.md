# Java 알고리즘 예제

이 노트북에서는 Java로 구현한 다양한 알고리즘들을 학습합니다.

## 정렬 알고리즘

### 버블 정렬 (Bubble Sort)

가장 간단한 정렬 알고리즘 중 하나입니다.

```java
public class BubbleSort {
    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90};
        
        System.out.println("정렬 전:");
        printArray(arr);
        
        bubbleSort(arr);
        
        System.out.println("\n버블 정렬 후:");
        printArray(arr);
    }
    
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    // 교환
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    
    public static void printArray(int[] arr) {
        for (int value : arr) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
```

### 선택 정렬 (Selection Sort)

매번 최솟값을 찾아서 정렬하는 알고리즘입니다.

```java
public class SelectionSort {
    public static void main(String[] args) {
        int[] arr = {64, 25, 12, 22, 11};
        
        System.out.println("정렬 전:");
        printArray(arr);
        
        selectionSort(arr);
        
        System.out.println("\n선택 정렬 후:");
        printArray(arr);
    }
    
    public static void selectionSort(int[] arr) {
        int n = arr.length;
        
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            
            // 최솟값과 현재 위치 교환
            int temp = arr[minIdx];
            arr[minIdx] = arr[i];
            arr[i] = temp;
        }
    }
    
    public static void printArray(int[] arr) {
        for (int value : arr) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
```

## 검색 알고리즘

### 선형 검색 (Linear Search)

배열을 처음부터 끝까지 순차적으로 검색하는 방법입니다.

```java
public class LinearSearch {
    public static void main(String[] args) {
        int[] arr = {2, 3, 4, 10, 40};
        int target = 10;
        
        System.out.println("배열: ");
        printArray(arr);
        System.out.println("찾을 값: " + target);
        
        int result = linearSearch(arr, target);
        
        if (result == -1) {
            System.out.println("값을 찾을 수 없습니다.");
        } else {
            System.out.println("값이 인덱스 " + result + "에서 발견되었습니다.");
        }
    }
    
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }
    
    public static void printArray(int[] arr) {
        for (int value : arr) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
```

### 이진 검색 (Binary Search)

정렬된 배열에서 효율적으로 값을 찾는 방법입니다.

```java
public class BinarySearch {
    public static void main(String[] args) {
        int[] arr = {2, 3, 4, 10, 40, 50, 60, 70};
        int target = 10;
        
        System.out.println("정렬된 배열:");
        printArray(arr);
        System.out.println("찾을 값: " + target);
        
        int result = binarySearch(arr, target);
        
        if (result == -1) {
            System.out.println("값을 찾을 수 없습니다.");
        } else {
            System.out.println("값이 인덱스 " + result + "에서 발견되었습니다.");
        }
    }
    
    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            System.out.println("검색 범위: [" + left + ", " + right + "], 중간값: " + arr[mid]);
            
            if (arr[mid] == target) {
                return mid;
            }
            
            if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
    
    public static void printArray(int[] arr) {
        for (int value : arr) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
```

## 수학 알고리즘

### 팩토리얼 계산

재귀와 반복문을 사용한 팩토리얼 계산입니다.

```java
public class Factorial {
    public static void main(String[] args) {
        int n = 5;
        
        System.out.println("=== 팩토리얼 계산 ===");
        System.out.println("n = " + n);
        
        long iterativeResult = factorialIterative(n);
        System.out.println("반복문으로 계산: " + n + "! = " + iterativeResult);
        
        long recursiveResult = factorialRecursive(n);
        System.out.println("재귀로 계산: " + n + "! = " + recursiveResult);
        
        // 과정 출력
        System.out.println("\n계산 과정:");
        for (int i = 1; i <= n; i++) {
            System.out.println(i + "! = " + factorialIterative(i));
        }
    }
    
    // 반복문을 사용한 팩토리얼
    public static long factorialIterative(int n) {
        long result = 1;
        for (int i = 1; i <= n; i++) {
            result *= i;
        }
        return result;
    }
    
    // 재귀를 사용한 팩토리얼
    public static long factorialRecursive(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorialRecursive(n - 1);
    }
}
```

### 피보나치 수열

재귀와 동적 프로그래밍을 사용한 피보나치 수열 계산입니다.

```java
public class Fibonacci {
    public static void main(String[] args) {
        int n = 10;
        
        System.out.println("=== 피보나치 수열 ===");
        System.out.println("첫 " + n + "개의 피보나치 수:");
        
        // 반복문으로 계산
        System.out.print("반복문: ");
        for (int i = 0; i < n; i++) {
            System.out.print(fibonacciIterative(i) + " ");
        }
        System.out.println();
        
        // 재귀로 계산 (작은 수만)
        System.out.print("재귀: ");
        for (int i = 0; i < Math.min(n, 8); i++) { // 재귀는 느리므로 8개만
            System.out.print(fibonacciRecursive(i) + " ");
        }
        System.out.println();
        
        // 성능 비교
        long startTime = System.nanoTime();
        long result1 = fibonacciIterative(30);
        long endTime = System.nanoTime();
        System.out.println("\n30번째 피보나치 수 (반복문): " + result1);
        System.out.println("실행 시간: " + (endTime - startTime) / 1000000.0 + " ms");
    }
    
    // 반복문을 사용한 피보나치
    public static long fibonacciIterative(int n) {
        if (n <= 1) return n;
        
        long prev = 0, curr = 1;
        for (int i = 2; i <= n; i++) {
            long next = prev + curr;
            prev = curr;
            curr = next;
        }
        return curr;
    }
    
    // 재귀를 사용한 피보나치
    public static long fibonacciRecursive(int n) {
        if (n <= 1) return n;
        return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
    }
}
```

### 최대공약수 (유클리드 호제법)

두 수의 최대공약수를 구하는 효율적인 알고리즘입니다.

```java
public class GCD {
    public static void main(String[] args) {
        int a = 48, b = 18;
        
        System.out.println("=== 최대공약수 계산 ===");
        System.out.println("a = " + a + ", b = " + b);
        
        int gcdResult = gcd(a, b);
        System.out.println("최대공약수: " + gcdResult);
        
        int lcmResult = lcm(a, b);
        System.out.println("최소공배수: " + lcmResult);
        
        // 계산 과정 출력
        System.out.println("\n유클리드 호제법 과정:");
        gcdWithSteps(a, b);
    }
    
    // 최대공약수 (유클리드 호제법)
    public static int gcd(int a, int b) {
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
    
    // 최소공배수
    public static int lcm(int a, int b) {
        return (a * b) / gcd(a, b);
    }
    
    // 계산 과정을 출력하는 GCD
    public static void gcdWithSteps(int a, int b) {
        while (b != 0) {
            System.out.println(a + " = " + b + " × " + (a / b) + " + " + (a % b));
            int temp = b;
            b = a % b;
            a = temp;
        }
        System.out.println("최대공약수: " + a);
    }
}
```

각 알고리즘을 실행해보고 결과를 확인해보세요. 시간 복잡도와 공간 복잡도를 생각해보면서 각 알고리즘의 특성을 이해해보시기 바랍니다!