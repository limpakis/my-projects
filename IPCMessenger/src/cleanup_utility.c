/*
 * cleanup_utility.c - Εργαλειο για χειροκινητο καθαρισμο της shared memory
 * 
 * Χρησιμο οταν το προγραμμα κλεινει αποτομα και η shared memory μενει στο συστημα
 */

#include "shm_manager.h"
#include <stdio.h>

int main() {
    printf("Καθαρισμος shared memory...\n");
    cleanup_shared_memory();
    printf("Ολοκληρωθηκε.\n");
    return 0;
}
