"""
40 code-generation benchmark tasks — 20 Python + 20 Java.

Each task contains:
  id          : unique identifier
  language    : "python" | "java"
  title       : short human-readable name
  description : natural-language prompt sent to the LLM
  test_cases  : list of dicts used by the harness to validate output

Python test-case keys:
  input    : list of positional arguments passed to the function
  expected : the exact return value to compare against

Java test-case keys:
  inputs       : list of Java-literal strings (method arguments)
  expected     : Java-literal / expression for the expected value
  return_type  : Java return type string (used to pick comparison strategy)
"""

# ---------------------------------------------------------------------------
# Python tasks
# ---------------------------------------------------------------------------
PYTHON_TASKS = [
    {
        "id": "py_001",
        "language": "python",
        "title": "Reverse String",
        "description": (
            "Write a Python function:\n"
            "    def reverse_string(s: str) -> str\n"
            "that returns the reversed version of the input string."
        ),
        "function_name": "reverse_string",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello"],  "expected": "olleh"},
            {"input": ["world"],  "expected": "dlrow"},
            {"input": [""],       "expected": ""},
            {"input": ["a"],      "expected": "a"},
            {"input": ["abcde"],  "expected": "edcba"},
        ],
    },
    {
        "id": "py_002",
        "language": "python",
        "title": "Is Palindrome",
        "description": (
            "Write a Python function:\n"
            "    def is_palindrome(s: str) -> bool\n"
            "that returns True if the string reads the same forwards and backwards."
        ),
        "function_name": "is_palindrome",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["racecar"], "expected": True},
            {"input": ["hello"],   "expected": False},
            {"input": ["a"],       "expected": True},
            {"input": [""],        "expected": True},
            {"input": ["abcba"],   "expected": True},
        ],
    },
    {
        "id": "py_003",
        "language": "python",
        "title": "Factorial",
        "description": (
            "Write a Python function:\n"
            "    def factorial(n: int) -> int\n"
            "that returns n! (0! = 1)."
        ),
        "function_name": "factorial",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [0],  "expected": 1},
            {"input": [1],  "expected": 1},
            {"input": [5],  "expected": 120},
            {"input": [7],  "expected": 5040},
            {"input": [10], "expected": 3628800},
        ],
    },
    {
        "id": "py_004",
        "language": "python",
        "title": "Fibonacci",
        "description": (
            "Write a Python function:\n"
            "    def fibonacci(n: int) -> int\n"
            "that returns the nth Fibonacci number (0-indexed: fib(0)=0, fib(1)=1)."
        ),
        "function_name": "fibonacci",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [0],  "expected": 0},
            {"input": [1],  "expected": 1},
            {"input": [6],  "expected": 8},
            {"input": [10], "expected": 55},
            {"input": [15], "expected": 610},
        ],
    },
    {
        "id": "py_005",
        "language": "python",
        "title": "Count Vowels",
        "description": (
            "Write a Python function:\n"
            "    def count_vowels(s: str) -> int\n"
            "that counts the number of vowels (a, e, i, o, u — case-insensitive) in s."
        ),
        "function_name": "count_vowels",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello"],   "expected": 2},
            {"input": ["aeiou"],   "expected": 5},
            {"input": [""],        "expected": 0},
            {"input": ["rhythm"],  "expected": 0},
            {"input": ["AEIOU"],   "expected": 5},
        ],
    },
    {
        "id": "py_006",
        "language": "python",
        "title": "Find Maximum",
        "description": (
            "Write a Python function:\n"
            "    def find_max(lst: list) -> int\n"
            "that returns the maximum element of the list without using the built-in max()."
        ),
        "function_name": "find_max",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [[1, 2, 3]],        "expected": 3},
            {"input": [[5, 1, 8, 2]],     "expected": 8},
            {"input": [[-1, -2, -3]],     "expected": -1},
            {"input": [[42]],             "expected": 42},
            {"input": [[0, 100, 50, 75]], "expected": 100},
        ],
    },
    {
        "id": "py_007",
        "language": "python",
        "title": "Is Prime",
        "description": (
            "Write a Python function:\n"
            "    def is_prime(n: int) -> bool\n"
            "that returns True if n is a prime number, False otherwise."
        ),
        "function_name": "is_prime",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [2],  "expected": True},
            {"input": [7],  "expected": True},
            {"input": [1],  "expected": False},
            {"input": [4],  "expected": False},
            {"input": [17], "expected": True},
            {"input": [0],  "expected": False},
        ],
    },
    {
        "id": "py_008",
        "language": "python",
        "title": "Binary Search",
        "description": (
            "Write a Python function:\n"
            "    def binary_search(arr: list, target: int) -> int\n"
            "that returns the index of target in the sorted list arr, or -1 if not found."
        ),
        "function_name": "binary_search",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 3], "expected": 2},
            {"input": [[1, 2, 3, 4, 5], 6], "expected": -1},
            {"input": [[10, 20, 30], 10],    "expected": 0},
            {"input": [[10, 20, 30], 30],    "expected": 2},
            {"input": [[], 5],               "expected": -1},
        ],
    },
    {
        "id": "py_009",
        "language": "python",
        "title": "Bubble Sort",
        "description": (
            "Write a Python function:\n"
            "    def bubble_sort(arr: list) -> list\n"
            "that returns a new sorted list using the bubble-sort algorithm "
            "without using Python's built-in sort."
        ),
        "function_name": "bubble_sort",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[5, 3, 1, 4, 2]],     "expected": [1, 2, 3, 4, 5]},
            {"input": [[1]],                  "expected": [1]},
            {"input": [[]],                   "expected": []},
            {"input": [[3, 1, 2]],            "expected": [1, 2, 3]},
            {"input": [[-3, 0, -1, 2, -2]],   "expected": [-3, -2, -1, 0, 2]},
        ],
    },
    {
        "id": "py_010",
        "language": "python",
        "title": "Two Sum",
        "description": (
            "Write a Python function:\n"
            "    def two_sum(nums: list, target: int) -> list\n"
            "Given a list of integers, return the indices of the two numbers "
            "that add up to target. Return the indices sorted in ascending order."
        ),
        "function_name": "two_sum",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9],  "expected": [0, 1]},
            {"input": [[3, 2, 4], 6],        "expected": [1, 2]},
            {"input": [[1, 5, 3, 7], 8],     "expected": [1, 3]},
            {"input": [[0, 4, 3, 0], 0],     "expected": [0, 3]},
        ],
    },
    {
        "id": "py_011",
        "language": "python",
        "title": "Is Anagram",
        "description": (
            "Write a Python function:\n"
            "    def is_anagram(s: str, t: str) -> bool\n"
            "that returns True if s and t are anagrams of each other "
            "(same characters, same frequencies)."
        ),
        "function_name": "is_anagram",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["listen", "silent"],   "expected": True},
            {"input": ["hello", "world"],     "expected": False},
            {"input": ["anagram", "nagaram"], "expected": True},
            {"input": ["rat", "car"],         "expected": False},
            {"input": ["", ""],              "expected": True},
        ],
    },
    {
        "id": "py_012",
        "language": "python",
        "title": "Word Frequency",
        "description": (
            "Write a Python function:\n"
            "    def word_frequency(text: str) -> dict\n"
            "that returns a dictionary mapping each word to its occurrence count. "
            "Words are separated by spaces (assume no punctuation)."
        ),
        "function_name": "word_frequency",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello world hello"],    "expected": {"hello": 2, "world": 1}},
            {"input": ["a b c a b a"],          "expected": {"a": 3, "b": 2, "c": 1}},
            {"input": ["one"],                   "expected": {"one": 1}},
            {"input": [""],                      "expected": {}},
        ],
    },
    {
        "id": "py_013",
        "language": "python",
        "title": "Balanced Parentheses",
        "description": (
            "Write a Python function:\n"
            "    def is_balanced(s: str) -> bool\n"
            "that returns True if every opening bracket has a matching closing "
            "bracket in the correct order. Brackets: (), [], {}."
        ),
        "function_name": "is_balanced",
        "difficulty": "medium",
        "category": "data_structures",
        "test_cases": [
            {"input": ["((()))"],   "expected": True},
            {"input": ["(()"],      "expected": False},
            {"input": [""],         "expected": True},
            {"input": ["{[()]}"],   "expected": True},
            {"input": ["{[(])}"],   "expected": False},
        ],
    },
    {
        "id": "py_014",
        "language": "python",
        "title": "Run-Length Encoding",
        "description": (
            "Write a Python function:\n"
            "    def run_length_encode(s: str) -> str\n"
            "that encodes a string using run-length encoding, "
            "e.g. 'aaabbc' → '3a2b1c'."
        ),
        "function_name": "run_length_encode",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["aaabbc"],   "expected": "3a2b1c"},
            {"input": ["abc"],      "expected": "1a1b1c"},
            {"input": ["aaaa"],     "expected": "4a"},
            {"input": ["a"],        "expected": "1a"},
        ],
    },
    {
        "id": "py_015",
        "language": "python",
        "title": "Missing Number",
        "description": (
            "Write a Python function:\n"
            "    def missing_number(nums: list) -> int\n"
            "Given a list of n distinct integers in the range [0, n], "
            "return the one missing number."
        ),
        "function_name": "missing_number",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[3, 0, 1]],              "expected": 2},
            {"input": [[0, 1]],                 "expected": 2},
            {"input": [[9,6,4,2,3,5,7,0,1]],   "expected": 8},
            {"input": [[0]],                    "expected": 1},
        ],
    },
    {
        "id": "py_016",
        "language": "python",
        "title": "Flatten List",
        "description": (
            "Write a Python function:\n"
            "    def flatten_list(lst: list) -> list\n"
            "that recursively flattens a nested list of arbitrary depth."
        ),
        "function_name": "flatten_list",
        "difficulty": "hard",
        "category": "data_structures",
        "test_cases": [
            {"input": [[[1, 2], [3, [4, 5]]]],   "expected": [1, 2, 3, 4, 5]},
            {"input": [[[1], [2], [3]]],           "expected": [1, 2, 3]},
            {"input": [[1, 2, 3]],                 "expected": [1, 2, 3]},
            {"input": [[[[1]]]],                   "expected": [1]},
            {"input": [[]],                        "expected": []},
        ],
    },
    {
        "id": "py_017",
        "language": "python",
        "title": "LRU Cache",
        "description": (
            "Write a Python class:\n"
            "    class LRUCache:\n"
            "        def __init__(self, capacity: int)\n"
            "        def get(self, key: int) -> int\n"
            "        def put(self, key: int, value: int) -> None\n"
            "Implement a Least Recently Used cache. get() returns the value if "
            "the key exists, else -1. put() inserts or updates the key-value pair, "
            "evicting the least recently used key when capacity is exceeded."
        ),
        "function_name": "LRUCache",
        "difficulty": "hard",
        "category": "data_structures",
        "test_cases": [
            {
                "input": ["capacity=2; c=LRUCache(capacity); c.put(1,1); c.put(2,2); c.get(1)"],
                "expected": 1
            },
            {
                "input": ["capacity=2; c=LRUCache(capacity); c.put(1,1); c.put(2,2); c.put(3,3); c.get(2)"],
                "expected": 2    # put(3,3) evicts key 1 (LRU); key 2 is still present
            },
            {
                "input": ["capacity=2; c=LRUCache(capacity); c.put(1,1); c.put(2,2); c.put(3,3); c.get(1)"],
                "expected": -1   # key 1 was evicted as least-recently-used
            },
            {
                "input": ["capacity=1; c=LRUCache(capacity); c.put(1,1); c.put(2,2); c.get(1)"],
                "expected": -1
            },
        ],
    },
    {
        "id": "py_018",
        "language": "python",
        "title": "Longest Common Subsequence",
        "description": (
            "Write a Python function:\n"
            "    def lcs(s1: str, s2: str) -> int\n"
            "that returns the length of the longest common subsequence of s1 and s2 "
            "using dynamic programming."
        ),
        "function_name": "lcs",
        "difficulty": "hard",
        "category": "algorithms",
        "test_cases": [
            {"input": ["abcde", "ace"],    "expected": 3},
            {"input": ["abc", "abc"],      "expected": 3},
            {"input": ["abc", "def"],      "expected": 0},
            {"input": ["", "abc"],         "expected": 0},
            {"input": ["abcba", "abcbcba"],"expected": 5},
        ],
    },
    {
        "id": "py_019",
        "language": "python",
        "title": "Thread-Safe Counter",
        "description": (
            "Write a Python class:\n"
            "    class ThreadSafeCounter:\n"
            "        def increment(self) -> None\n"
            "        def decrement(self) -> None\n"
            "        def get_value(self) -> int\n"
            "that implements a thread-safe counter using a threading lock. "
            "The counter starts at 0."
        ),
        "function_name": "ThreadSafeCounter",
        "difficulty": "hard",
        "category": "concurrency",
        "test_cases": [
            {
                "input": ["c=ThreadSafeCounter(); c.increment(); c.increment(); c.get_value()"],
                "expected": 2
            },
            {
                "input": ["c=ThreadSafeCounter(); c.increment(); c.decrement(); c.get_value()"],
                "expected": 0
            },
            {
                "input": ["c=ThreadSafeCounter(); c.get_value()"],
                "expected": 0
            },
            {
                "input": ["c=ThreadSafeCounter(); [c.increment() for _ in range(100)]; c.get_value()"],
                "expected": 100
            },
        ],
    },
    {
        "id": "py_020",
        "language": "python",
        "title": "GCD and LCM of List",
        "description": (
            "Write two Python functions:\n"
            "    def gcd(a: int, b: int) -> int\n"
            "    def lcm_of_list(numbers: list) -> int\n"
            "gcd() returns the greatest common divisor of a and b using the "
            "Euclidean algorithm. lcm_of_list() returns the least common multiple "
            "of all integers in the list. lcm_of_list() must call gcd() internally."
        ),
        "function_name": "lcm_of_list",
        "difficulty": "hard",
        "category": "self_invoking",
        "test_cases": [
            {"input": [[4, 6]],        "expected": 12},
            {"input": [[3, 4, 5]],     "expected": 60},
            {"input": [[1, 2, 3, 4, 5]],"expected": 60},
            {"input": [[7]],           "expected": 7},
        ],
    },
]

