#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include "raylib.h"

#include "interface.h"
#include "state.h"

State state;
// Game loop
void update_and_draw() {
    while (!WindowShouldClose()) {


        //we create a struct for pressed keys
        KeyState keys = malloc(sizeof(*keys));
        keys->up = IsKeyDown(KEY_UP);
        keys->down = IsKeyDown(KEY_DOWN);
        keys->left = IsKeyDown(KEY_LEFT);
        keys->right = IsKeyDown(KEY_RIGHT);
        keys->enter = IsKeyDown(KEY_ENTER);
        keys->p = IsKeyDown(KEY_P);
        keys->n = IsKeyDown(KEY_N);

        if (!state_info(state)->playing && keys->enter) {
            state_destroy(state);
            state = state_create();
            free(keys);
            continue; 
        }
        // update and design-draw
        state_update(state, keys);
        interface_draw_frame(state);

        free(keys);
    }
 }
int main() {
    state = state_create();
    interface_init();

    SetTargetFPS(60); 
    start_main_loop(update_and_draw);


    interface_close();
    return 0;
}
