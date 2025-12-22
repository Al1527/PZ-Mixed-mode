CXX = g++
CXXFLAGS = -std=c++17 `pkg-config --cflags opencv4` -Iinclude
LDFLAGS = -lopencv_core -lopencv_imgcodecs -lopencv_highgui -lopencv_imgproc

TARGET = main
SRCS = src/main.cpp src/imagesManager.cpp

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
