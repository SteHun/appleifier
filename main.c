#include <ti/screen.h>
#include <ti/getcsc.h>
#include <ti/real.h>
#include <sys/timers.h>
#include <stdlib.h>
#include <time.h>
#include "vid.h"

#define FPS 10

#define BLACK (char)224
#define WHITE ' '
#define BORDER '-'
#define NEWFRAME_VALUE (char)50

// black character:    224
//possible newlines:
// 214     the character :

const int screenheight = 9;
const int screenwidth = 26;

void int2str(int24_t value, char* str){
    real_t tmp_real = os_Int24ToReal(value);
    os_RealToStr(str, &tmp_real, 8, 1, 2);
}
void float2str(float value, char* str){
    real_t tmp_real = os_FloatToReal(value);
    os_RealToStr(str, &tmp_real, 8, 1, 5);
}

void wait(){
	while (!os_GetCSC()){};
	while (os_GetCSC()){};
}

void printfloat(float value){
	char string[10];
	float2str(value, string);
	os_PutStrFull(string);
	os_NewLine();
}


void update_screen(char* buffer){
	os_SetCursorPos(0, 0);
	os_PutStrFull(buffer);
}

void toggle_buffer_value(char* buffer, char x, char y){
	if (buffer[y * screenwidth + x] == BLACK)
		buffer[y * screenwidth + x] = WHITE;
	else
		buffer[y * screenwidth + x] = BLACK;
}



int main(void)
{
	
    os_ClrHome();
	os_DisableHomeTextBuffer();
	// Setup Border
	char border[screenwidth + 1];
	for (int i = 0; i < screenwidth; i++){
		border[i] = BORDER;
	}
	border[screenwidth] = '\0';
	os_SetCursorPos(9, 0);
	os_PutStrLine(border);
	
	// Setup initial buffer
	int buffersize = screenwidth * screenheight;
	char buffer[buffersize + 1];
	for (int i = 0; i < buffersize; i++){
		buffer[i] = BLACK;
	}
	
	buffer[screenwidth * screenheight] = '\0';
	update_screen(buffer);
	clock_t frame_duration = (1.0 / (float)FPS) * CLOCKS_PER_SEC;
	clock_t start_t, target_t;
	int current_frame = 1;
	unsigned int number_of_instructions = sizeof(vid)/sizeof(vid[0]);
	unsigned int current_instruction = 0;
	start_t = clock();
	target_t = start_t;
	while (true){
		if (os_GetCSC() == sk_Clear)
			return 0;
		
		// process frame
		while (vid[current_instruction] != NEWFRAME_VALUE){
			toggle_buffer_value(buffer, vid[current_instruction], vid[current_instruction + 1]);
			current_instruction += 2;
		}
		current_instruction++;
		if (current_instruction >= number_of_instructions)
			break;
		
		// draw frame if time is left over
		target_t += frame_duration;
		if (clock() < target_t){
			update_screen(buffer);
			while ((float)clock() < target_t){}
		}

		
		current_frame++;
	}
	os_SetCursorPos(9, 0);
	os_PutStrLine("END press any key");
	wait();
    return 0;
}
