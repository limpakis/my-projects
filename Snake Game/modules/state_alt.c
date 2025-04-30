//αυτη εδω ειναι η στατε.ψ
#include <stdlib.h>

#include "ADTVector.h"
#include "ADTList.h"
#include "state.h"
#include <math.h>
#include "ADTMap.h"

// Οι ολοκληρωμένες πληροφορίες της κατάστασης του παιχνιδιού.
// Ο τύπος State είναι pointer σε αυτό το struct, αλλά το ίδιο το struct
// δεν είναι ορατό στον χρήστη.

struct state {
	Map objects;			// περιέχει στοιχεία Object (μήλα, αετοί)
	struct state_info info;	// Γενικές πληροφορίες για την κατάσταση του παιχνιδιού
	int frame_counter;      // Μετρητής frames
};


int compare_position(Pointer a, Pointer b) {
    Vector2* va = (Vector2*)a;
    Vector2* vb = (Vector2*)b;

    // Μπορείς να διαλέξεις όποια σειρά θέλεις, εδώ συγκρίνουμε πρώτα x, μετά y
    if (va->x < vb->x) return -1;
    if (va->x > vb->x) return 1;
    if (va->y < vb->y) return -1;
    if (va->y > vb->y) return 1;

    return 0; // είναι ίσα
}

uint hash_vector2(Pointer a) {
    Vector2* v = (Vector2*)a;

    // Μετατρέπουμε τα float σε int για hashing
    int x_int = (int)(v->x * 1000); // Πολλαπλασιάζουμε για ακρίβεια
    int y_int = (int)(v->y * 1000);

    // Απλό hash combo για 2 ακέραιους
    return (uint)(x_int * 73856093) ^ (y_int * 19349663);
}

// Bοηθητικές συναρτήσεις /////////////////////////////////////////////////////////////////////////////////
//

static double vec_distance(Vector2 v1, Vector2 v2){
	double sum = (v1.x - v2.x)*(v1.x - v2.x) + (v1.y - v2.y)*(v1.y - v2.y);
	return sqrt(sum);
}
// Δημιουργεί και επιστρέφει ένα αντικείμενο
static Object create_object(ObjectType type, Vector2 position, double size, Direction direction) {
	Object obj = malloc(sizeof(*obj));
	obj->type = type;
	obj->position = position;
	obj->size = size;
	obj->direction = direction;
	return obj;
}

// Δημιουργεί και επιστρέφει ένα διάνυσμα
static Vector2* create_vector(Vector2 value) {
	Vector2* res = malloc(sizeof(*res));
	*res = value;
	return res;
}

// Επιστρέφει ένα διάνυσμα μετατοπισμένο κατά distance στην κατεύθυνση dir σε σχέση με το vec
static Vector2 move_in_direction(Vector2 vec, Direction dir, float distance) {
	Vector2 res = vec;
	switch (dir) {
	    case UP:    res.y -= distance; break;
	    case DOWN:  res.y += distance; break;
	    case RIGHT: res.x += distance; break;
	    case LEFT:  res.x -= distance; break;
	}
	return res;
}

// Επιστρέφει τη θέση του κεφαλιού του φιδιού
static Vector2 snake_head_pos(List snake) {
	return *(Vector2*)list_node_value(snake, list_last(snake));
}

// Επιστρέφει έναν τυχαίο πραγματικό αριθμό στο διάστημα [min,max]
static double randf(double min, double max) {
	return min + (double)rand() / RAND_MAX * (max - min);
}

// Επιστρέφει έναν τυχαίο ακέραιο αριθμό στο διάστημα [min,max]
static int randi(int min, int max) {
	return min + rand() % (max - min + 1);
}

// Δημιουργεί num αντικείμενα σε τυχαία απόσταση από το φίδι, και με τυχαία κατεύθυνση κίνησης
static void add_random_objects(State state, ObjectType type, int num) {
	Vector2 head_pos = snake_head_pos(state->info.snake);
   
	for (int i = 0; i < num; i++) {
	    // Τυχαία θέση και κατεύθυνση
	    Vector2 position = move_in_direction(head_pos, randi(0, 3), randf(MIN_DIST, MAX_DIST));
	    Direction dir = randi(0, 3);


	    int size = type == APPLE ? APPLE_SIZE : EAGLE_SIZE;
	    Object obj = create_object(type, position, size, dir);
	    map_insert(state->objects, &position, obj);
	}
}
/////////////////////////////////////////////////////////////////////////////////////////////////////


