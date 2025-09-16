
### Java 날짜와 시간 API: 자주 겪는 어려움과 해결 방법 학습 가이드

안녕하세요, 여러분! 오늘 수업에서 다룬 Java의 `java.time` API는 매우 강력하지만, 처음 사용할 때 몇 가지 혼란스러운 점이 있을 수 있습니다. 많은 분들이 질문했던 내용과 자주 겪었던 어려움을 바탕으로, 핵심 개념을 다시 한번 정리해 보려고 합니다.

이 가이드를 통해 각 개념을 더 명확하게 이해하고, 앞으로 비슷한 실수를 피할 수 있을 거예요. 함께 차근차근 살펴봅시다.

### 1. 날짜 간격 계산: `Period`는 `LocalDate`와 함께 사용해요

많은 분들이 두 시간 사이의 날짜 차이를 계산하기 위해 `Period.between()`을 사용하다가 타입 불일치 오류를 만났습니다. 왜 이런 오류가 발생할까요?

핵심은 **`Period`는 '날짜(년, 월, 일)'의 차이만 다루는 클래스**라는 점입니다. 시간(시, 분, 초)이나 타임존 정보는 고려하지 않죠. 그래서 `Period`는 시간과 타임존 정보까지 포함된 `ZonedDateTime`이 아닌, 순수 날짜 정보만 가진 `LocalDate` 타입을 필요로 합니다.

이 문제를 해결하는 방법은 간단합니다. `ZonedDateTime` 객체에서 `.toLocalDate()` 메서드를 호출하여 `LocalDate`로 변환해주면 됩니다.

**흔히 발생하는 오류**

```java
import java.time.Period;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public class DateTimeErrorExample {
    public static void main(String[] args) {
        ZonedDateTime zdt1 = ZonedDateTime.of(2024, 1, 1, 10, 0, 0, 0, ZoneId.of("Asia/Seoul"));
        ZonedDateTime zdt2 = ZonedDateTime.of(2025, 3, 15, 12, 0, 0, 0, ZoneId.of("Asia/Seoul"));

        // 컴파일 오류 발생!
        Period.between(); 메서드는 ZonedDateTime이 아닌 LocalDate를 인자로 받기 때문입니다.
        Period period = Period.between(zdt1, zdt2); 
    }
}
```

**올바른 해결 방법**

```java
import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public class DateTimeSolution {
    public static void main(String[] args) {
        ZonedDateTime zdt1 = ZonedDateTime.of(2024, 1, 1, 10, 0, 0, 0, ZoneId.of("Asia/Seoul"));
        ZonedDateTime zdt2 = ZonedDateTime.of(2025, 3, 15, 12, 0, 0, 0, ZoneId.of("Asia/Seoul"));

        // .toLocalDate()를 사용해 ZonedDateTime에서 시간과 타임존 정보를 제외하고 날짜 정보만 추출합니다.
        LocalDate date1 = zdt1.toLocalDate();
        LocalDate date2 = zdt2.toLocalDate();

        Period period = Period.between(date1, date2);

        System.out.printf("날짜 차이: %d년 %d개월 %d일\n", 
            period.getYears(), period.getMonths(), period.getDays());
        // 출력: 날짜 차이: 1년 2개월 14일
    }
}
```

### 2. 날짜를 문자로: `DateTimeFormatter` 패턴 올바르게 사용하기

날짜와 시간 객체를 원하는 형식의 문자열로 바꿀 때 `DateTimeFormatter`는 정말 유용합니다. 하지만 패턴을 잘못 사용하면 `IllegalArgumentException` 오류가 발생하기 쉽습니다.

가장 흔한 실수는 'T'와 같은 **고정된 문자(리터럴)를 패턴의 일부로 그대로 사용하는 것**입니다. 패턴에서 알파벳은 특별한 의미(예: `y`는 년, `M`은 월)를 가지기 때문에, 포맷터는 'T'를 해석할 수 없어 오류를 냅니다.

이럴 때는 **작은따옴표('')로 고정된 문자를 감싸주면 됩니다.** 이렇게 하면 포맷터는 "이것은 약속된 기호가 아니라 그냥 문자 T입니다"라고 인식하게 됩니다.

**흔히 발생하는 오류**

```java
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class FormatErrorExample {
    public static void main(String[] args) {
        ZonedDateTime zdt = ZonedDateTime.now();
        
        // java.lang.IllegalArgumentException: Unknown pattern letter: T
        // 'T'는 y, M, d 등과 같이 약속된 패턴 문자가 아니기 때문에 오류가 발생합니다.
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-ddTHH:mm:ss z");
        System.out.println(zdt.format(formatter));
    }
}
```

