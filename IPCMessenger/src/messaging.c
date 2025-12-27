/*
 * messaging.c - Υλοποιηση αποστολης και ληψης μηνυματων
 * 
 * Το πιο σημαντικο κομματι - πως τα μηνυματα μεταφερονται
 * και πως εξασφαλιζεται οτι ολοι τα διαβαζουν μια φορα
 */

#include "messaging.h"
#include "dialog_ops.h"
#include "shm_manager.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/*
 * Στελνει ενα μηνυμα στον διαλογο
 * Επιστρεφει 0 σε επιτυχια, -1 σε αποτυχια
 */
int send_msg(SharedMemoryData* memory, int dialog_id, const char* message_text) {
    lock_memory();
    
    // Βρισκω τον διαλογο
    DialogInfo* dialog = get_dialog_by_id(memory, dialog_id);
    if (dialog == NULL) {
        unlock_memory();
        fprintf(stderr, "Αποτυχια αποστολης: δεν βρεθηκε ο διαλογος\n");
        return -1;
    }
    
    // Ψαχνω για κενη θεση στην ουρα μηνυματων
    int empty_slot = -1;
    for (int i = 0; i < MAX_MSGS_IN_QUEUE; i++) {
        if (memory->message_queue[i].occupied == 0) {
            empty_slot = i;
            break;
        }
    }
    
    if (empty_slot == -1) {
        unlock_memory();
        fprintf(stderr, "Η ουρα μηνυματων ειναι γεματη!\n");
        return -1;
    }
    
    // Δημιουργια του μηνυματος
    MessageEntry* new_msg = &memory->message_queue[empty_slot];
    new_msg->occupied = 1;
    new_msg->belongs_to_dialog = dialog_id;
    new_msg->sender_pid = getpid();
    
    strncpy(new_msg->text, message_text, MSG_TEXT_SIZE - 1);
    new_msg->text[MSG_TEXT_SIZE - 1] = '\0';
    
    // Κανενας δεν το εχει διαβασει ακομα
    for (int i = 0; i < dialog->participant_count; i++) {
        new_msg->has_been_read[i] = 0;
    }
    
    unlock_memory();
    
    return 0;
}

/*
 * Ελεγχει για νεα μηνυματα και τα διαβαζει
 * Επιστρεφει 1 αν ελαβε TERMINATE, 0 αλλιως
 */
int check_and_receive_messages(SharedMemoryData* memory, int dialog_id) {
    int got_terminate = 0;
    pid_t my_pid = getpid();
    
    lock_memory();
    
    // Βρισκω τον διαλογο μου
    DialogInfo* my_dialog = get_dialog_by_id(memory, dialog_id);
    if (my_dialog == NULL) {
        unlock_memory();
        return 0;
    }
    
    // Βρισκω τη θεση μου στον πινακα συμμετεχοντων
    int my_index = find_participant_index(my_dialog, my_pid);
    if (my_index == -1) {
        unlock_memory();
        return 0;
    }
    
    // Διατρεχω ολα τα μηνυματα
    for (int i = 0; i < MAX_MSGS_IN_QUEUE; i++) {
        MessageEntry* msg = &memory->message_queue[i];
        
        // Αν δεν υπαρχει μηνυμα, συνεχισε
        if (msg->occupied == 0) continue;
        
        // Αν δεν ειναι για τον διαλογο μου, συνεχισε
        if (msg->belongs_to_dialog != dialog_id) continue;
        
        // Αν το εχω ηδη διαβασει, συνεχισε
        if (msg->has_been_read[my_index]) continue;
        
        // Εμφανιση του μηνυματος
        printf("\n>>> [Νεο μηνυμα απο PID %d]: %s\n", msg->sender_pid, msg->text);
        fflush(stdout);
        
        // Σημειωση οτι το διαβασα
        msg->has_been_read[my_index] = 1;
        
        // Ελεγχος για TERMINATE
        if (strcmp(msg->text, "TERMINATE") == 0) {
            got_terminate = 1;
            my_dialog->participants[my_index].is_active = 0;
        }
        
        // Ελεγχος αν ολοι οι ενεργοι συμμετεχοντες το διαβασαν
        int everyone_read_it = 1;
        for (int p = 0; p < my_dialog->participant_count; p++) {
            // Αν ειναι ενεργος και δεν το διαβασε
            if (my_dialog->participants[p].is_active && !msg->has_been_read[p]) {
                everyone_read_it = 0;
                break;
            }
        }
        
        // Αν ολοι το διαβασαν, διεγραψε το
        if (everyone_read_it) {
            msg->occupied = 0;
        }
    }
    
    // Αν ελαβα TERMINATE, ελεγξε αν ο διαλογος πρεπει να κλεισει
    if (got_terminate) {
        int any_active = 0;
        for (int p = 0; p < my_dialog->participant_count; p++) {
            if (my_dialog->participants[p].is_active) {
                any_active = 1;
                break;
            }
        }
        
        // Αν δεν υπαρχουν ενεργοι συμμετεχοντες, κλεισε τον διαλογο
        if (!any_active) {
            my_dialog->active = 0;
            
            // Ελεγχος αν υπαρχουν αλλοι ενεργοι διαλογοι
            int any_dialogs_left = 0;
            for (int d = 0; d < MAX_DIALOGS; d++) {
                if (memory->all_dialogs[d].active) {
                    any_dialogs_left = 1;
                    break;
                }
            }
            
            // Αν δεν υπαρχουν αλλοι διαλογοι, καθαρισμος
            if (!any_dialogs_left) {
                unlock_memory();
                cleanup_shared_memory();
                return 1;
            }
        }
    }
    
    unlock_memory();
    
    return got_terminate;
}
