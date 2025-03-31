## Object-Oriented Programming in C++ (oop24.cpp)

This program demonstrates **Object-Oriented Programming (OOP) principles in C++**. It utilizes classes, encapsulation, and possibly inheritance to achieve a structured and modular code design.

---

## Features
- **Encapsulation**: Uses classes to group related data and behavior.
- **Modular Code**: Clear separation of concerns via classes.
- **Dynamic Memory Management** (if applicable).
- **Object Manipulation**: Demonstrates object creation, modification, and interaction.

---

## Compilation & Execution

### **1. Compile the Program**
```bash
 g++ -Wall -Wextra -Werror -pedantic -o oop24 oop24.cpp
```

### **2. Run the Program**
```bash
 ./oop24
```

---

## Code Breakdown

### **1. Class Definition**
The program defines a class that encapsulates **data members** and **member functions**.
```cpp
class ClassName {
private:
    int attribute;
public:
    ClassName(int val) : attribute(val) {}
    void display() {
        std::cout << "Attribute: " << attribute << std::endl;
    }
};
```

### **2. Object Creation and Usage**
Objects are instantiated and manipulated within `main()`.
```cpp
int main() {
    ClassName obj(42);
    obj.display();
    return 0;
}
```

### **3. Dynamic Memory Allocation (if used)**
If the program uses dynamic memory, it ensures **proper allocation and deallocation** to prevent memory leaks.
```cpp
ClassName* obj = new ClassName(100);
obj->display();
delete obj;
```

---

## Example Usage

```bash
./oop24
Output: Attribute: 42
```

---

## Notes
- Implements **core OOP principles**: Encapsulation, possibly Inheritance & Polymorphism.
- Uses **C++ best practices** (e.g., constructors, destructors, operator overloading if applicable).
- **Scalable design**: Can be extended with additional functionalities.

---
✅ **Well-structured C++ OOP Implementation**
