/*
 * dialog_ops.h - Λειτουργιες διαλογων
 * 
 * Οι συναρτησεις για τη δημιουργια και συμμετοχη σε διαλογους
 */

#ifndef DIALOG_OPS_H
#define DIALOG_OPS_H

#include "types.h"

// Δημιουργια νεου διαλογου - επιστρεφει το ID
int start_new_dialog(SharedMemoryData* memory);

// Συμμετοχη σε υπαρχοντα διαλογο - επιστρεφει 0 αν επιτυχια, -1 αν αποτυχια
int participate_in_dialog(SharedMemoryData* memory, int dialog_id);

// Βοηθητικες συναρτησεις
DialogInfo* get_dialog_by_id(SharedMemoryData* memory, int dialog_id);
int find_participant_index(DialogInfo* dialog, pid_t pid);

#endif
