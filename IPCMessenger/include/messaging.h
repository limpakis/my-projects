/*
 * messaging.h - Αποστολη και ληψη μηνυματων
 * 
 * Οι κυριες λειτουργιες για τη μεταφορα μηνυματων μεταξυ διεργασιων
 */

#ifndef MESSAGING_H
#define MESSAGING_H

#include "types.h"

// Αποστολη μηνυματος σε διαλογο
int send_msg(SharedMemoryData* memory, int dialog_id, const char* message_text);

// Ληψη νεων μηνυματων - επιστρεφει 1 αν ελαβε TERMINATE, 0 αλλιως
int check_and_receive_messages(SharedMemoryData* memory, int dialog_id);

#endif