**올바른 해결 방법**

```java
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class FormatSolution {
    public static void main(String[] args) {
        ZonedDateTime zdt = ZonedDateTime.now();
        
        // 'T'와 같이 패턴의 일부가 아닌 고정 문자는 작은따옴표로 감싸줍니다.
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss z");

        System.out.println(zdt.format(formatter));
        // 예시 출력: 2024-05-21T15:30:00 KST
    }
}
```

### 3. 타임존의 중요성: `ZonedDateTime` vs. `LocalDateTime`

두 클래스의 차이는 **'타임존(시간대) 정보'의 유무**입니다. 이 개념이 왜 중요한지 비유를 통해 알아볼까요?

-   **`LocalDateTime`**: 단순히 '오전 9시'라고 말하는 것과 같습니다. 어느 나라의 오전 9시인지 알 수 없죠. 날짜와 시간 정보만 있습니다.
-   **`ZonedDateTime`**: '한국 시간(KST) 기준 오전 9시'라고 말하는 것과 같습니다. 전 세계 어디서든 오해 없이 정확한 특정 시점을 가리킬 수 있습니다.

따라서, 국제적인 서비스를 만들거나 서로 다른 시간대에 있는 시점 간의 정확한 시간 차이를 계산해야 할 때는 반드시 `ZonedDateTime`을 사용해야 합니다.

**개념을 코드로 이해하기**

```java
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public class ZoneConcept {
    public static void main(String[] args) {
        // 그냥 '오전 9시'. 어디의 오전 9시인지는 모릅니다.
        LocalDateTime ldt = LocalDateTime.of(2024, 5, 21, 9, 0);
        System.out.println("LocalDateTime: " + ldt);

        // '서울의 오전 9시'라는 명확한 시점
        ZonedDateTime seoulTime = ZonedDateTime.of(ldt, ZoneId.of("Asia/Seoul"));
        System.out.println("Seoul ZonedDateTime: " + seoulTime);

        // '뉴욕의 오전 9시'라는 명확한 시점
        ZonedDateTime newYorkTime = ZonedDateTime.of(ldt, ZoneId.of("America/New_York"));
        System.out.println("New York ZonedDateTime: " + newYorkTime);

        // 서울의 오전 9시와 뉴욕의 오전 9시는 로컬 시간은 같지만, 전 세계 기준으로는 전혀 다른 시간입니다.
        // 서울의 오전 9시가 뉴욕의 오전 9시보다 13시간 더 빠른(먼저 발생한) 시간입니다.
        System.out.println("서울 시간이 뉴욕 시간보다 이후인가? " + seoulTime.isAfter(newYorkTime));
        // 출력: 서울 시간이 뉴욕 시간보다 이후인가? false
    }
}
```

### 4. 기본 중의 기본: `import` 구문 잊지 않기

`cannot find symbol` 오류는 "컴파일러가 `DateTimeFormatter`라는 클래스를 어디서 찾아야 할지 모르겠습니다!"라고 외치는 것과 같습니다.

Java는 클래스를 패키지 단위로 관리합니다. `ZonedDateTime`은 `java.time` 패키지에 있지만, `DateTimeFormatter`는 그 하위 패키지인 `java.time.format`에 속해 있습니다. `import java.time.*`를 사용하더라도 바로 아래에 있는 클래스만 가져올 뿐, 하위 패키지(`format`) 안의 클래스까지 가져오지는 않습니다.

해결책은 간단합니다. **사용하려는 모든 클래스의 전체 경로를 정확히 `import` 해주세요.**

**흔히 발생하는 오류**

```java
// import java.time.format.DateTimeFormatter; // 이 줄을 빠뜨렸습니다.
import java.time.ZonedDateTime;

public class ImportErrorExample {
    public static void main(String[] args) {
        // error: cannot find symbol
        // 컴파일러가 DateTimeFormatter 클래스가 어디에 있는지 찾지 못해 오류가 발생합니다.
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        ZonedDateTime now = ZonedDateTime.now();
        System.out.println(now.format(dtf));
    }
}
```

**올바른 해결 방법**

```java
import java.time.format.DateTimeFormatter; // 필요한 클래스를 정확하게 임포트합니다.
import java.time.ZonedDateTime;

public class ImportSolution {
    public static void main(String[] args) {
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        ZonedDateTime now = ZonedDateTime.now();
        System.out.println(now.format(dtf));
        // 출력: 2024-05-21
    }
}
```

