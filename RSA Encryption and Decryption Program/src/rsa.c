#include <stdio.h>
#include <stdlib.h>
#include <string.h>

long long totient(long long p, long long q){return (p-1)*(q-1);}

long long gcd(long long p, long long q){
    if(q == 0){
        return p;
    }else if(p == 0){
        return q;
    }else{
        return gcd(q, p%q);
    }
}

int isPrime(long long n){
    if(n < 2){
        return 0;
    }
    for(int i = 2; i*i <= n; i++){
        if(n % i == 0){
            return 0;
        }
    } 
    return 1;
}

long long coprime(long long a, long long b){
    if(gcd(a, b) == 1){
        return 1;
    }else{
        return 0;
    }
}



long long mod_exp(long long base, long long exp, long long mod){
    long long result = 1;
    while(exp > 0){
        if(exp % 2 == 1){
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

int main(int argc, char **argv){
    if(argc != 6){
        printf("Usage: ./rsa enc|dec <exp_exp> <priv_exp> <prime1> <prime2>\n");
        return 1;
    }
    if(strcmp(argv[1], "enc") != 0 && strcmp(argv[1], "dec") != 0){
        printf("First argument must be 'enc' or 'dec'\n");
        return 1;
    }

    long long e = atoll(argv[2]);
    long long d = atoll(argv[3]);
    long long p = atoll(argv[4]);
    long long q = atoll(argv[5]);
    long long m;



    if(e < 1 || d < 1 || p < 1 || q < 1){
        printf("Negative numbers are not allowed\n");
        return 1;
    }

    if(!isPrime(p) ||!isPrime(q)){
        printf("p and q must be prime\n");
        return 1;
    }

    long long phi_N = totient(p, q);
    
    if(!coprime(e, phi_N)){
        printf("e is not coprime with phi(N)\n");
        return 1;
    }

    long long N = p * q;

    if((e*d)% phi_N != 1){
        printf("e * d mod phi(N) is not 1\n");
        return 1;
    }

    if(scanf("%lld", &m) != 1){
        return 1;
    }

    if(m < 1){
        printf("Negative numbers are not allowed\n");
        return 1;
    }

    if(m >= N){
        printf("Message is larger than N\n");
        return 1;
    }

    if(strcmp(argv[1], "enc") == 0){
        long long enc_message = mod_exp(m, e, N);
        printf("%lld\n", enc_message);
    }else if(strcmp(argv[1], "dec") == 0){
        long long dec_message = mod_exp(m, d, N);
        printf("%lld\n", dec_message);
    }

    return 0; 
}