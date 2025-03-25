## **JabbaMaps: City Distance Path Finder**

### **Program Overview:**  
This program reads a file containing city-to-city distances and determines a path to visit all cities using a greedy nearest-neighbor approach. It constructs a distance matrix, selects the nearest unvisited city at each step, and prints the travel order along with the total distance cost.

---

### **Usage Instructions:**  
1. **Compile the program:**  
   ```sh
   gcc -o jabbamaps jabbamaps.c
   ```
2. **Run the program with a data file:**  
   ```sh
   ./jabbamaps distances.txt
   ```

---

### **File Format Requirements:**  
- Each line should follow this format:  
  ```
  city1-city2: distance
  ```
- Example:
  ```
  NewYork-Boston: 215
  Boston-Philadelphia: 300
  Philadelphia-Washington: 140
  ```
- Cities must be uniquely named and distances should be positive integers.

---

### **Program Behavior:**  
- Reads the file and extracts city names and distances.
- Builds a distance matrix to store connections.
- Uses a **greedy nearest-neighbor algorithm** to determine a travel path.
- Prints the order of visits and total travel cost.
- Handles input errors, missing files, and invalid formats.

---

### **Limitations:**  
⚠️ **Maximum of 64 cities** due to predefined array sizes.  
⚠️ **Disconnected cities will cause an error** (i.e., no path between them).