// Δημιουργεί και επιστρέφει την αρχική κατάσταση του παιχνιδιού

State state_create() {
	// Δημιουργία του state
	State state = malloc(sizeof(*state));

	// Γενικές πληροφορίες
	state->info.playing = true;			// Το παιχνίδι ξεκινάει αμέσως
	state->info.paused = false;			// Χωρίς να είναι paused
	state->info.score = 0;				// Αρχικό σκορ 0
	state->frame_counter = 0;			// Αρχικό frame 0

	// Δημιουργούμε το φίδι
	state->info.snake = list_create(free);													// αυτόματη αποδέσμευση μνήμης
	list_insert_next(state->info.snake, LIST_BOF, create_vector((Vector2){0, 0}));			// κεφάλι
	list_insert_next(state->info.snake, LIST_BOF, create_vector((Vector2){-SNAKE_SIZE, 0}));// ουρά

	state->info.snake_direction = RIGHT;	// Αρχική κίνηση προς τα δεξιά

	// Δημιουργούμε το vector των αντικειμένων, και προσθέτουμε αντικείμενα
	state->objects = map_create(compare_position, NULL, NULL);
	map_set_hash_function(state->objects, hash_vector2);
	add_random_objects(state, APPLE, MIN_APPLES_NUM);
	add_random_objects(state, EAGLE, MIN_EAGLES_NUM);

	return state;
}

// Επιστρέφει τις βασικές πληροφορίες του παιχνιδιού στην κατάσταση state

StateInfo state_info(State state) {
	return &state->info;
}

// Επιστρέφει μια λίστα με όλα τα αντικείμενα του παιχνιδιού στην κατάσταση state,
// των οποίων η θέση position βρίσκεται εντός του παραλληλογράμμου με πάνω αριστερή
// γωνία top_left και κάτω δεξιά bottom_right.

List state_objects(State state, Vector2 top_left, Vector2 bottom_right) {
	List result = list_create(NULL);
	
	for(
		MapNode node=map_first(state->objects);
		node != MAP_EOF; 
		node = map_next(state->objects, node)){
			Vector2* pos = map_node_key(state->objects, node);
			Vector2 temp = *pos;
			float x = temp.x;
			float y = temp.y;
			if(x>=top_left.x && x<=bottom_right.y && y>=bottom_right.y && y<=top_left.y){
				list_insert_next(result, LIST_BOF, map_node_value(state->objects, node));
			}
	}

	return result;
}

// Ενημερώνει την κατάσταση state του παιχνιδιού μετά την πάροδο 1 frame.
// Το keys περιέχει τα πλήκτρα τα οποία ήταν πατημένα κατά το frame αυτό.

