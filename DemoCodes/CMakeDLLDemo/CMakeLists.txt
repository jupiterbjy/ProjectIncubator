cmake_minimum_required(VERSION 3.10)
project(CMakeDLLDemo VERSION 1.0.0 LANGUAGES CXX)

add_library(CMakeDLLDemo SHARED
    cmake_dll_demo.cpp
    cmake_dll_demo.hpp
)

set_property(TARGET CMakeDLLDemo PROPERTY CXX_STANDARD 20)
set_property(TARGET CMakeDLLDemo PROPERTY CXX_STANDARD_REQUIRED ON)

# macro defined for compile time, which can be used to determine whether it's
# building for DLL or else, at least that's my understanding...
# seemingly a convention for `_EXPORTS` macro for following two:
# #define *_API __declspec(dllexport)
# #define *_API __declspec(dllimport)
target_compile_definitions(CMakeDLLDemo PRIVATE CMAKE_DLL_DEMO_EXPORTS)

target_include_directories(CMakeDLLDemo
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:include>
)
