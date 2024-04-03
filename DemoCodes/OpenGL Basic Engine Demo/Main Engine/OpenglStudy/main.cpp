
//#define GLEW_STATIC
//#include <GL/glew.h>

#include "glad/glad.h"
#include <GLFW/glfw3.h>

#include <iostream>
#include <math.h>
#include <vector>

#include "Math/YAMath.h"
#include "Util/shader.h"
#include "Util/FrameChecker.h"
#include "DataTypes/mesh.h"
#include "DataTypes/cam.h"

#include "Util/fps_control.h"


// Resizes the viewport whenever resize event fires.
// Whenever resize happens, GLFW calls this.
void framebuffer_size_callback(GLFWwindow* window, int width, int height);

void Input(GLFWwindow* window);

// Default starting window size
const unsigned int mWIDTH = 800;
const unsigned int mHEIGHT = 600;


GLFWwindow* boilerplate() {
    glfwInit();

    // glBufferData(
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);

    // Enforce core-profile, where it doesn't have backward-compatable features
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Create window and assert
    GLFWwindow* window = glfwCreateWindow(mWIDTH, mHEIGHT, "OpenGL TEST", NULL, NULL);

    if (window == NULL)
    {
        std::cout << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        exit(-1);
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(0);

    // Registering function to fire on resize event
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // Create viewport - crash when added?
    // glViewport(0, 0, mWIDTH, mHEIGHT);

    // Assert GLAD works
    // Without this won't run
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        exit(-1);
    }

    //Create Z Buffer
    glEnable(GL_DEPTH_TEST);

    return window;
}


int main()
{
    GLFWwindow* window = boilerplate();

    Shader mShader("glsl/default.vs", "glsl/default.fs");

    // Frame time checker
    FrameChecker TimeChecker;

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);

    float rotation_factor = -5.0f / M_PI;
    std::vector<Mesh> meshes;

    meshes.push_back(Mesh::Cube());
    meshes.push_back(Mesh::Cube());
    meshes.push_back(Mesh::Cube());
    meshes.push_back(Mesh::Cube());

    meshes[0].color = Vec3(1.0f, 1.0f, 0.0f);
    meshes[1].color = Vec3(1.0f, 0.0f, 0.0f);
    meshes[2].color = Vec3(0.0f, 1.0f, 0.0f);
    meshes[3].color = Vec3(0.0f, 0.0f, 1.0f);

    meshes[0].translate(-1.0f, 1.0f, 0.0f);
    meshes[1].translate(1.0f, 1.0f, 0.0f);
    meshes[2].translate(-1.0f, -1.0f, 0.0f);
    meshes[3].translate(1.0f, -1.0f, 0.0f);

    std::vector<Vec3> rot_axes = {
        Vec3(1.0f, 0.0f, 0.0f).Normalize(),
        Vec3(0.0f, 1.0f, 0.0f).Normalize(),
        Vec3(1.1f, 0.0f, 1.0f).Normalize(),
        Vec3(0.0f, 0.0f, 1.0f).Normalize(),
    };

    // Custom cam implementation
    float cam_distance = 3.0f;
    Cam cam;
    cam.translate(0.0f, 0.0f, -cam_distance);

    // view trans
    // Mat4 view(1.0f);
    // view.Translate(0.0f, 0.0f, -3.0f);

    // screen space projection
    float fov = 45.0f;
    float aspect_ratio = (float)mWIDTH / (float)mHEIGHT;
    float _near = 0.1f;
    float _far = 100.0f;

    Mat4 projection = Mat4::perspective(
        fov, aspect_ratio, _near, _far
    );

    // Near-far is based on World space (0, 0, 0) so need neg/pos combination
    //projection = Mat4::orthographic(
    //  -5, 5, -5, 5, -10.0, 10.0
	//);

    // Shared memory creation
    HANDLE hMapFile;
    unsigned char* pBuf;

    size_t data_size = mWIDTH * mHEIGHT * 4;
    hMapFile = CreateFileMapping(
        INVALID_HANDLE_VALUE,
        NULL,
        PAGE_READWRITE,
        0,
        data_size,
        TEXT("MAPPING_OBJECT")
    );

    pBuf = (unsigned char*) MapViewOfFile(
		hMapFile,
		FILE_MAP_ALL_ACCESS,
		0,
		0,
		data_size
	);

    if (pBuf == NULL) {
        CloseHandle(hMapFile);
        return 1;
    }

    auto fps_ctrl = FpsControl(120);
    // TimeChecker.Initialize();
    while (!glfwWindowShouldClose(window))
    {
        fps_ctrl.tick();
        glfwSetWindowTitle(window, fps_ctrl.curr_avg_fps_str().c_str());
        // Tho events whomst happen during drawing, Thy shall be triggered!
        glfwPollEvents();

        // TODO: Create subclass of cam that has a fixed lookat target
        // TODO: Create subclass of cam that has a fixed lookat target & orbit
        // TODO: Create light class
        // TODO: fix angle reset on identical pos w/ target


        // Process input
        Input(window);

        // Clear screen to color. Both are state-clearing function, revealing
        // FSM-like internals of OpenGL
        glClearColor(0.7f, 0.9f, 0.7f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Update cam pos
        auto factor = 1.1f + sin(glfwGetTime());
        cam.position(
            sin(glfwGetTime()) * cam_distance * factor,
            0.0f,
            cos(glfwGetTime()) * cam_distance * factor
        );

        // Activate our shader; if there's multiple shader this will be meaningful
        mShader.use();

        // send shader param
        mShader.setVec3("lightPos", Vec3(0.0f, 0.0f, 0.0f));
        mShader.setMat4("projection", projection);
        mShader.setMat4("view", cam.transform);
        
        for (size_t idx = 0; idx < meshes.size(); idx++) {
            
            mShader.setVec3("objectColor", meshes[idx].color);
            meshes[idx].rotate(1.0f * fps_ctrl.delta_time(), rot_axes[idx]);
            mShader.setMat4("model", meshes[idx].transform);

            vao_bind(meshes[idx]);
            glDrawArrays(GL_TRIANGLES, 0, int(meshes[idx].size / 6));
        }

        glReadPixels(0, 0, mWIDTH, mHEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, pBuf);

        fps_ctrl.wait();

        // ...All drawing calls done, swap back(Drawing buffer) & front buffer.
        glfwSwapBuffers(window);
    }

    // Clean exit - ommitable?
    // glfwTerminate();

    // unmap mem
    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);

	return 0;
}


void Input(GLFWwindow* window)
{
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);
}

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
    glViewport(0, 0, width, height);
}


// Loop
// 
// Timer Update (dt)
// Input
// Update (Game logic / Camera update / player move)
// 
// Render
// {
//  Clear buffer
// 
//  Shader A
//  use shader A
//  transfer data to shader A
//  Draw
// 
//  
// 
// 
//  Shader B
//  use shader B
//  transfer data to shader B
//  Draw
// 
//  Flush (Swap buffer)
// }
// 
