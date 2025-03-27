#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define MAXSIZE 256

int factorize(unsigned long long n) {
  if (n <= 1) {
    return 1;
  }

  char buffer[MAXSIZE];
  int pos = 0;
  int count = 0;

  while ((n & 1) == 0) {
    pos += sprintf(buffer + pos, "2 ");
    n >>= 1;  
    count++;
  }

  while (n % 3 == 0) {
    pos += sprintf(buffer + pos, "3 ");
    n /= 3;
    count++;
  }

  for (unsigned long long i = 5; i <= sqrt(n); i += 6) {
    if (n % i == 0) {
      pos += sprintf(buffer + pos, "%llu ", i);
      n /= i;
      count++;
    }

    if (n % (i + 2) == 0) {
      pos += sprintf(buffer + pos, "%llu ", i + 2);
      n /= (i + 2);
      count++;
    }
  }

  if (n > 1) {
    pos += sprintf(buffer + pos, "%llu ", n);
    count++;
  }

  if (count != 2) {
    printf("Usage: ./factor <semiprime>\n");
    return 1;
  }

  buffer[pos] = '\0';
  printf("Factors: %s\n", buffer);
  return 0;
}

int main(int argc, char *argv[]) {
  if (argc != 2) {
    printf("Usage: %s <number>\n", argv[0]);
    return 1;
  }

  unsigned long long num = atoll(argv[1]); 
  factorize(num);
  return 0;
}