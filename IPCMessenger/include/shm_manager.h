/*
 * shm_manager.h - Διαχειριση της shared memory
 * 
 * Εδω βαζω τις συναρτησεις που χειριζονται τη δημιουργια, συνδεση
 * και καταστροφη της shared memory, καθως και το locking με semaphores.
 */

#ifndef SHM_MANAGER_H
#define SHM_MANAGER_H

#include "types.h"

// Συναρτησεις για τη διαχειριση της shared memory
SharedMemoryData* connect_to_shared_memory(int should_create);
void disconnect_from_shared_memory(SharedMemoryData* mem_ptr);
void cleanup_shared_memory(void);

// Συναρτησεις για locking (critical sections)
void lock_memory(void);
void unlock_memory(void);

#endif
