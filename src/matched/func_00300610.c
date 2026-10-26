extern long long LibgccCommon_16(long long, long long);
extern long long LibgccCommon_17(long long, long long);
void func_00300610(char *p, char *q){ if (*(int *)(p + 0xC) != 0) return; *(long long *)(p + 0x128) = *(long long *)(p + 0x128) + LibgccCommon_17(LibgccCommon_16(*(long long *)(p + 0x130), *(long long *)q), *(long long *)(q + 8)); }
