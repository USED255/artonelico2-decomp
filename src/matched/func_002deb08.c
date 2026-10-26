int func_002deb08(int a, char *b){ int r = 0; unsigned char *p = (unsigned char *)b; if (p[0] == 0 && p[1] == 0 && p[2] == 1) { unsigned x = (p[3] + 0x47) & 0xFF; r = x < 2; } return r; }
