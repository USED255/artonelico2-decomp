char *func_002b3920(char *p, int n){ p += 0x10; if (n > 0) { do { int c = *(int *)(p + 0x10); int d = *(int *)(p + 0x14); n--; p += ((c + d + 8) << 2); } while (n != 0); } return p; }
