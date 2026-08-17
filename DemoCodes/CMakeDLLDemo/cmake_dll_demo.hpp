#ifndef CMAKE_DLL_DEMO_HPP_
#define CMAKE_DLL_DEMO_HPP_

#if defined(_WIN32) || defined(_WIN64) || defined(__CYGWIN__)
    // win
    #ifdef CMAKE_DLL_DEMO_EXPORTS
        #define CMAKE_DLL_DEMO_API __declspec(dllexport)
    #else
        #define CMAKE_DLL_DEMO_API __declspec(dllimport)
    #endif
#else
    // gcc / clang?
    #define CMAKE_DLL_DEMO_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {

    CMAKE_DLL_DEMO_API int add(int a, int b);

    CMAKE_DLL_DEMO_API int sub(int a, int b);

    CMAKE_DLL_DEMO_API int mul(int a, int b);

    CMAKE_DLL_DEMO_API float div(int a, int b);

}
#endif // __cplusplus

#endif // CMAKE_DLL_DEMO_HPP_
