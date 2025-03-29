#include "neurolib.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <unistd.h> // Include this header for unlink()
#define BUFFER_SIZE 1024


// Function to check if the filename has a ".json" extension
int has_json_extension(const char *filename) {
    const char *dot = strrchr(filename, '.'); // Find the last '.' in the filename
    return (dot && strcmp(dot, ".json") == 0); // Check if it ends with ".json"
}

// we need a function that can check if the input file has the struccture of a json file    
int is_valid_json(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Could not open file");
        return 0;
    }

    int braces = 0, brackets = 0;
    char c, prev = 0;
    int in_string = 0;

    while ((c = fgetc(file)) != EOF) {
        // Handle strings
        if (c == '"') {
            if (prev != '\\') { // Toggle string state only if not an escaped quote
                in_string = !in_string;
            }
        }

        // Ignore content inside strings
        if (in_string) {
            prev = c;
            continue;
        }

        // Count braces and brackets
        if (c == '{') braces++;
        if (c == '}') braces--;
        if (c == '[') brackets++;
        if (c == ']') brackets--;

        // Ensure counts don't go negative
        if (braces < 0 || brackets < 0) {
            fclose(file);
            return 0; // Mismatched braces/brackets
        }

        prev = c;
    }

    fclose(file);

    // Valid JSON if all braces and brackets are matched and closed
    return braces == 0 && brackets == 0 && !in_string;
}

// Function to trim leading spaces from a string
char *trim_leading_spaces(char *str) {
    while (isspace(*str)) {
        str++;
    }
    return str;
}

// Function to replace escape sequences like \n with actual characters
void process_escape_sequences(char *str) {
    char *src = str, *dest = str;
    while (*src) {
        if (*src == '\\' && *(src + 1) == 'n') {
            *dest++ = '\n'; // Replace the escape sequence \n with an actual newline character
            src += 2;      // Skip the escape sequence
        } else {
            if (*src == '\n') {
                // Replace unwanted newlines (not part of the escape sequence) with a space
                *dest++ = ' ';
            } else {
                *dest++ = *src; // Otherwise, copy the character as-is
            }
            src++;
        }
    }
    *dest = '\0'; // Null-terminate the processed string
}

// Function to find "choices[0].message.content"
char *find_content_in_json(const char *filename){
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening file");
        return NULL;
    }

    char buffer[BUFFER_SIZE];
    char content[BUFFER_SIZE * 10] = ""; // To hold multi-line content
    int in_content = 0;                 // Flag to track if inside the "content" key

    // Read the file line by line
    while (fgets(buffer, BUFFER_SIZE, file)) {
        
        trim_leading_spaces(content);
        if (in_content) {
            // If already in "content", collect lines until the closing quote
            char *end_quote = strchr(buffer, '\"');
            if (end_quote) {
                *end_quote = '\0'; // End the string at the closing quote
                strcat(content, trim_leading_spaces(buffer));
                break; // Exit when the value is fully extracted
            } else {
                strcat(content, trim_leading_spaces(buffer)); // Append trimmed line
            }
        } else {
            // Look for the "content" key
            char *key = strstr(buffer, "\"content\"");
            if (key) {
                // Find the colon after "content"
                char *colon = strchr(key, ':');
                if (colon) {
                    char *value_start = colon + 1;
                    // Skip whitespace and the opening quote
                    while (*value_start == ' ' || *value_start == '\"') {
                        value_start++;
                    }

                    // Check if the value ends on the same line
                    char *end_quote = strchr(value_start, '\"');
                    if (end_quote) {
                        *end_quote = '\0'; // Null-terminate the string
                        strcpy(content, trim_leading_spaces(value_start));
                        fclose(file);
                        process_escape_sequences(content); // Process escape sequences
                        return strdup(content);            // Return dynamically allocated string
                    } else {
                        // Otherwise, start collecting multi-line content
                        strcpy(content, trim_leading_spaces(value_start));
                        in_content = 1; // Set the flag to continue reading
                    }
                }
            }
        }
    }

    fclose(file);

    // Process escape sequences in the content
    process_escape_sequences(content);

    // Return the normalized content if found, else NULL
    return (strlen(content) > 0) ? strdup(content) : NULL;
}


int main(int argc, char **argv){
    neurosym_init();

    if(argc < 2 || argc > 3){
        fprintf(stderr, "Usage:./jason <API_KEY> [filename]\n");
        return 1;
    }

    if(argc == 2){
        if(strcmp(argv[1], "--bot") == 0){
            while(1){
                printf("> What would you like to know? ");
                char prompt[1024];
                if (fgets(prompt, sizeof(prompt), stdin)) {  // Get input from the user
                    // remove the \n character that fgets adds at the end of the input
                    prompt[strcspn(prompt, "\n")] = '\0';

                    // Get the response from the API (response function already implemented)
                    char *api_response = response(prompt);

                    if (api_response == NULL) {
                    printf("Error: No response received from the API.\n");
                    continue;
                    }

                    // Save the response to a temporary file
                    const char *temp_filename = "temp_response.json";
                    FILE *temp_file = fopen(temp_filename, "w");
                    if (temp_file == NULL) {
                        perror("Error creating temp file");
                        free(api_response);
                        continue;
                    }

                    fprintf(temp_file, "%s", api_response);
                    fclose(temp_file);

                    // Extract content from the JSON file
                    char *response_message = find_content_in_json(temp_filename);

                    if (response_message != NULL) {
                        // Print the response from the function
                        printf("%s\n", response_message);
                        free(response_message);  // Don't forget to free memory!
                    } else {
                        printf("Failed to find content in the JSON response.\n");
                    }

                    // Clean up the temporary file
                    unlink(temp_filename);  // Remove the temporary file
                    free(api_response);  // Free the memory allocated by the response function
                } else {
                    printf("Terminating\n");
                    return 1;
                }
            }
            
        }else{
            fprintf(stderr, "Usage:./jason <API_KEY> [filename]\n");
            return 1;
        }

    }else if(argc == 3){
        if(strcmp(argv[1], "--extract") == 0){ 
            if(has_json_extension(argv[2])){ // we check if the file the json extension
                if(!is_valid_json(argv[2])){ //we chevck if the arguement is a valid json file
                    fprintf(stderr, "Not an accepted JSON!\n");
                    return 1;
                }
             //we continue our program since we have checked our arguement
                // response(argv[2])
                char *content= find_content_in_json(argv[2]);
                printf("%s\n", content);
               

            } else {
                fprintf(stderr, "The file does not have a '.json' extension\n");
                return 1;
            }
        }else{
            fprintf(stderr, "Usage:./jason <API_KEY> [filename]\n");
            return 1;
        }
    }

}
