#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_window 50

int main (int argc, char **argv) {
    if (argc < 2 || argc > 4) {
        printf("Usage: ./future <filename> [--window N (default: 50)]\n");
        return 1;
    }

    int window_size = DEFAULT_window;

// Mathcing the variables from arguement section 
    if (argc == 4) {
       if (strcmp(argv[2], "--window") != 0) {
            fprintf(stderr, "Usage: ./future <filename> [--window N (default: 50)]\n");
            return 1;
        }
        window_size = atoi(argv[3]);
        if (window_size < 1) {
            fprintf(stderr, "window too small!\n");
            return 1;
        }
    }
// File opening 
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        fprintf(stderr, "Error opening file\n");
        return 1;
    }

    double *data = NULL;
    int capacity = 10;
    int size = 0;
    data = malloc(capacity * sizeof(double));

// Here we check  if the memory allocation failled.
    if (!data) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return 1;
    }

    double value;
    while (fscanf(file, "%lf", &value) == 1) {
        if (size == capacity) {
            capacity *= 2;
            data = realloc(data, capacity * sizeof(double));
            if (!data) {
                perror("Memory allocation failed");
                fclose(file);
                return 1;
            }
        }
        data[size] = value; 
        ++size;
    }

    fclose(file);
// Check if the window is larger than the size 
    if (window_size > size) {
        fprintf(stderr, "window too large!\n");
        free(data);
        return 1;
    }

// Calculating moving average of last terms of window
    double sum = 0;
    for (int i = size - window_size; i < size; i++) {
        sum += data[i];
    }

    double avg = sum / window_size;
    printf("%.2f\n", avg);

    free(data);
    return 0;
}
