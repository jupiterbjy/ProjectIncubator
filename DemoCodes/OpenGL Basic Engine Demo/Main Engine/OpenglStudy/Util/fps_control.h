#ifndef HIN_FPS_CONTROL_H_
#define HIN_FPS_CONTROL_H_

#include <chrono>
#include <thread>


// https://stackoverflow.com/a/48497278/10909029
// Implementation

class FpsControl
{
protected:
	bool auto_adjust = false;

	// not using unsigned to prevent conversions
	int target_fps = 60;
	int frames = 0;
	int frame_margin = 5;
	int last_avg_fps = 0;

	std::chrono::steady_clock::time_point start_t;
	std::chrono::steady_clock::time_point end_t;
	std::chrono::steady_clock::time_point last_t;
	float delta_t;

	unsigned int frame_time = 16;

	void adjust_frame_time(std::chrono::duration<float> diff) {
		// TODO: implement frame time change delay timer

		if (frame_time == 0) return;

		// if frame is lagging behind update the frame time
		auto frame_diff = target_fps - frames;

		if (frame_margin < frame_diff) {
			frame_time--;
			printf("New Frame time: %d\n", frame_time);
		}
		else if (-frame_margin > frame_diff) {
			frame_time++;
			printf("New Frame time: %d\n", frame_time);
		}
	}
public:
	FpsControl(int fps, bool enable_auto_adjust=false)
		: target_fps(fps), frame_time(1000/fps), auto_adjust(enable_auto_adjust) {
		start();
	}

	void start() {
		start_t = std::chrono::steady_clock::now();
	}

	void tick() {
		frames++;

		auto now = std::chrono::steady_clock::now();
		delta_t = std::chrono::duration<float>(now - last_t).count();
		last_t = now;

		end_t = last_t + std::chrono::milliseconds(frame_time);

		// Update framerate every second
		auto diff = last_t - start_t;

		if (diff > std::chrono::seconds(1)) {
			last_avg_fps = frames;
			frames = 0;
			start_t = last_t;

			if (!auto_adjust) return;
			adjust_frame_time(diff);
		}
	}

	void wait() {
		std::this_thread::sleep_until(end_t);
	}

	void set_fps(size_t fps) {
		target_fps = fps;
		frame_time = 1000 / fps;
	}

	void set_frame_time(size_t ft) {
		frame_time = ft;
		target_fps = 1000 / ft;
	}

	float delta_time() {
		return delta_t;
	}

	std::string curr_avg_fps_str() {
		return "FPS: " + std::to_string(last_avg_fps);
	}

};


#endif // !HIN_FPS_CONTROL_H_