void state_update(State state, KeyState keys) {
	if(keys->p)
		state->info.paused = !state->info.paused;
	// // Αν πατηθεί το p γίνεται παύση
	if(state->info.paused && !keys->n)
		return;
		
	// αυξανω το frame counter σε καθε κληση
	state->frame_counter++;

	//Προσοχή: λόγω της ιδιαίτερης κίνησης του φιδιού,
	//η μεταβολή της κίνησης του πρέπει να γίνεται κάθε UPDATE_STATE_FRAMES
	//(όχι σε κάθε frame). Για να γίνει αυτό πρέπει να χρησιμοποιήσετε τη μεταβλητή
	//frame_counter του state.

	if(state->frame_counter % UPDATE_STATE_FRAMES == 0){
		
		// Ανανεωνω το position του φιδιου
		List snake = state->info.snake;
		for(
			ListNode node = list_first(snake);
			node != list_last(snake);
			node = list_next(snake, node)
		){
			Vector2 *nheadpos = list_node_value(snake, node);
			*nheadpos = *(Vector2*)list_node_value(snake, list_next(snake, node));
		}

		// Αν πατηθουν κουμπια μετακινητε το φιδακι
		if(keys->right && state->info.snake_direction != LEFT)
			state->info.snake_direction=RIGHT;
		if(keys->left && state->info.snake_direction != RIGHT)
			state->info.snake_direction=LEFT;
		if(keys->up && state->info.snake_direction !=DOWN)
			state->info.snake_direction=UP;
		if(keys->down && state->info.snake_direction !=UP)
			state->info.snake_direction=DOWN;

		// παιρνω την διευθυνση του κεφαλιου
		Vector2* head_pos = list_node_value(snake, list_last(snake));

		// δεσμευω χειροκινητα μνημη για να αποθηκευσω τα στοιχεια της καινουργιας 
		Vector2* new_head = malloc(sizeof(Vector2));

		// υπολογιζω το καινουργιο κεφαλι
		*new_head = move_in_direction(*head_pos, state->info.snake_direction, SNAKE_SIZE);

		// βγαζω την ουρα απο την λιστα
        list_remove_next(snake, LIST_BOF);

        // προσθετω το καινουριου στην αρχη
        list_insert_next(snake, list_last(snake), new_head);
	}

	// Κάνω iterate και ανανεώνω τις θέσεις για όλα τα αντικείμενα
	List snake = state->info.snake;
	int apple_no = 0;
	int eagle_no = 0;
	for (MapNode node1 =map_first(state->objects);
		node1 != MAP_EOF; 
		node1 = map_next(state->objects, node1)){
		Object obj = map_node_value(state->objects, node1);
		if(obj->type == APPLE){
			double dist_from_snake = vec_distance(obj->position, snake_head_pos(snake));
			if(dist_from_snake <= MAX_DIST){
				apple_no++;
			}
		}
		if(obj->type == EAGLE){
			double dist_from_snake = vec_distance(obj->position, snake_head_pos(snake));
			if(dist_from_snake <= MAX_DIST){
				eagle_no++;
			}
		}
	}
	if(apple_no < MIN_APPLES_NUM){
		add_random_objects(state, APPLE, MIN_APPLES_NUM - apple_no);
	}
	if(eagle_no < MIN_EAGLES_NUM){
		add_random_objects(state, EAGLE, MIN_EAGLES_NUM - eagle_no);
	}

	
	//Τα updates γίνονται κάθε UPDATE_STATE_FRAMES 
	if(state->frame_counter % UPDATE_STATE_FRAMES == 0){
		// Κάνω iterate και ανανεώνω τις θέσεις για τα αντικείμενα
		for (MapNode node1 =map_first(state->objects);
		node1 != MAP_EOF; 
		node1 = map_next(state->objects, node1)){
		Object obj = map_node_value(state->objects, node1);
			if(obj->type == EAGLE){
				if ((rand() % 1000) < (int)(EAGLE_TURN_PROB * 1000)) {
					Direction new_dir = rand() % 4;  // 0 ως 3: UP, DOWN, LEFT, RIGHT
					obj->direction = new_dir;
					obj->position = move_in_direction(obj->position, obj->direction, EAGLE_SPEED);
				}
			}
		}
	}

	// Συγκρουσεις με αετους
	for(
			ListNode node = list_first(snake);
			node != list_last(snake);
			node = list_next(snake, node)
		) {
		for (MapNode node1 =map_first(state->objects);
		node1 != MAP_EOF; 
		node1 = map_next(state->objects, node1)){
			Object obj = map_node_value(state->objects, node1);
			if(obj->type==EAGLE) {
				Vector2 nobeposition = *(Vector2*)list_node_value(snake, list_last(snake));
				Vector2 eagleposition = obj->position;
				if (nobeposition.x==eagleposition.x && nobeposition.x==eagleposition.x) {
					state->info.playing=0;
				}
			}
		}
	}

	// συγκρουση με σωμα
	for(
			ListNode node = list_first(snake);
			node != list_last(snake);
			node = list_next(snake, node)
		) {
			Vector2 bodyposition = *(Vector2*)list_node_value(snake, node);
			if (snake_head_pos(snake).x == bodyposition.x && snake_head_pos(snake).y == bodyposition.y) {
				state->info.playing = 0;  // Game over αν χτυπησει στο σωμα του 
			}
		}

	// συγκρουσεις με μηλα, μεγαλωνει το φιδι και αυξανεται το σκορ
	for (MapNode node1 =map_first(state->objects);
		node1 != MAP_EOF; 
		node1 = map_next(state->objects, node1)) {
		Object obj = map_node_value(state->objects, node1);
		if (obj->type == APPLE) {
			Vector2 appleposition = obj->position;

			if (snake_head_pos(snake).x == appleposition.x && snake_head_pos(snake).y == appleposition.y) {
				// Αυξανετε το σκορ
				state->info.score++;

				// προσθεσε νεο κεφαλι
				list_insert_next(snake, list_last(snake), create_vector(move_in_direction(snake_head_pos(snake), state->info.snake_direction , SNAKE_SIZE)));
		
				// αφαιρω τα μηλα απο το map
				map_remove(state->objects, obj);
				
			}
		}
	}
}
// Καταστρέφει την κατάσταση state ελευθερώνοντας τη δεσμευμένη μνήμη.

void state_destroy(State state) {
	// Προς υλοποίηση
}
