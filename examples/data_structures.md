# Java 자료구조 예제

이 노트북에서는 Java로 구현한 기본적인 자료구조들을 학습합니다.

## 스택 (Stack)

후입선출(LIFO - Last In First Out) 방식으로 동작하는 자료구조입니다.

```java
import java.util.Stack;

public class StackExample {
    public static void main(String[] args) {
        Stack<Integer> stack = new Stack<>();
        
        System.out.println("=== 스택 연산 ===");
        
        // 데이터 추가 (push)
        System.out.println("데이터 추가:");
        for (int i = 1; i <= 5; i++) {
            stack.push(i);
            System.out.println("Push " + i + " -> 스택: " + stack);
        }
        
        System.out.println("\n스택 크기: " + stack.size());
        System.out.println("맨 위 원소 (peek): " + stack.peek());
        
        // 데이터 제거 (pop)
        System.out.println("\n데이터 제거:");
        while (!stack.isEmpty()) {
            int popped = stack.pop();
            System.out.println("Pop " + popped + " -> 스택: " + stack);
        }
        
        System.out.println("\n스택이 비어있는가? " + stack.isEmpty());
        
        // 실제 활용 예제: 괄호 검사
        System.out.println("\n=== 괄호 검사 예제 ===");
        String[] expressions = {
            "(())",
            "(()",
            "()())",
            "{[()]}"
        };
        
        for (String expr : expressions) {
            boolean isValid = isValidParentheses(expr);
            System.out.println(expr + " -> " + (isValid ? "유효" : "무효"));
        }
    }
    
    // 괄호 유효성 검사
    public static boolean isValidParentheses(String s) {
        Stack<Character> stack = new Stack<>();
        
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '{' || c == '[') {
                stack.push(c);
            } else if (c == ')' || c == '}' || c == ']') {
                if (stack.isEmpty()) return false;
                
                char top = stack.pop();
                if ((c == ')' && top != '(') ||
                    (c == '}' && top != '{') ||
                    (c == ']' && top != '[')) {
                    return false;
                }
            }
        }
        
        return stack.isEmpty();
    }
}
```

## 큐 (Queue)

선입선출(FIFO - First In First Out) 방식으로 동작하는 자료구조입니다.

```java
import java.util.Queue;
import java.util.LinkedList;

public class QueueExample {
    public static void main(String[] args) {
        Queue<String> queue = new LinkedList<>();
        
        System.out.println("=== 큐 연산 ===");
        
        // 데이터 추가 (enqueue)
        System.out.println("데이터 추가:");
        String[] customers = {"Alice", "Bob", "Charlie", "David", "Eve"};
        for (String customer : customers) {
            queue.offer(customer);
            System.out.println("Enqueue " + customer + " -> 큐: " + queue);
        }
        
        System.out.println("\n큐 크기: " + queue.size());
        System.out.println("맨 앞 원소 (peek): " + queue.peek());
        
        // 데이터 제거 (dequeue)
        System.out.println("\n고객 서비스 처리:");
        int serviceNumber = 1;
        while (!queue.isEmpty()) {
            String customer = queue.poll();
            System.out.println("서비스 " + serviceNumber++ + ": " + customer + " 처리 완료 -> 대기: " + queue);
        }
        
        System.out.println("\n큐가 비어있는가? " + queue.isEmpty());
        
        // 원형 큐 시뮬레이션
        System.out.println("\n=== 원형 큐 시뮬레이션 ===");
        simulateCircularQueue();
    }
    
    public static void simulateCircularQueue() {
        int[] circularQueue = new int[5];
        int front = 0, rear = 0, size = 0;
        int capacity = circularQueue.length;
        
        // 데이터 추가
        int[] data = {10, 20, 30, 40};
        for (int value : data) {
            if (size < capacity) {
                circularQueue[rear] = value;
                rear = (rear + 1) % capacity;
                size++;
                System.out.println("추가: " + value + ", 큐 상태: " + 
                                 java.util.Arrays.toString(circularQueue) + 
                                 ", front=" + front + ", rear=" + rear);
            }
        }
        
        // 데이터 제거
        for (int i = 0; i < 2; i++) {
            if (size > 0) {
                int removed = circularQueue[front];
                circularQueue[front] = 0; // 시각화를 위해 0으로 설정
                front = (front + 1) % capacity;
                size--;
                System.out.println("제거: " + removed + ", 큐 상태: " + 
                                 java.util.Arrays.toString(circularQueue) + 
                                 ", front=" + front + ", rear=" + rear);
            }
        }
    }
}
```

## 연결 리스트 (Linked List)

노드들이 포인터로 연결된 선형 자료구조입니다.

