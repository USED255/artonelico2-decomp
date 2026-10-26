struct S { char pad[0x1FF4]; int idx; };
void *func_002f0968(struct S *p){ return (void *)((char *)p + p->idx * 0x74 + 0x1390); }
