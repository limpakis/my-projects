#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_CITIES 64          // this is the max number of cities we can handle
#define MAX_LINE_LENGTH 256    // max length of a single line from the file
#define MAX_CITY_NAME 128      // max length for a city's name

//  checks if the city is already in the list of cities
int city_exists(char cities[MAX_CITIES][MAX_LINE_LENGTH], int n, char *city) {
    for (int i = 0; i < n; i++) {
        if (strcmp(cities[i], city) == 0) { // compare city names
            return 1; // yep, it exists
        }
    }
    return 0; // nope, its not there
}

// finds the nearest city that hasn't been visited yet
int find_nearest_city(int **dist, int n, int current_city, int *visited) {
    int min_distance = INT_MAX; // start with a crazy large number
    int nearest_city = -1;      // this will store the closest city index

    for (int i = 0; i < n; i++) {
        // check if the city hasnt been visited and if it's closer
        if (!visited[i] && dist[current_city][i] > 0 && dist[current_city][i] < min_distance) {
            min_distance = dist[current_city][i];
            nearest_city = i; // found a closer city
        }
    }

    return nearest_city; // return the closest city's index
}

int main(int argc, char **argv) {
    // we check if the user actually gave us the filename
    if (argc != 2) {
        fprintf(stderr, "Usage: ./jabbamaps <filename>\n");
        return 1;
    }

    // opeing the file if it fails iut prints a fail message
    FILE *file = fopen(argv[1], "r");
    if (file == NULL) {
        fprintf(stderr, "Error opening file\n");
        return 1;
    }

    char cities[MAX_CITIES][MAX_LINE_LENGTH]; // array to store city names
    int n = 0; // counter for the number of cities
    char line[MAX_LINE_LENGTH]; // buffer to read lines from the file
    char city1[MAX_CITY_NAME], city2[MAX_CITY_NAME];
    int distance;

    // read the file line by line and process it
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = '\0'; // get rid of the annoying newline character

        // parse lines in the format "city1-city2: distance"
        if (sscanf(line, "%127[^-]-%127[^:]: %d", city1, city2, &distance) == 3) {
            // add city1 if it's not already in the list
            if (!city_exists(cities, n, city1)) {
                strcpy(cities[n], city1);
                n++;
            }
            // add city2 if it's not already in the list
            if (!city_exists(cities, n, city2)) {
                strcpy(cities[n], city2);
                n++;
            }
        } else {
            fprintf(stderr, "Invalid line format: %s\n", line); 
        }
    }

    // we create the distance matrix (n x n)
    int **dist = malloc(n * sizeof(int *));
    for (int i = 0; i < n; i++) {
        dist[i] = malloc(n * sizeof(int));
        for (int j = 0; j < n; j++) {
            dist[i][j] = 0; // initialize all distances to zero
        }
    }

    // rewind the file to process distances again
    rewind(file);
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = '\0'; // again, we remove the newline

        // paarse the line for city names and distances
        if (sscanf(line, "%127[^-]-%127[^:]: %d", city1, city2, &distance) == 3) {
            int city1_index = -1, city2_index = -1;

            // find the index of each city in the list
            for (int i = 0; i < n; i++) {
                if (strcmp(cities[i], city1) == 0) {
                    city1_index = i;
                }
                if (strcmp(cities[i], city2) == 0) {
                    city2_index = i;
                }
            }

            // fill in the distance matrix if the cities are valid
            if (city1_index != -1 && city2_index != -1) {
                dist[city1_index][city2_index] = distance;
                dist[city2_index][city1_index] = distance; // because of the symmetry
            }
        }
    }

    // we keep track of which cities we visited
    int visited[MAX_CITIES] = {0};
    int total_distance = 0;
    int current_city = 0;
    visited[current_city] = 1; // mark a cuty as visited
    printf("We will visit the cities in the following order:\n %s", cities[current_city]); // starting city 

    // Visit all cities one by one
    for (int step = 1; step < n; step++) {
        int next_city = find_nearest_city(dist, n, current_city, visited);
        if (next_city == -1) { 
            fprintf(stderr, "Error: No path found\n");
            return 1;
        }

        total_distance += dist[current_city][next_city]; // add distance
        printf(" -(%d)-> %s", dist[current_city][next_city], cities[next_city]); // print the path
        visited[next_city] = 1; // mark the city as visited
        current_city = next_city; // move to the next city
    }

    printf("\nTotal cost: %d\n", total_distance);

    // free all the dynamically allocated memory
    for (int i = 0; i < n; i++) {
        free(dist[i]);
    }
    free(dist);
    fclose(file); // close the file
    return 0; 
}
