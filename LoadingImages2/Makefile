CXX = g++
CXXFLAGS = -std=c++17 `pkg-config --cflags opencv4` -Iinclude
LDFLAGS = -lopencv_core -lopencv_imgcodecs -lopencv_highgui -lopencv_imgproc -lopencv_ximgproc

TARGET = main
SRCS = src/main.cpp src/imagesManager.cpp src/windowManager.cpp

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
