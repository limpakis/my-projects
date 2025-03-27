# Semi-Prime Factorization in C  

## **Overview**  
This C program factorizes a given number and checks if it is a **semiprime** (a product of exactly two prime numbers). If not, it returns an error.  

## **Key Highlights**  
- **Bitwise Optimization**: Uses `n & 1` to quickly check for divisibility by 2.  
- **Efficient Trial Division**:  
  - First removes factors of **2 and 3**.  
  - Uses **6k ± 1 optimization** to check for other prime factors.  
- **Validation**: Ensures exactly **two prime factors** before printing.  

## **Usage**  
### **Compile & Run**  
```sh
gcc -o factor factor.c -lm  
./factor <semiprime> 

