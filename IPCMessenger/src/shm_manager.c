/*
 * shm_manager.c - Υλοποιηση διαχειρισης shared memory
 * 
 * Χρησιμοποιω System V shared memory (shmget, shmat κλπ) και
 * POSIX named semaphores για το synchronization.
 */

#include "shm_manager.h"
#include <sys/shm.h>
#include <semaphore.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Το key για τη shared memory - χρησιμοποιω κατι τυχαιο
#define SHARED_MEM_KEY 0x5A7B

// Ονομα για το semaphore
#define SEM_NAME "/dialog_sem_lock"

// Στατικες μεταβλητες για το module
static sem_t* semaphore = NULL;
static int shm_id = -1;

/*
 * Συνδεεται στη shared memory (η τη δημιουργει αν χρειαζεται)
 * 
 * should_create: 1 = δημιουργησε τη αν δεν υπαρχει, 0 = μονο συνδεση
 */
SharedMemoryData* connect_to_shared_memory(int should_create) {
    int flags = 0666;  // permissions
    
    if (should_create) {
        flags |= IPC_CREAT;
    }
    
    // Προσπαθεια να παρω/δημιουργησω το shared memory segment
    shm_id = shmget(SHARED_MEM_KEY, sizeof(SharedMemoryData), flags);
    if (shm_id < 0) {
        perror("Αποτυχια shmget");
        return NULL;
    }
    
    // Κανω attach τη shared memory στη διεργασια μου
    SharedMemoryData* mem_ptr = (SharedMemoryData*) shmat(shm_id, NULL, 0);
    if (mem_ptr == (void*) -1) {
        perror("Αποτυχια shmat");
        return NULL;
    }
    
    // Ανοιγμα η δημιουργια του semaphore
    if (should_create) {
        // Δημιουργω νεο semaphore με αρχικη τιμη 1 (unlocked)
        semaphore = sem_open(SEM_NAME, O_CREAT, 0666, 1);
    } else {
        // Απλα ανοιγω το υπαρχον
        semaphore = sem_open(SEM_NAME, 0);
    }
    
    if (semaphore == SEM_FAILED) {
        perror("Αποτυχια sem_open");
        shmdt(mem_ptr);
        return NULL;
    }
    
    // Αν ειναι νεα shared memory, την αρχικοποιω
    if (should_create) {
        lock_memory();
        
        // Μηδενισμος ολων των δομων
        mem_ptr->next_available_id = 1;
        
        for (int i = 0; i < MAX_DIALOGS; i++) {
            mem_ptr->all_dialogs[i].active = 0;
            mem_ptr->all_dialogs[i].participant_count = 0;
        }
        
        for (int i = 0; i < MAX_MSGS_IN_QUEUE; i++) {
            mem_ptr->message_queue[i].occupied = 0;
        }
        
        unlock_memory();
    }
    
    return mem_ptr;
}

/*
 * Αποσυνδεση απο τη shared memory
 */
void disconnect_from_shared_memory(SharedMemoryData* mem_ptr) {
    if (mem_ptr != NULL) {
        shmdt(mem_ptr);
    }
    
    if (semaphore != NULL) {
        sem_close(semaphore);
    }
}

/*
 * Καταστροφη της shared memory απο το συστημα
 * (να καλειται μονο οταν τελειωσουν ολες οι διεργασιες)
 */
void cleanup_shared_memory(void) {
    int id = shmget(SHARED_MEM_KEY, sizeof(SharedMemoryData), 0666);
    if (id >= 0) {
        shmctl(id, IPC_RMID, NULL);
    }
    
    sem_unlink(SEM_NAME);
}

/*
 * Κλειδωμα της shared memory (critical section start)
 */
void lock_memory(void) {
    if (semaphore != NULL) {
        sem_wait(semaphore);
    }
}

/*
 * Ξεκλειδωμα της shared memory (critical section end)
 */
void unlock_memory(void) {
    if (semaphore != NULL) {
        sem_post(semaphore);
    }
}