# ---------------------------------------------------------------------------
# Java tasks
# ---------------------------------------------------------------------------
# Each test case has:
#   inputs      : list of Java literal strings (method arguments)
#   expected    : Java expression for expected value
#   return_type : Java type — used to select comparison strategy in harness
# ---------------------------------------------------------------------------
JAVA_TASKS = [
    {
        "id": "java_001",
        "language": "java",
        "title": "Reverse String",
        "description": (
            "Write a Java method:\n"
            "    public static String reverseString(String s)\n"
            "that returns the reversed version of the input string."
        ),
        "function_name": "reverseString",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello"],  "expected": "olleh"},
            {"input": ["world"],  "expected": "dlrow"},
            {"input": [""],       "expected": ""},
            {"input": ["a"],      "expected": "a"},
            {"input": ["abcde"],  "expected": "edcba"},
        ],
    },
    {
        "id": "java_002",
        "language": "java",
        "title": "Is Palindrome",
        "description": (
            "Write a Java method:\n"
            "    public static boolean isPalindrome(String s)\n"
            "that returns true if the string reads the same forwards and backwards."
        ),
        "function_name": "isPalindrome",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["racecar"], "expected": True},
            {"input": ["hello"],   "expected": False},
            {"input": ["a"],       "expected": True},
            {"input": [""],        "expected": True},
            {"input": ["abcba"],   "expected": True},
        ],
    },
    {
        "id": "java_003",
        "language": "java",
        "title": "Factorial",
        "description": (
            "Write a Java method:\n"
            "    public static long factorial(int n)\n"
            "that returns n! (0! = 1)."
        ),
        "function_name": "factorial",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [0],  "expected": 1},
            {"input": [1],  "expected": 1},
            {"input": [5],  "expected": 120},
            {"input": [7],  "expected": 5040},
            {"input": [10], "expected": 3628800},
        ],
    },
    {
        "id": "java_004",
        "language": "java",
        "title": "Fibonacci",
        "description": (
            "Write a Java method:\n"
            "    public static int fibonacci(int n)\n"
            "that returns the nth Fibonacci number "
            "(0-indexed: fibonacci(0)=0, fibonacci(1)=1)."
        ),
        "function_name": "fibonacci",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [0],  "expected": 0},
            {"input": [1],  "expected": 1},
            {"input": [6],  "expected": 8},
            {"input": [10], "expected": 55},
            {"input": [15], "expected": 610},
        ],
    },
    {
        "id": "java_005",
        "language": "java",
        "title": "Count Vowels",
        "description": (
            "Write a Java method:\n"
            "    public static int countVowels(String s)\n"
            "that counts the number of vowels (a, e, i, o, u — case-insensitive) in s."
        ),
        "function_name": "countVowels",
        "difficulty": "easy",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello"],   "expected": 2},
            {"input": ["aeiou"],   "expected": 5},
            {"input": [""],        "expected": 0},
            {"input": ["rhythm"],  "expected": 0},
            {"input": ["AEIOU"],   "expected": 5},
        ],
    },
    {
        "id": "java_006",
        "language": "java",
        "title": "Find Maximum",
        "description": (
            "Write a Java method:\n"
            "    public static int findMax(int[] arr)\n"
            "that returns the maximum element of the array "
            "without using any built-in sort or max utilities."
        ),
        "function_name": "findMax",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [[1, 2, 3]],        "expected": 3},
            {"input": [[5, 1, 8, 2]],     "expected": 8},
            {"input": [[-1, -2, -3]],     "expected": -1},
            {"input": [[42]],             "expected": 42},
            {"input": [[0, 100, 50, 75]], "expected": 100},
        ],
    },
    {
        "id": "java_007",
        "language": "java",
        "title": "Is Prime",
        "description": (
            "Write a Java method:\n"
            "    public static boolean isPrime(int n)\n"
            "that returns true if n is a prime number, false otherwise."
        ),
        "function_name": "isPrime",
        "difficulty": "easy",
        "category": "algorithms",
        "test_cases": [
            {"input": [2],  "expected": True},
            {"input": [7],  "expected": True},
            {"input": [1],  "expected": False},
            {"input": [4],  "expected": False},
            {"input": [17], "expected": True},
            {"input": [0],  "expected": False},
        ],
    },
    {
        "id": "java_008",
        "language": "java",
        "title": "Binary Search",
        "description": (
            "Write a Java method:\n"
            "    public static int binarySearch(int[] arr, int target)\n"
            "that returns the index of target in the sorted array arr, "
            "or -1 if not found."
        ),
        "function_name": "binarySearch",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 3], "expected": 2},
            {"input": [[1, 2, 3, 4, 5], 6], "expected": -1},
            {"input": [[10, 20, 30], 10],    "expected": 0},
            {"input": [[10, 20, 30], 30],    "expected": 2},
            {"input": [[], 5],               "expected": -1},
        ],
    },
    {
        "id": "java_009",
        "language": "java",
        "title": "Bubble Sort",
        "description": (
            "Write a Java method:\n"
            "    public static int[] bubbleSort(int[] arr)\n"
            "that returns a new sorted array using the bubble-sort algorithm "
            "without using Arrays.sort() or any built-in sort."
        ),
        "function_name": "bubbleSort",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[5, 3, 1, 4, 2]],    "expected": [1, 2, 3, 4, 5]},
            {"input": [[1]],                 "expected": [1]},
            {"input": [[]],                  "expected": []},
            {"input": [[3, 1, 2]],           "expected": [1, 2, 3]},
            {"input": [[-3, 0, -1, 2, -2]], "expected": [-3, -2, -1, 0, 2]},
        ],
    },
    {
        "id": "java_010",
        "language": "java",
        "title": "Two Sum",
        "description": (
            "Write a Java method:\n"
            "    public static int[] twoSum(int[] nums, int target)\n"
            "Given an array of integers, return the indices of the two numbers "
            "that add up to target. Return the indices sorted in ascending order."
        ),
        "function_name": "twoSum",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"input": [[3, 2, 4], 6],       "expected": [1, 2]},
            {"input": [[1, 5, 3, 7], 8],    "expected": [1, 3]},
            {"input": [[0, 4, 3, 0], 0],    "expected": [0, 3]},
        ],
    },
    {
        "id": "java_011",
        "language": "java",
        "title": "Is Anagram",
        "description": (
            "Write a Java method:\n"
            "    public static boolean isAnagram(String s, String t)\n"
            "that returns true if s and t are anagrams of each other "
            "(same characters, same frequencies)."
        ),
        "function_name": "isAnagram",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["listen", "silent"],   "expected": True},
            {"input": ["hello", "world"],     "expected": False},
            {"input": ["anagram", "nagaram"], "expected": True},
            {"input": ["rat", "car"],         "expected": False},
            {"input": ["", ""],              "expected": True},
        ],
    },
    {
        "id": "java_012",
        "language": "java",
        "title": "Word Frequency",
        "description": (
            "Write a Java method:\n"
            "    public static Map<String, Integer> wordFrequency(String text)\n"
            "that returns a map of each word to its occurrence count. "
            "Words are separated by spaces (assume no punctuation). "
            "Return an empty map for an empty string."
        ),
        "function_name": "wordFrequency",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["hello world hello"],
             "expected": {"hello": 2, "world": 1}},
            {"input": ["a b c a b a"],
             "expected": {"a": 3, "b": 2, "c": 1}},
            {"input": ["one"],
             "expected": {"one": 1}},
            {"input": [""],
             "expected": {}},
        ],
    },
    {
        "id": "java_013",
        "language": "java",
        "title": "Balanced Parentheses",
        "description": (
            "Write a Java method:\n"
            "    public static boolean isBalanced(String s)\n"
            "that returns true if every opening bracket has a matching closing "
            "bracket in the correct order. Brackets: (), [], {}."
        ),
        "function_name": "isBalanced",
        "difficulty": "medium",
        "category": "data_structures",
        "test_cases": [
            {"input": ["((()))"],  "expected": True},
            {"input": ["(()"],     "expected": False},
            {"input": [""],        "expected": True},
            {"input": ["{[()]}"],  "expected": True},
            {"input": ["{[(])}"],  "expected": False},
        ],
    },
    {
        "id": "java_014",
        "language": "java",
        "title": "Run-Length Encoding",
        "description": (
            "Write a Java method:\n"
            "    public static String runLengthEncode(String s)\n"
            "that encodes a string using run-length encoding, "
            "e.g. 'aaabbc' → '3a2b1c'."
        ),
        "function_name": "runLengthEncode",
        "difficulty": "medium",
        "category": "string_manipulation",
        "test_cases": [
            {"input": ["aaabbc"], "expected": "3a2b1c"},
            {"input": ["abc"],    "expected": "1a1b1c"},
            {"input": ["aaaa"],   "expected": "4a"},
            {"input": ["a"],      "expected": "1a"},
        ],
    },
    {
        "id": "java_015",
        "language": "java",
        "title": "Missing Number",
        "description": (
            "Write a Java method:\n"
            "    public static int missingNumber(int[] nums)\n"
            "Given an array of n distinct integers in the range [0, n], "
            "return the one missing number."
        ),
        "function_name": "missingNumber",
        "difficulty": "medium",
        "category": "algorithms",
        "test_cases": [
            {"input": [[3, 0, 1]],             "expected": 2},
            {"input": [[0, 1]],                "expected": 2},
            {"input": [[9,6,4,2,3,5,7,0,1]],  "expected": 8},
            {"input": [[0]],                   "expected": 1},
        ],
    },
    {
        "id": "java_016",
        "language": "java",
        "title": "Flatten List",
        "description": (
            "Write a Java method:\n"
            "    public static List<Integer> flattenList(Object[] arr)\n"
            "that recursively flattens a nested array of arbitrary depth "
            "and returns a flat List<Integer>."
        ),
        "function_name": "flattenList",
        "difficulty": "hard",
        "category": "data_structures",
        "test_cases": [
            {"input": [[[1, 2], [3, [4, 5]]]],  "expected": [1, 2, 3, 4, 5]},
            {"input": [[[1], [2], [3]]],          "expected": [1, 2, 3]},
            {"input": [[1, 2, 3]],                "expected": [1, 2, 3]},
            {"input": [[[[1]]]],                  "expected": [1]},
            {"input": [[]],                       "expected": []},
        ],
    },
    {
        "id": "java_017",
        "language": "java",
        "title": "LRU Cache",
        "description": (
            "Write a Java class:\n"
            "    class LRUCache {\n"
            "        LRUCache(int capacity)\n"
            "        int get(int key)\n"
            "        void put(int key, int value)\n"
            "    }\n"
            "Implement a Least Recently Used cache. get() returns the value if "
            "the key exists, else -1. put() inserts or updates the key-value pair, "
            "evicting the least recently used key when capacity is exceeded."
        ),
        "function_name": "LRUCache",
        "difficulty": "hard",
        "category": "data_structures",
        "test_cases": [
            {
                "input": ["LRUCache c=new LRUCache(2); c.put(1,1); c.put(2,2); c.get(1)"],
                "expected": 1
            },
            {
                "input": ["LRUCache c=new LRUCache(2); c.put(1,1); c.put(2,2); c.put(3,3); c.get(2)"],
                "expected": 2    # put(3,3) evicts key 1 (LRU); key 2 is still present
            },
            {
                "input": ["LRUCache c=new LRUCache(2); c.put(1,1); c.put(2,2); c.put(3,3); c.get(1)"],
                "expected": -1   # key 1 was evicted as least-recently-used
            },
            {
                "input": ["LRUCache c=new LRUCache(1); c.put(1,1); c.put(2,2); c.get(1)"],
                "expected": -1
            },
        ],
    },
    {
        "id": "java_018",
        "language": "java",
        "title": "Longest Common Subsequence",
        "description": (
            "Write a Java method:\n"
            "    public static int lcs(String s1, String s2)\n"
            "that returns the length of the longest common subsequence of "
            "s1 and s2 using dynamic programming."
        ),
        "function_name": "lcs",
        "difficulty": "hard",
        "category": "algorithms",
        "test_cases": [
            {"input": ["abcde", "ace"],     "expected": 3},
            {"input": ["abc", "abc"],       "expected": 3},
            {"input": ["abc", "def"],       "expected": 0},
            {"input": ["", "abc"],          "expected": 0},
            {"input": ["abcba", "abcbcba"], "expected": 5},
        ],
    },
    {
        "id": "java_019",
        "language": "java",
        "title": "Thread-Safe Counter",
        "description": (
            "Write a Java class:\n"
            "    class ThreadSafeCounter {\n"
            "        void increment()\n"
            "        void decrement()\n"
            "        int getValue()\n"
            "    }\n"
            "that implements a thread-safe counter using AtomicInteger. "
            "The counter starts at 0."
        ),
        "function_name": "ThreadSafeCounter",
        "difficulty": "hard",
        "category": "concurrency",
        "test_cases": [
            {
                "input": ["ThreadSafeCounter c=new ThreadSafeCounter(); c.increment(); c.increment(); c.getValue()"],
                "expected": 2
            },
            {
                "input": ["ThreadSafeCounter c=new ThreadSafeCounter(); c.increment(); c.decrement(); c.getValue()"],
                "expected": 0
            },
            {
                "input": ["ThreadSafeCounter c=new ThreadSafeCounter(); c.getValue()"],
                "expected": 0
            },
            {
                "input": ["ThreadSafeCounter c=new ThreadSafeCounter(); for(int i=0;i<100;i++) c.increment(); c.getValue()"],
                "expected": 100
            },
        ],
    },
    {
        "id": "java_020",
        "language": "java",
        "title": "GCD and LCM of List",
        "description": (
            "Write two Java methods:\n"
            "    public static int gcd(int a, int b)\n"
            "    public static long lcmOfList(int[] numbers)\n"
            "gcd() returns the greatest common divisor of a and b using the "
            "Euclidean algorithm. lcmOfList() returns the least common multiple "
            "of all integers in the array. lcmOfList() must call gcd() internally."
        ),
        "function_name": "lcmOfList",
        "difficulty": "hard",
        "category": "self_invoking",
        "test_cases": [
            {"input": [[4, 6]],          "expected": 12},
            {"input": [[3, 4, 5]],       "expected": 60},
            {"input": [[1, 2, 3, 4, 5]], "expected": 60},
            {"input": [[7]],             "expected": 7},
        ],
    },
]

ALL_TASKS = PYTHON_TASKS + JAVA_TASKS
