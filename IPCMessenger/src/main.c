/*
 * main.c - Κυριο προγραμμα
 * 
 * Το interface με το χρηστη και η διαχειριση του receiver thread
 */

#include "types.h"
#include "shm_manager.h"
#include "dialog_ops.h"
#include "messaging.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

// Καθολικες μεταβλητες που χρειαζεται το thread
static SharedMemoryData* global_memory = NULL;
static int current_dialog_id = -1;
static volatile int keep_running = 1;

// Mutex για να μην μπερδευονται τα prints
pthread_mutex_t output_mutex = PTHREAD_MUTEX_INITIALIZER;

/*
 * Thread function που τρεχει στο background και ελεγχει για νεα μηνυματα
 */
void* message_receiver_thread(void* arg) {
    (void)arg;  // δεν το χρησιμοποιω
    
    while (keep_running) {
        // Ελεγχος για νεα μηνυματα
        int terminated = check_and_receive_messages(global_memory, current_dialog_id);
        
        if (terminated) {
            pthread_mutex_lock(&output_mutex);
            printf("\n[ΣΥΣΤΗΜΑ] Ο διαλογος τερματιστηκε.\n");
            fflush(stdout);
            pthread_mutex_unlock(&output_mutex);
            
            keep_running = 0;
            break;
        }
        
        // Περιμενε λιγο πριν ελεγξεις ξανα (200ms)
        usleep(200000);
    }
    
    return NULL;
}

/*
 * Βοηθητικη συναρτηση για διαβασμα αριθμου
 */
int read_number() {
    int num;
    if (scanf("%d", &num) != 1) {
        return -1;
    }
    // Καθαρισμα του buffer
    while (getchar() != '\n');
    return num;
}

/*
 * Βοηθητικη συναρτηση για διαβασμα κειμενου
 */
void read_text(char* buffer, int max_size) {
    if (fgets(buffer, max_size, stdin) == NULL) {
        buffer[0] = '\0';
        return;
    }
    // Αφαιρεση του newline
    buffer[strcspn(buffer, "\n")] = '\0';
}

/*
 * Εμφανιζει τους διαθεσιμους διαλογους
 */
void show_available_dialogs(SharedMemoryData* memory) {
    lock_memory();
    
    printf("\n=== Διαθεσιμοι Διαλογοι ===\n");
    int found_any = 0;
    
    for (int i = 0; i < MAX_DIALOGS; i++) {
        if (memory->all_dialogs[i].active) {
            printf("  - Διαλογος ID: %d (Συμμετεχοντες: %d)\n", 
                   memory->all_dialogs[i].dialog_id,
                   memory->all_dialogs[i].participant_count);
            found_any = 1;
        }
    }
    
    if (!found_any) {
        printf("  (Κανενας ενεργος διαλογος)\n");
    }
    
    unlock_memory();
}

int main() {
    int choice;
    
    printf("========================================\n");
    printf("  Συστημα Ανταλλαγης Μηνυματων         \n");
    printf("========================================\n\n");
    
    printf("Επιλεξτε δραση:\n");
    printf("  [1] Δημιουργια νεου διαλογου\n");
    printf("  [2] Συμμετοχη σε υπαρχοντα διαλογο\n");
    printf("\nΕπιλογη: ");
    fflush(stdout);
    
    choice = read_number();
    
    if (choice == 1) {
        // Δημιουργια νεου διαλογου
        
        // Πρωτα προσπαθω να συνδεθω (μηπως υπαρχει ηδη)
        global_memory = connect_to_shared_memory(0);
        
        // Αν δεν υπαρχει, τη δημιουργω
        if (global_memory == NULL) {
            global_memory = connect_to_shared_memory(1);
            if (global_memory == NULL) {
                fprintf(stderr, "Σφαλμα: Αδυναμια δημιουργιας shared memory.\n");
                return 1;
            }
        }
        
        current_dialog_id = start_new_dialog(global_memory);
        
        if (current_dialog_id < 0) {
            fprintf(stderr, "Σφαλμα: Αποτυχια δημιουργιας διαλογου.\n");
            disconnect_from_shared_memory(global_memory);
            return 1;
        }
        
        printf("\nΔημιουργηθηκε νεος διαλογος με ID: %d\n", current_dialog_id);
        
    } else if (choice == 2) {
        // Συμμετοχη σε υπαρχοντα
        
        global_memory = connect_to_shared_memory(0);
        if (global_memory == NULL) {
            fprintf(stderr, "Σφαλμα: Δεν υπαρχει ενεργο συστημα.\n");
            return 1;
        }
        
        show_available_dialogs(global_memory);
        
        printf("\nΔωστε το ID του διαλογου: ");
        fflush(stdout);
        
        current_dialog_id = read_number();
        
        if (participate_in_dialog(global_memory, current_dialog_id) < 0) {
            fprintf(stderr, "Σφαλμα: Αποτυχια συμμετοχης.\n");
            disconnect_from_shared_memory(global_memory);
            return 1;
        }
        
        printf("\nΣυμμετεχετε στον διαλογο %d\n", current_dialog_id);
        
    } else {
        printf("Μη εγκυρη επιλογη.\n");
        return 1;
    }
    
    // Ξεκινημα του receiver thread
    pthread_t receiver_tid;
    pthread_create(&receiver_tid, NULL, message_receiver_thread, NULL);
    
    printf("\n");
    printf("===========================================\n");
    printf("Eisaste ston dialogo %d\n", current_dialog_id);
    printf("===========================================\n");
    
    // Κυριος βροχος του προγραμματος
    while (keep_running) {
        printf("\n[1] Αποστολη μηνυματος\n");
        printf("[2] Αποστολη TERMINATE\n");
        printf("[3] Εξοδος\n");
        printf(">>> ");
        fflush(stdout);
        
        choice = read_number();
        
        if (choice == 1) {
            // Αποστολη κανονικου μηνυματος
            char message[MSG_TEXT_SIZE];
            
            printf("Γραψε το μηνυμα σου: ");
            fflush(stdout);
            
            read_text(message, sizeof(message));
            
            if (strlen(message) > 0) {
                if (send_msg(global_memory, current_dialog_id, message) == 0) {
                    printf("Το μηνυμα σταλθηκε.\n");
                } else {
                    printf("Αποτυχια αποστολης.\n");
                }
            }
            
        } else if (choice == 2) {
            // Αποστολη TERMINATE
            send_msg(global_memory, current_dialog_id, "TERMINATE");
            printf("\nΣταλθηκε σημα τερματισμου.\n");
            fflush(stdout);
            
            // Περιμενε λιγο για να φτασει το μηνυμα
            sleep(1);
            keep_running = 0;
            
        } else if (choice == 3) {
            // Απλη εξοδος
            printf("\nΑποχωρηση...\n");
            keep_running = 0;
        }
    }
    
    // Περιμενε το thread να τελειωσει
    pthread_join(receiver_tid, NULL);
    
    // Αποσυνδεση
    disconnect_from_shared_memory(global_memory);
    
    printf("\nΤο προγραμμα τερματιστηκε.\n");
    
    return 0;
}
