#pragma once

#include "ADTVector.h"
#include "ADTList.h"
#include "raylib.h"

// Χαρακτηριστικά αντικειμένων
#define UPDATE_STATE_FRAMES 4
#define SNAKE_SIZE 20
#define EAGLE_SIZE 20
#define EAGLE_SPEED 5
#define APPLE_SIZE 30
#define EAGLE_TURN_PROB 0.07
#define MIN_APPLES_NUM 8
#define MIN_EAGLES_NUM 8
#define MIN_DIST (0.7 * SCREEN_WIDTH)    
#define MAX_DIST (1.5 * SCREEN_WIDTH)

#define SCREEN_WIDTH 800	// Πλάτος της οθόνης
#define SCREEN_HEIGHT 800	// Υψος της οθόνης

// Οι τύποι του παιχνιδιού
typedef enum {
     UP, DOWN, LEFT, RIGHT 
} Direction;

typedef enum {
    APPLE, EAGLE
} ObjectType;

typedef struct object {
    ObjectType type;
    Vector2 position;
    double size;
    Direction direction;
}* Object;



// Πλήκτρα
typedef struct key_state {
    bool up;
    bool down;
    bool left;
    bool right;
    bool enter;
    bool p;
    bool n;
} *KeyState;

// Δηλώσεις τύπων
typedef struct state* State;

// Δομή πληροφοριών του παιχνιδιού
typedef struct state_info {
    List snake;
    Direction snake_direction;
    bool playing;
    bool paused;
    int score;
}* StateInfo;

// Βασική δομή του state
struct state {
    Vector objects;                  // Περιέχει τα αντικείμενα (μήλα, αετοί)
    struct state_info info;          // Γενικές πληροφορίες του παιχνιδιού
    int frame_counter;               // Μετρητής frames
};

// Δηλώσεις συναρτήσεων
Vector2 snake_head_pos(List snake);
State state_create();
void state_destroy(State state);
StateInfo state_info(State state);
List state_objects(State state, Vector2 top_left, Vector2 bottom_right);
void state_update(State state, KeyState keys);


