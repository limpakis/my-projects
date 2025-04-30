//////////////////////////////////////////////////////////////////
//
// Test για το state.h module
//
//////////////////////////////////////////////////////////////////

#include <stdlib.h>
#include <math.h>
#include "acutest.h"			// Απλή βιβλιοθήκη για unit testing
#include "ADTVector.h"

#include "state.h"


///// Βοηθητικές συναρτήσεις ////////////////////////////////////////
//
// Ελέγχει την (προσεγγιστική) ισότητα δύο double
// (λόγω λαθών το a == b δεν είναι ακριβές όταν συγκρίνουμε double).
static bool double_equal(double a, double b) {
	return fabs(a-b) < 1e-6;
}

// Ελέγχει την ισότητα δύο διανυσμάτων
static bool vec2_equal(Vector2 a, Vector2 b) {
	return double_equal(a.x, b.x) && double_equal(a.y, b.y);
}

// Επιστρέφει τη θέση του κεφαλιού του φιδιού
static Vector2 snake_head_pos(State state) {
	List snake = state_info(state)->snake;
	return *(Vector2*)list_node_value(snake, list_last(snake));
}
/////////////////////////////////////////////////////////////////////
struct state {
	Vector objects;			// περιέχει στοιχεία Object (μήλα, αετοί)
	struct state_info info;	// Γενικές πληροφορίες για την κατάσταση του παιχνιδιού
	int frame_counter;      // Μετρητής frames
};


void test_state_create() {
	State state = state_create();
	TEST_ASSERT(state != NULL);

	StateInfo info = state_info(state);
	TEST_ASSERT(info != NULL);

	TEST_ASSERT(info->playing);
	TEST_ASSERT(!info->paused);
	TEST_ASSERT(info->score == 0);

	// Αρχική θέση φιδιού
	TEST_ASSERT( vec2_equal( snake_head_pos(state), (Vector2){0,0}) );

	// ελενχος αν εχει δυο τουλαχιστον τμηματα
	List snake = info->snake;
    TEST_ASSERT(list_size(snake) >= 2);
	TEST_ASSERT(info->snake_direction == RIGHT);
	int apple_no = 0;
    int eagle_no = 0;
    for (int i = 0; i < vector_size(state->objects); i++) {
        Object obj = vector_get_at(state->objects, i);
        if (obj->type == APPLE) apple_no++;
        if (obj->type == EAGLE) eagle_no++;
    }
	//ελενχος ελαχιστων
    TEST_ASSERT(apple_no >= MIN_APPLES_NUM);
    TEST_ASSERT(eagle_no >= MIN_EAGLES_NUM);
}

void test_state_update() {
	State state = state_create();
	TEST_ASSERT(state != NULL && state_info(state) != NULL);

	// Πληροφορίες για τα πλήκτρα (αρχικά κανένα δεν είναι πατημένο)
	struct key_state keys = { false, false, false, false, false, false };
	
	// Χωρίς κανένα πλήκτρο, το φίδι μετακινείται προς τα δεξιά
	for (int i = 0; i < UPDATE_STATE_FRAMES; i++)
		state_update(state, &keys);	// χρειαζόμαστε πολλαπλά updates για να κινηθεί το φίδι

	TEST_ASSERT( vec2_equal( snake_head_pos(state), (Vector2){SNAKE_SIZE,0}) );
	TEST_ASSERT( state_info(state)->snake_direction == RIGHT );

	// Προσθέστε επιπλέον ελέγχους
}

void test_snake_cant_reverse() {
	State state = state_create();
	struct key_state keys = {0};

	for (int i = 0; i < UPDATE_STATE_FRAMES; i++) state_update(state, &keys);

	keys.left = true;
	for (int i = 0; i < UPDATE_STATE_FRAMES; i++) state_update(state, &keys);

	TEST_ASSERT(state_info(state)->snake_direction == RIGHT);
}

void test_snake_growth() {
	State state = state_create();
	struct key_state keys = {0};

	Vector2 pos = snake_head_pos(state);
	Vector2 apple_pos = { pos.x + SNAKE_SIZE, pos.y };
	Object apple = malloc(sizeof(*apple));
	apple->type = APPLE;
	apple->position = apple_pos;
	vector_insert_last(state->objects, apple);
	

	int old_size = list_size(state_info(state)->snake);

	for (int i = 0; i < UPDATE_STATE_FRAMES; i++) state_update(state, &keys);

	TEST_ASSERT(list_size(state_info(state)->snake) == old_size + 1);
}

void test_pause() {
	State state = state_create();
	state_info(state)->paused = true;

	Vector2 before = snake_head_pos(state);
	struct key_state keys = { .right = true };

	for (int i = 0; i < UPDATE_STATE_FRAMES * 2; i++) state_update(state, &keys);

	TEST_ASSERT(vec2_equal(before, snake_head_pos(state)));
}

void test_collision_with_eagle() {
	State state = state_create();
	struct key_state keys = {0};

	Vector2 eagle_pos = { SNAKE_SIZE, 0 };
	Object eagle = malloc(sizeof(*eagle));
	eagle->type = EAGLE;
	eagle->position = eagle_pos;
	vector_insert_last(state->objects, eagle);

	for (int i = 0; i < UPDATE_STATE_FRAMES; i++) state_update(state, &keys);

	TEST_ASSERT(state_info(state)->playing == false);
}


// Λίστα με όλα τα tests προς εκτέλεση
TEST_LIST = {
	{ "test_state_create", test_state_create },
	{ "test_state_update", test_state_update },
	{ "test_snake_cant_reverse", test_snake_cant_reverse },
	{ "test_snake_growth", test_snake_growth },
	{ "test_pause", test_pause },
	{ "test_collision_with_eagle", test_collision_with_eagle },
	{ NULL, NULL } // τερματίζουμε τη λίστα με NULL
};
