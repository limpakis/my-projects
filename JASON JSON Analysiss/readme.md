## JSON Validation and Analysis Program

This program is designed to **validate JSON structure**, extract data from JSON files, and interact with an API. It provides two main functionalities:

1. **Bot Mode**: Accepts user prompts and returns responses via an API.
2. **Content Extraction**: Validates and extracts content from a JSON file.

---

## Installation Instructions

1. **Compile the Program**
   ```bash
   gcc -Wall -Wextra -Werror -pedantic -c neurolib.c
   gcc -Wall -Wextra -Werror -pedantic -c jason.c
   gcc -o jason neurolib.o jason.o -lssl -lcrypto
   ```

2. **Run the Program**
   - **Bot Mode**: `./jason --bot`
   - **Extract JSON Content**: `./jason --extract <filename.json>`

---

## Code Description

### 1. **Checking JSON Extensions**
The function `has_json_extension` verifies if a filename ends with `.json`.
```c
int has_json_extension(const char *filename) {
    const char *dot = strrchr(filename, '.');
    return (dot && strcmp(dot, ".json") == 0);
}
```

---

### 2. **JSON Structure Validation**
The function `is_valid_json` checks the integrity of a JSON file, ensuring proper bracket and quotation matching.
```c
int is_valid_json(const char *filename) {
    // Reads the file character by character
    // and checks brackets, quotes, and string literals.
}
```

---

### 3. **Extracting JSON Content**
The `find_content_in_json` function searches for the key `"content"` and returns its value. If the content spans multiple lines, it consolidates them.
```c
char *find_content_in_json(const char *filename) {
    // Reads the file line by line, locates "content"
    // and processes escape sequences (\n, etc.).
}
```

---

### 4. **Bot Mode**
When executed with `--bot`, the program waits for user prompts, queries the API, and returns responses. Answers are temporarily stored and retrieved.
```c
if (strcmp(argv[1], "--bot") == 0) {
    while (1) {
        // Receive user prompt, call API, and return response.
    }
}
```

---

### 5. **Extraction Mode**
With `--extract`, the program validates the JSON file and extracts its content.
```c
if (strcmp(argv[1], "--extract") == 0) {
    if (has_json_extension(argv[2])) {
        if (!is_valid_json(argv[2])) {
            fprintf(stderr, "Not an accepted JSON!\n");
            return 1;
        }
        char *content = find_content_in_json(argv[2]);
        printf("%s\n", content);
    }
}
```

---

## Usage Examples

### 1. Bot Mode
```bash
./jason --bot
> What would you like to know? Hello, AI!
```

### 2. Extract JSON Content
```bash
./jason --extract example.json
```

---

## Notes
- Escape sequences (`\n`, `\t`) are converted into actual characters.
- Use `unlink()` to delete temporary files after use.

---
✅ **Efficient & Reliable JSON Processing**
