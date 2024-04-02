#pragma once

#include <GLFW/glfw3.h>
#include <string>
#include <iostream>


class FrameChecker
{
private:
	float deltaTime = 0.0f;
	float lastFrame = 0.0f;
	float TotalTime = 0.0f;
public:
	FrameChecker() {}
	~FrameChecker() {}

	void Initialize()
	{
		deltaTime = 0.0f;
		lastFrame = 0.0f;
		TotalTime = 0.0f;
	}

	std::string CheckLastTimeStr()
	{
		float currentFrame = static_cast<float>(glfwGetTime());
		deltaTime = currentFrame - lastFrame;
		lastFrame = currentFrame;

		double frame = 1.0f / deltaTime;
		TotalTime += deltaTime;
		return "FPS : " + std::to_string((int)frame);
	}
	float GetDeltaTime() { return deltaTime; }
	float GetTotalTime() { return TotalTime; }

};