void func_00310420(char *p, int idx, int x, int y, int z){ char *q = (char *)((int)p + idx * 12 + 0x3DC); *(int *)(q + 8) = z; *(int *)q = x; *(int *)(q + 4) = y; }
