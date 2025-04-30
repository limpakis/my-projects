#include "raylib.h"

#include "state.h"
#include <string.h>
#include "interface.h"

// Assets
Sound game_over_snd;
Music game_song;
Texture apple_img;
Texture eagle_img;


void interface_init() {
	// initializing window
	InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "My Snake Game");
	SetTargetFPS(60);
	InitAudioDevice();

	//image and sounds load
	apple_img = LoadTextureFromImage(LoadImage("assets/apple.png"));
	eagle_img = LoadTextureFromImage(LoadImage("assets/eagle.png"));
	game_over_snd = LoadSound("assets/game_over.mp3"); 
    game_song = LoadMusicStream("assets/gamesong.mp3");
    PlayMusicStream(game_song);
}

void interface_close() {
	CloseAudioDevice();
	CloseWindow();
}

void interface_draw_frame(State state) {
    BeginDrawing();
    UpdateMusicStream(game_song);
    // we clean background
	ClearBackground(DARKGRAY);

    //snake is always in the center 
    Vector2 snake_head = snake_head_pos(state->info.snake);

    float offset_x = snake_head.x - SCREEN_WIDTH / 2;
    float offset_y = snake_head.y - SCREEN_HEIGHT / 2;

    // we take all the objects that are in the monitor using our function state_objects
    Vector2 top_left = (Vector2){ offset_x, offset_y };
    Vector2 bottom_right = (Vector2){ offset_x + SCREEN_WIDTH, offset_y + SCREEN_HEIGHT };
    List visible_objects = state_objects(state, top_left, bottom_right);

    
    // we draw the snake
    for (ListNode node = list_first(state->info.snake); node != LIST_EOF; node = list_next(state->info.snake, node)) {
        Vector2* part = list_node_value(state->info.snake, node);

        float screen_x = part->x - offset_x;
        float screen_y = part->y - offset_y;

        DrawCircle(screen_x, screen_y, SNAKE_SIZE / 2, GREEN);
    }

    // we draw the objects
    for (
        ListNode node = list_first(visible_objects);
        node != LIST_EOF;
        node = list_next(visible_objects, node)
    ){
        Object obj = list_node_value(visible_objects, node);

        //Trasnfer of cordinates from arena to the monitor
        float screen_x = obj->position.x - offset_x;
        float screen_y = obj->position.y - offset_y;

        if (obj->type == APPLE)
            DrawTexture(apple_img, screen_x - apple_img.width/2, screen_y - apple_img.height/2, WHITE);
        else if (obj->type == EAGLE)
            DrawTexture(eagle_img, screen_x - eagle_img.width/2, screen_y - eagle_img.height/2, WHITE);

    }


    //if the game is pasued we are showing a message to the player
    if(state->info.paused){
        const int pressEnterFontSize = 24;

        const char* pressEnterMsg = "PRESS [P] TO CONTINUE";
 
        int screenWidth = GetScreenWidth();
        int screenHeight = GetScreenHeight();

        DrawText(
            pressEnterMsg,
            screenWidth / 2 - MeasureText(pressEnterMsg, pressEnterFontSize) / 2,
            screenHeight / 2,
            pressEnterFontSize,
            RED
        );

    }
    // Αν το παιχνίδι έχει τελειώσει, σχεδιάζομαι το μήνυμα για να ξαναρχίσει
	if (!state->info.playing) {


        const int gameOverFontSize = 60;
        const int pressEnterFontSize = 24;

        const char* gameOverMsg = "GAME OVER";
        const char* pressEnterMsg = "PRESS [ENTER] TO PLAY AGAIN!";
        
        int screenWidth = GetScreenWidth();
        int screenHeight = GetScreenHeight();

        DrawText(
            gameOverMsg,
            screenWidth / 2 - MeasureText(gameOverMsg, gameOverFontSize) / 2,
            screenHeight / 2 - 80,
            gameOverFontSize,
            RED
        );

        DrawText(
            pressEnterMsg,
            screenWidth / 2 - MeasureText(pressEnterMsg, pressEnterFontSize) / 2,
            screenHeight / 2,
            pressEnterFontSize,
            RED
        );
	}

    // Σχεδιάζουμε το σκορ και το FPS counter
	DrawText(TextFormat("SIZE %i", state->info.score), 20, 20, 40, YELLOW);
	DrawFPS(SCREEN_WIDTH - 100, 20);


    // Ηχος, αν είμαστε στο frame που συνέβη το game_over


    EndDrawing();
}