# Makefile for Multi-Process Chat System (IPC Communication)
# Professional build configuration with organized directory structure

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pthread -g -Iinclude
LDFLAGS = -pthread

# Directories
SRCDIR = src
INCDIR = include
BUILDDIR = build
DOCSDIR = docs

# Source files
SOURCES = $(SRCDIR)/main.c $(SRCDIR)/shm_manager.c $(SRCDIR)/dialog_ops.c $(SRCDIR)/messaging.c
OBJECTS = $(SOURCES:$(SRCDIR)/%.c=$(BUILDDIR)/%.o)
EXECUTABLE = dialog_system

# Cleanup utility
CLEANUP_SRC = $(SRCDIR)/cleanup_utility.c $(SRCDIR)/shm_manager.c
CLEANUP_OBJ = $(CLEANUP_SRC:$(SRCDIR)/%.c=$(BUILDDIR)/%.o)
CLEANUP_EXE = cleanup

# Default target
all: directories $(EXECUTABLE) $(CLEANUP_EXE)

# Create build directory
directories:
	@mkdir -p $(BUILDDIR)

# Main executable
$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "✓ Built $(EXECUTABLE) successfully"

# Cleanup utility
$(CLEANUP_EXE): $(CLEANUP_OBJ)
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "✓ Built $(CLEANUP_EXE) utility successfully"

# Object file compilation
$(BUILDDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)
	rm -f $(EXECUTABLE) $(CLEANUP_EXE)
	@echo "✓ Cleaned build artifacts"

# Install (copy to system path - optional)
install: all
	sudo cp $(EXECUTABLE) /usr/local/bin/
	sudo cp $(CLEANUP_EXE) /usr/local/bin/
	@echo "✓ Installed to /usr/local/bin/"

# Uninstall
uninstall:
	sudo rm -f /usr/local/bin/$(EXECUTABLE)
	sudo rm -f /usr/local/bin/$(CLEANUP_EXE)
	@echo "✓ Uninstalled from /usr/local/bin/"

# Run the program
run: $(EXECUTABLE)
	./$(EXECUTABLE)

# Debug build with additional flags
debug: CFLAGS += -DDEBUG -O0 -ggdb3
debug: clean all

# Release build with optimizations
release: CFLAGS += -O3 -DNDEBUG
release: clean all

# Code analysis
analyze:
	cppcheck --enable=all --std=c99 $(SRCDIR)/*.c $(INCDIR)/*.h

# Memory leak check (requires Valgrind)
memcheck: $(EXECUTABLE)
	@if command -v valgrind >/dev/null 2>&1; then \
		valgrind --leak-check=full --show-leak-kinds=all ./$(EXECUTABLE); \
	else \
		echo "! Valgrind not found - install it for memory checking"; \
	fi

# Show project statistics
stats:
	@echo "=== Project Statistics ==="
	@echo "Lines of code (C files):"
	@wc -l $(SRCDIR)/*.c | tail -1
	@echo "Lines of code (Header files):"
	@wc -l $(INCDIR)/*.h | tail -1
	@echo "Total files:"
	@find $(SRCDIR) $(INCDIR) -name "*.c" -o -name "*.h" | wc -l

# Help
help:
	@echo "Available targets:"
	@echo "  all      - Build main program and cleanup utility"
	@echo "  clean    - Remove build artifacts"
	@echo "  run      - Build and run the program"
	@echo "  debug    - Build with debug flags"
	@echo "  release  - Build optimized version"
	@echo "  install  - Install to system path"
	@echo "  analyze  - Run static code analysis"
	@echo "  memcheck - Run memory leak detection"
	@echo "  stats    - Show project statistics"
	@echo "  help     - Show this help message"

.PHONY: all directories clean install uninstall run debug release analyze memcheck stats help