```java
public class LinkedListExample {
    
    // 노드 클래스
    static class Node {
        int data;
        Node next;
        
        Node(int data) {
            this.data = data;
            this.next = null;
        }
    }
    
    // 단순 연결 리스트 클래스
    static class SimpleLinkedList {
        private Node head;
        
        // 리스트 끝에 추가
        public void append(int data) {
            Node newNode = new Node(data);
            if (head == null) {
                head = newNode;
                return;
            }
            
            Node current = head;
            while (current.next != null) {
                current = current.next;
            }
            current.next = newNode;
        }
        
        // 리스트 앞에 추가
        public void prepend(int data) {
            Node newNode = new Node(data);
            newNode.next = head;
            head = newNode;
        }
        
        // 특정 값 삭제
        public void delete(int data) {
            if (head == null) return;
            
            if (head.data == data) {
                head = head.next;
                return;
            }
            
            Node current = head;
            while (current.next != null && current.next.data != data) {
                current = current.next;
            }
            
            if (current.next != null) {
                current.next = current.next.next;
            }
        }
        
        // 리스트 출력
        public void display() {
            Node current = head;
            System.out.print("리스트: ");
            while (current != null) {
                System.out.print(current.data + " -> ");
                current = current.next;
            }
            System.out.println("null");
        }
        
        // 리스트 크기
        public int size() {
            int count = 0;
            Node current = head;
            while (current != null) {
                count++;
                current = current.next;
            }
            return count;
        }
        
        // 특정 값 검색
        public boolean contains(int data) {
            Node current = head;
            while (current != null) {
                if (current.data == data) {
                    return true;
                }
                current = current.next;
            }
            return false;
        }
    }
    
    public static void main(String[] args) {
        SimpleLinkedList list = new SimpleLinkedList();
        
        System.out.println("=== 연결 리스트 연산 ===");
        
        // 데이터 추가
        System.out.println("데이터 추가:");
        list.append(10);
        list.display();
        
        list.append(20);
        list.display();
        
        list.append(30);
        list.display();
        
        list.prepend(5);
        list.display();
        
        System.out.println("리스트 크기: " + list.size());
        
        // 검색
        System.out.println("\n검색:");
        System.out.println("20이 있는가? " + list.contains(20));
        System.out.println("100이 있는가? " + list.contains(100));
        
        // 삭제
        System.out.println("\n데이터 삭제:");
        list.delete(20);
        System.out.println("20 삭제 후:");
        list.display();
        
        list.delete(5);
        System.out.println("5 삭제 후:");
        list.display();
        
        System.out.println("최종 리스트 크기: " + list.size());
    }
}
```

## 이진 트리 (Binary Tree)

각 노드가 최대 두 개의 자식을 가지는 트리 자료구조입니다.

```java
public class BinaryTreeExample {
    
    // 트리 노드 클래스
    static class TreeNode {
        int data;
        TreeNode left, right;
        
        TreeNode(int data) {
            this.data = data;
            left = right = null;
        }
    }
    
    // 이진 트리 클래스
    static class BinaryTree {
        TreeNode root;
        
        // 전위 순회 (Preorder)
        public void preorderTraversal(TreeNode node) {
            if (node != null) {
                System.out.print(node.data + " ");
                preorderTraversal(node.left);
                preorderTraversal(node.right);
            }
        }
        
        // 중위 순회 (Inorder)
        public void inorderTraversal(TreeNode node) {
            if (node != null) {
                inorderTraversal(node.left);
                System.out.print(node.data + " ");
                inorderTraversal(node.right);
            }
        }
        
        // 후위 순회 (Postorder)
        public void postorderTraversal(TreeNode node) {
            if (node != null) {
                postorderTraversal(node.left);
                postorderTraversal(node.right);
                System.out.print(node.data + " ");
            }
        }
        
        // 트리 높이 계산
        public int height(TreeNode node) {
            if (node == null) return -1;
            return Math.max(height(node.left), height(node.right)) + 1;
        }
        
        // 노드 개수 계산
        public int countNodes(TreeNode node) {
            if (node == null) return 0;
            return countNodes(node.left) + countNodes(node.right) + 1;
        }
        
        // 특정 값 검색
        public boolean search(TreeNode node, int target) {
            if (node == null) return false;
            if (node.data == target) return true;
            return search(node.left, target) || search(node.right, target);
        }
    }
    
    public static void main(String[] args) {
        BinaryTree tree = new BinaryTree();
        
        // 트리 구성
        //       1
        //      / \
        //     2   3
        //    / \   \
        //   4   5   6
        
        tree.root = new TreeNode(1);
        tree.root.left = new TreeNode(2);
        tree.root.right = new TreeNode(3);
        tree.root.left.left = new TreeNode(4);
        tree.root.left.right = new TreeNode(5);
        tree.root.right.right = new TreeNode(6);
        
        System.out.println("=== 이진 트리 순회 ===");
        System.out.println("트리 구조:");
        System.out.println("       1");
        System.out.println("      / \\");
        System.out.println("     2   3");
        System.out.println("    / \\   \\");
        System.out.println("   4   5   6");
        System.out.println();
        
        System.out.print("전위 순회 (Root->Left->Right): ");
        tree.preorderTraversal(tree.root);
        System.out.println();
        
        System.out.print("중위 순회 (Left->Root->Right): ");
        tree.inorderTraversal(tree.root);
        System.out.println();
        
        System.out.print("후위 순회 (Left->Right->Root): ");
        tree.postorderTraversal(tree.root);
        System.out.println();
        
        System.out.println("\n=== 트리 정보 ===");
        System.out.println("트리 높이: " + tree.height(tree.root));
        System.out.println("노드 개수: " + tree.countNodes(tree.root));
        
        System.out.println("\n=== 검색 ===");
        System.out.println("5가 있는가? " + tree.search(tree.root, 5));
        System.out.println("10이 있는가? " + tree.search(tree.root, 10));
    }
}
```