### 5. 문자를 날짜로: 형식에 맞는 `DateTimeFormatter`로 파싱하기

`LocalDateTime.parse(String)`와 같은 메서드는 **정해진 기본 형식(ISO-8601 표준, `yyyy-MM-ddTHH:mm:ss`)을 기대**합니다. 마치 약속된 암호를 해독하는 것과 같죠.

만약 입력된 문자열이 이 약속된 형식과 다르면(예: 'T' 대신 공백이 있는 경우), 파서는 "이 암호는 내가 아는 방식과 다릅니다!"라며 `DateTimeParseException`을 발생시킵니다.

이때는 우리가 직접 '해독 가이드'를 제공해주면 됩니다. 바로 입력 문자열의 형식과 똑같은 패턴을 가진 `DateTimeFormatter`를 만들어서 `parse()` 메서드에 함께 전달하는 것입니다.

**문제 상황**

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;

public class ParseErrorExample {
    public static void main(String[] args) {
        String input = "2025-09-04 10:30"; // 기본 형식인 'T'가 아닌 공백을 사용
        try {
            // 기본 파서가 "yyyy-MM-ddTHH:mm" 형식을 기대하는데, 다른 형식이 들어와서 오류 발생
            LocalDateTime ldt = LocalDateTime.parse(input);
            System.out.println(ldt);
        } catch (DateTimeParseException e) {
            System.err.println("파싱 오류: " + e.getMessage());
        }
    }
}
```

**올바른 해결 방법**

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ParseSolution {
    public static void main(String[] args) {
        String input = "2025-09-04 10:30";
        
        // "yyyy-MM-dd HH:mm" 형식의 문자열을 해석할 수 있도록 '가이드'를 만들어줍니다.
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
        
        // 만들어진 가이드(formatter)를 사용해 문자열을 파싱합니다.
        LocalDateTime ldt = LocalDateTime.parse(input, formatter);
        
        System.out.println("파싱 성공: " + ldt);
        // 출력: 파싱 성공: 2025-09-04T10:30
    }
}
```

### 6. 핵심 철학 이해하기: `java.time`의 객체 지향과 불변성(Immutability)

마지막으로, `java.time` API를 잘 사용하려면 이 API가 설계된 핵심 철학을 이해하는 것이 중요합니다.

-   **객체 지향적 설계**: 날짜, 시간, 기간, 포맷터 등 모든 것이 각자의 역할과 기능을 가진 독립적인 **'객체'**입니다. 우리는 이 객체들에게 '메시지를 보내'(메서드를 호출하여) 원하는 결과를 얻습니다. 예를 들어, `ZonedDateTime` 객체에게 '너를 `LocalDate`로 바꿔줘'(`.toLocalDate()`)라고 요청하는 식이죠.

-   **불변성(Immutability)**: 이것은 매우 중요한 특징입니다. `java.time`의 모든 객체는 **한번 생성되면 그 상태가 절대 변하지 않습니다.** `plusDays(1)`과 같은 메서드를 호출하면 기존 객체가 바뀌는 것이 아니라, **하루가 더해진 '새로운' 객체가 생성되어 반환됩니다.** 이 덕분에 여러 곳에서 날짜 객체를 사용하더라도 값이 예상치 못하게 변경될 걱정 없이 안전하게 프로그래밍할 수 있습니다.

**객체 지향과 불변성을 보여주는 예제**

```java
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class OOPConcept {
    public static void main(String[] args) {
        // 1. ZonedDateTime 객체 생성
        ZonedDateTime nowInSeoul = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));

        // 2. DateTimeFormatter 객체 생성
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시 mm분");
        
        // 3. nowInSeoul 객체의 format() 메서드를 호출하여 포맷팅된 문자열 얻기
        String formattedString = nowInSeoul.format(formatter);
        System.out.println("현재 서울 시간: " + formattedString);

        // 4. nowInSeoul 객체에 plusDays() 메서드를 호출하여 '새로운' ZonedDateTime 객체 얻기
        ZonedDateTime tomorrow = nowInSeoul.plusDays(1);
        System.out.println("내일 같은 시간: " + tomorrow.format(formatter));
        
        // nowInSeoul 객체 자체는 변하지 않았음을 확인 (불변성)
        System.out.println("원본 객체는 불변: " + nowInSeoul.format(formatter));
    }
}
```