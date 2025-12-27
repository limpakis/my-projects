/*
 * types.h - Ορισμοι βασικων δομων για το συστημα ανταλλαγης μηνυματων
 * 
 * Εδω οριζω τις δομες που θα χρησιμοποιησω για τη διαχειριση των διαλογων
 * και των μηνυματων στη shared memory.
 */

#ifndef TYPES_H
#define TYPES_H

#include <sys/types.h>

// Μεγιστα ορια του συστηματος
#define MAX_DIALOGS 10
#define MAX_PARTICIPANTS 10
#define MAX_MSGS_IN_QUEUE 100
#define MSG_TEXT_SIZE 256

/*
 * Καθε συμμετεχων σε διαλογο εχει ενα PID και μια κατασταση
 */
typedef struct {
    pid_t process_id;
    int is_active;  // 1 = ενεργος, 0 = εχει φυγει
} Participant;

/*
 * Ενας διαλογος περιεχει:
 * - μοναδικο ID
 * - λιστα συμμετεχοντων
 * - κατασταση (ενεργος/οχι)
 */
typedef struct {
    int dialog_id;
    int active;  // 0 = κενη θεση, 1 = ενεργος διαλογος
    Participant participants[MAX_PARTICIPANTS];
    int participant_count;
} DialogInfo;

/*
 * Ενα μηνυμα στο συστημα περιεχει:
 * - το ID του διαλογου στον οποιο ανηκει
 * - τον αποστολεα (PID)
 * - το κειμενο
 * - πινακα με το ποιοι το εχουν διαβασει
 */
typedef struct {
    int belongs_to_dialog;
    pid_t sender_pid;
    char text[MSG_TEXT_SIZE];
    int occupied;  // 0 = ελευθερη θεση, 1 = υπαρχει μηνυμα
    int has_been_read[MAX_PARTICIPANTS];  // ποιος συμμετεχων το διαβασε
} MessageEntry;

/*
 * Η κυρια δομη της shared memory
 * Περιεχει ολους τους διαλογους και ολα τα μηνυματα
 */
typedef struct {
    DialogInfo all_dialogs[MAX_DIALOGS];
    MessageEntry message_queue[MAX_MSGS_IN_QUEUE];
    int next_available_id;  // για τη δημιουργια νεων dialog IDs
} SharedMemoryData;

#endif
