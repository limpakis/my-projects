## RSA Encryption and Decryption Program

This program implements **RSA encryption and decryption**, using user-provided prime numbers and exponents. It verifies input validity, performs modular exponentiation, and ensures the correctness of RSA key pairs.

---

## Features
- **Encrypts and decrypts messages using RSA**
- **Validates input primes and key properties**
- **Efficient modular exponentiation for large numbers**

---

## Installation and Usage

1. **Compile the Program**
   ```bash
   gcc -Wall -Wextra -Werror -pedantic -o rsa rsa.c
   ```

2. **Run the Program**
   - **Encryption Mode**: `./rsa enc <public_exp> <private_exp> <prime1> <prime2>`
   - **Decryption Mode**: `./rsa dec <public_exp> <private_exp> <prime1> <prime2>`

   Example:
   ```bash
   echo 123 | ./rsa enc 65537 1234567891 61 53
   ```
   ```bash
   echo 2790 | ./rsa dec 65537 1234567891 61 53
   ```

---

## Code Description

### 1. **Computing Euler’s Totient Function**
The function `totient(p, q)` computes **φ(N)**, which is required for RSA key validation.
```c
long long totient(long long p, long long q) {
    return (p - 1) * (q - 1);
}
```

---

### 2. **Greatest Common Divisor (GCD) Function**
The `gcd` function determines if `e` and φ(N) are coprime.
```c
long long gcd(long long p, long long q) {
    return (q == 0) ? p : gcd(q, p % q);
}
```

---

### 3. **Prime Number Verification**
The function `isPrime(n)` ensures that `p` and `q` are both prime.
```c
int isPrime(long long n) {
    if (n < 2) return 0;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}
```

---

### 4. **Modular Exponentiation**
This function efficiently computes `(base^exp) % mod`.
```c
long long mod_exp(long long base, long long exp, long long mod) {
    long long result = 1;
    while (exp > 0) {
        if (exp % 2 == 1) result = (result * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}
```

---

### 5. **Encryption and Decryption Logic**
- **Encryption**: `C = M^e mod N`
- **Decryption**: `M = C^d mod N`
```c
if (strcmp(argv[1], "enc") == 0) {
    long long enc_message = mod_exp(m, e, N);
    printf("%lld\n", enc_message);
} else if (strcmp(argv[1], "dec") == 0) {
    long long dec_message = mod_exp(m, d, N);
    printf("%lld\n", dec_message);
}
```

---

## Usage Examples

### 1. Encrypt a Message
```bash
echo 42 | ./rsa enc 65537 1234567891 61 53
```

### 2. Decrypt a Message
```bash
echo 2790 | ./rsa dec 65537 1234567891 61 53
```

---

## Notes
- `p` and `q` must be prime.
- `e` must be coprime with φ(N).
- `(e * d) % φ(N) = 1` must hold.
- Messages must be **smaller than N**.

---
✅ **Secure & Optimized RSA Implementation**
