/*
 * dialog_ops.c - Υλοποιηση λειτουργιων διαλογων
 * 
 * Εδω υλοποιω τη δημιουργια και συμμετοχη σε διαλογους
 */

#include "dialog_ops.h"
#include "shm_manager.h"
#include <unistd.h>
#include <stdio.h>
#include <string.h>

/*
 * Βρισκει ενα διαλογο με βαση το ID του
 */
DialogInfo* get_dialog_by_id(SharedMemoryData* memory, int dialog_id) {
    for (int i = 0; i < MAX_DIALOGS; i++) {
        if (memory->all_dialogs[i].active && 
            memory->all_dialogs[i].dialog_id == dialog_id) {
            return &memory->all_dialogs[i];
        }
    }
    return NULL;
}

/*
 * Βρισκει τη θεση ενος συμμετεχοντα στον πινακα του διαλογου
 */
int find_participant_index(DialogInfo* dialog, pid_t pid) {
    for (int i = 0; i < dialog->participant_count; i++) {
        if (dialog->participants[i].process_id == pid) {
            return i;
        }
    }
    return -1;
}

/*
 * Δημιουργει εναν νεο διαλογο
 * Επιστρεφει το ID του διαλογου η -1 σε αποτυχια
 */
int start_new_dialog(SharedMemoryData* memory) {
    lock_memory();
    
    // Ψαχνω για κενη θεση στον πινακα διαλογων
    int free_slot = -1;
    for (int i = 0; i < MAX_DIALOGS; i++) {
        if (memory->all_dialogs[i].active == 0) {
            free_slot = i;
            break;
        }
    }
    
    if (free_slot == -1) {
        unlock_memory();
        fprintf(stderr, "Δεν υπαρχουν διαθεσιμες θεσεις για νεο διαλογο!\n");
        return -1;
    }
    
    // Αρχικοποιηση του νεου διαλογου
    DialogInfo* new_dialog = &memory->all_dialogs[free_slot];
    new_dialog->active = 1;
    new_dialog->dialog_id = memory->next_available_id;
    memory->next_available_id++;
    
    // Προσθηκη του τρεχοντος process ως πρωτου συμμετεχοντα
    new_dialog->participant_count = 1;
    new_dialog->participants[0].process_id = getpid();
    new_dialog->participants[0].is_active = 1;
    
    int created_id = new_dialog->dialog_id;
    
    unlock_memory();
    
    return created_id;
}

/*
 * Συμμετοχη σε υπαρχοντα διαλογο
 * Επιστρεφει 0 σε επιτυχια, -1 σε αποτυχια
 */
int participate_in_dialog(SharedMemoryData* memory, int dialog_id) {
    lock_memory();
    
    // Βρισκω τον διαλογο
    DialogInfo* target_dialog = get_dialog_by_id(memory, dialog_id);
    
    if (target_dialog == NULL) {
        unlock_memory();
        fprintf(stderr, "Δεν βρεθηκε διαλογος με ID %d!\n", dialog_id);
        return -1;
    }
    
    // Ελεγχος αν υπαρχει χωρος για αλλον συμμετεχοντα
    if (target_dialog->participant_count >= MAX_PARTICIPANTS) {
        unlock_memory();
        fprintf(stderr, "Ο διαλογος ειναι γεματος!\n");
        return -1;
    }
    
    // Προσθηκη του τρεχοντος process
    int new_index = target_dialog->participant_count;
    target_dialog->participants[new_index].process_id = getpid();
    target_dialog->participants[new_index].is_active = 1;
    target_dialog->participant_count++;
    
    unlock_memory();
    
    return 0;
}