## 해시 테이블 (Hash Table) 기본 구현

키-값 쌍을 저장하는 자료구조의 간단한 구현입니다.

```java
public class SimpleHashTable {
    
    // 키-값 쌍을 저장하는 클래스
    static class Entry {
        String key;
        int value;
        Entry next; // 충돌 해결을 위한 체이닝
        
        Entry(String key, int value) {
            this.key = key;
            this.value = value;
            this.next = null;
        }
    }
    
    private Entry[] table;
    private int size;
    private int capacity;
    
    public SimpleHashTable(int capacity) {
        this.capacity = capacity;
        this.table = new Entry[capacity];
        this.size = 0;
    }
    
    // 해시 함수
    private int hash(String key) {
        int hash = 0;
        for (char c : key.toCharArray()) {
            hash += c;
        }
        return hash % capacity;
    }
    
    // 값 저장
    public void put(String key, int value) {
        int index = hash(key);
        Entry newEntry = new Entry(key, value);
        
        if (table[index] == null) {
            table[index] = newEntry;
        } else {
            // 체이닝으로 충돌 해결
            Entry current = table[index];
            while (current.next != null) {
                if (current.key.equals(key)) {
                    current.value = value; // 기존 값 업데이트
                    return;
                }
                current = current.next;
            }
            if (current.key.equals(key)) {
                current.value = value;
            } else {
                current.next = newEntry;
            }
        }
        size++;
    }
    
    // 값 조회
    public Integer get(String key) {
        int index = hash(key);
        Entry current = table[index];
        
        while (current != null) {
            if (current.key.equals(key)) {
                return current.value;
            }
            current = current.next;
        }
        return null;
    }
    
    // 키 존재 여부 확인
    public boolean containsKey(String key) {
        return get(key) != null;
    }
    
    // 값 삭제
    public boolean remove(String key) {
        int index = hash(key);
        Entry current = table[index];
        Entry prev = null;
        
        while (current != null) {
            if (current.key.equals(key)) {
                if (prev == null) {
                    table[index] = current.next;
                } else {
                    prev.next = current.next;
                }
                size--;
                return true;
            }
            prev = current;
            current = current.next;
        }
        return false;
    }
    
    // 해시 테이블 상태 출력
    public void display() {
        System.out.println("=== 해시 테이블 상태 ===");
        for (int i = 0; i < capacity; i++) {
            System.out.print("인덱스 " + i + ": ");
            Entry current = table[i];
            if (current == null) {
                System.out.println("null");
            } else {
                while (current != null) {
                    System.out.print("(" + current.key + ":" + current.value + ")");
                    if (current.next != null) System.out.print(" -> ");
                    current = current.next;
                }
                System.out.println();
            }
        }
        System.out.println("크기: " + size);
    }
    
    public static void main(String[] args) {
        SimpleHashTable hashTable = new SimpleHashTable(7);
        
        System.out.println("=== 해시 테이블 연산 ===");
        
        // 데이터 추가
        String[] keys = {"apple", "banana", "orange", "grape", "kiwi"};
        int[] values = {100, 200, 150, 80, 120};
        
        for (int i = 0; i < keys.length; i++) {
            hashTable.put(keys[i], values[i]);
            System.out.println("추가: " + keys[i] + " -> " + values[i] + 
                             " (해시값: " + hashTable.hash(keys[i]) + ")");
        }
        
        hashTable.display();
        
        // 데이터 조회
        System.out.println("\n=== 데이터 조회 ===");
        for (String key : keys) {
            Integer value = hashTable.get(key);
            System.out.println(key + " -> " + value);
        }
        
        // 존재하지 않는 키 조회
        System.out.println("mango -> " + hashTable.get("mango"));
        
        // 데이터 삭제
        System.out.println("\n=== 데이터 삭제 ===");
        hashTable.remove("banana");
        System.out.println("banana 삭제 후:");
        hashTable.display();
    }
}
```

각 자료구조의 특성과 용도를 이해하고, 실제 상황에서 어떤 자료구조를 선택해야 하는지 생각해보세요!