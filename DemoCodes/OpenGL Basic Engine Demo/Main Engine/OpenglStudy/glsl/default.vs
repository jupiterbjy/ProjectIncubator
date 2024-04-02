#version 330 core

// shader inputs
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

// mvp matrix
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// shader outputs
out vec3 FragPos;
out vec3 Normal;

void main()
{
	Normal = normal;  
	FragPos = vec3(model * vec4(position, 1.0f));
	gl_Position = projection * view * model * vec4(position, 1.0f);
}