#include <string>
#include <fstream>
#include <sstream>


std::string read_file(const char* path) {
	std::ifstream file(path);
	std::stringstream ss;

	ss << file.rdbuf();
	return ss.str();
}