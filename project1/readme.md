## Moving Average Calculator

This C program computes the **moving average** of the last `N` numbers from a file containing numerical data.

### Features
- Reads numerical values from a given file.
- Dynamically allocates memory to store the values.
- Computes the moving average over a specified window size (`N`).
- Default window size: **50** (can be modified via `--window N`).
- Handles errors gracefully (invalid arguments, file access issues, memory allocation failures, etc.).

### Usage
```bash
./future <filename> [--window N]
```
- `<filename>`: Path to the input file containing numerical data.
- `--window N`: (Optional) Set a custom window size `N`.

### Example
```bash
./future data.txt --window 30
```
This computes the moving average of the last **30** numbers in `data.txt`.

### Error Handling
- Displays an error if the window size is too small or too large.
- Ensures the file is readable before processing.
- Checks for memory allocation failures.

### Output
- Prints the moving average to **two decimal places**.

---
✅ **Efficient & Memory-Safe Implementation**
