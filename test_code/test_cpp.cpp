#include <string>
#include <vector>

/**
 * Sorts a vector of integers using bubble sort
 * This is not an efficient sorting algorithm for large datasets
 */
std::vector<int> bubbleSort(std::vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    return arr;
}

// A simple Point class to represent 2D coordinates
class Point {
private:
    double x;
    double y;
    
public:
    // Constructor with default values
    Point(double x_val = 0, double y_val = 0) : x(x_val), y(y_val) {}
    
    // Calculate distance from origin
    double distanceFromOrigin() const {
        return sqrt(x*x + y*y);
    }
    
    // Calculate distance between two points
    static double distance(const Point& p1, const Point& p2) {
        double dx = p1.x - p2.x;
        double dy = p1.y - p2.y;
        return sqrt(dx*dx + dy*dy);
    }
};
